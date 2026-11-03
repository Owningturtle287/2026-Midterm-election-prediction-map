#!/usr/bin/env python3
"""Collect identity-checked real portraits; never synthesize or substitute a face.

Ballotpedia source pages are retained beside each remote portrait URL. The source
is attribution, not a claim that these photographs share a permissive license.
Missing photographs remain null and must render as initials in the UI.
"""
import concurrent.futures, datetime, hashlib, html, json, pathlib, re, sys, threading, time, unicodedata, urllib.error, urllib.parse, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / '.portrait-cache'
OUT = ROOT / 'dist/assets/portraits.json'
CACHE.mkdir(exist_ok=True)
lock = threading.Lock()

def clean(name):
    return re.sub(r'^vs\.\s*', '', name).strip()

def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]','',s).strip()

def identity(name, other):
    aliases={'morgan griffith':'h morgan griffith'}
    a,b=aliases.get(norm(name),norm(name)).split(),aliases.get(norm(other),norm(other)).split()
    for row in [a,b]:
        while row and row[-1] in ('jr','sr','ii','iii','iv'):row.pop()
    return bool(a and b and a[-1]==b[-1] and a[0][0]==b[0][0])

def fetch(url, timeout=18):
    req=urllib.request.Request(url,headers={'User-Agent':'MidtermAtlas/1.0 (public candidate portrait attribution; no scraping of private data)'})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read(),r.geturl(),{k.lower():v for k,v in r.headers.items()}

DATA=json.loads((ROOT/'dist/assets/forecast.json').read_text())
people={clean(k):dict(v,name=clean(k)) for k,v in DATA['people'].items()}
contexts={k:set() for k in people}
priority={k:3 for k in people}
current={}
for office in ('house','senate','governor'):
    for race in DATA[office]:
        st=race.get('state')
        for raw in race.get('candidates',[]):
            k=clean(raw)
            contexts.setdefault(k,set()).add(st)
            priority[k]=min(priority.get(k,3),0 if office!='house' else (1 if abs(race.get('margin',99))<10 else 2))
        c=race.get('current',{})
        if c.get('name') in people:contexts.setdefault(c['name'],set()).add(st)
        if c.get('bioguide'):current[c['bioguide']]={**c,'state':st}
for c in DATA['currentSenators']:
    if c.get('name') in people:contexts.setdefault(c['name'],set()).add(c.get('state'))
    if c.get('bioguide'):current[c['bioguide']]=c

stats={'done':0,'photo':0,'missing':0,'cached':0,'official':0}
results={}

def official(person):
    u=person.get('photo') or ''
    if 'nga.org/' in u:
        matches=[r for r in DATA['governor'] if r.get('current',{}).get('name')==person['name']]
        if len(matches)==1:
            try:
                b,_,h=fetch(u,12)
                if len(b)>500 and h.get('content-type','').startswith('image/'):
                    source='https://www.nga.org/governors/'+DATA['states'][matches[0]['state']].lower().replace(' ','-')+'/'
                    return {'photo':u,'photoSource':source,'photoCredit':'Official governor portrait via National Governors Association','identitySource':source,'photoStatus':'verified-official-governor'}
            except Exception:pass
        return None
    m=re.search(r'/([A-Z]\d{6})\.jpg$',u)
    if not m or m[1] not in current:return None
    c=current[m[1]]
    if not identity(person['name'],c['name']):return None
    states=contexts.get(person['name'],set())
    if states and c.get('state') not in states:return None
    for photo_url in [u,'https://clerk.house.gov/images/members/'+m[1]+'.jpg']:
        try:
            b,final,heads=fetch(photo_url,12)
            if len(b)<500 or not heads.get('content-type','').startswith('image/'):continue
        except Exception:continue
        clerk='clerk.house.gov/' in photo_url
        return {'photo':photo_url,'photoSource':'https://clerk.house.gov/Members/ViewMemberList' if clerk else 'https://github.com/unitedstates/images','photoCredit':'Official U.S. House member portrait' if clerk else 'Official congressional portrait via unitedstates/images','identitySource':c.get('url') or 'https://clerk.house.gov/Members','photoStatus':'verified-official-house' if clerk else 'verified-official'}
    return None


def ballotpedia(name, states):
    # Person infoboxes are used exclusively; article thumbnails and opponent faces
    # are never selected. Validate heading and state before reading its widget.
    candidates=[name]
    replacements={'Michael Bouchard Jr.':'Michael Bouchard','Mike Bouchard':'Michael Bouchard','Robert J. Wittman':'Rob Wittman','Thomas H. Kean Jr.':'Tom Kean Jr.','Bernard Sanders':'Bernie Sanders','James C. Justice':'Jim Justice','Darline Graham':'Darline Graham','Katie Boyd Britt':'Katie Britt'}
    if name in replacements:candidates.insert(0,replacements[name])
    candidates += [name+' ('+DATA['states'].get(st,st)+')' for st in states if st in DATA['states']]
    for page_name in candidates:
        url='https://ballotpedia.org/'+urllib.parse.quote(page_name.replace(' ','_'),safe='()_')
        try:
            raw,final,_=fetch(url)
            if not raw:return None
            s=raw.decode('utf-8','replace')
        except (urllib.error.URLError,TimeoutError,ValueError):continue
        title=re.search(r'<title>(.*?)</title>',s,re.S|re.I)
        if not title:continue
        title=html.unescape(re.sub('<[^>]+>','',title[1])).replace(' - Ballotpedia','').strip()
        if not identity(name,title):continue
        start=re.search(r'class=["\'][^"\']*\binfobox\s+person\b[^"\']*["\']',s,re.I)
        if not start:continue
        block=s[start.start():start.start()+65000]
        # The biography or infobox must identify the expected state.
        if states and not any(re.search(r'\b'+re.escape(DATA['states'].get(st,st))+r'\b',html.unescape(re.sub('<[^>]+>',' ',block)),re.I) for st in states if st in DATA['states']):continue
        for img in re.findall(r'<img\b[^>]*>',block,re.I):
            attrs={k.lower():html.unescape(v) for k,_,v in re.findall(r'([\w:-]+)\s*=\s*(["\'])(.*?)\2',img,re.S)}
            if 'widget-img' not in attrs.get('class',''):continue
            u=attrs.get('src','')
            if not u or any(t in (u+' '+attrs.get('alt','')).lower() for t in ['submitphoto','placeholder','silhouette','no_photo','nophoto']):continue
            if u.startswith('//'):u='https:'+u
            if not u.startswith('https://'):continue
            return {'photo':u,'photoSource':final,'photoCredit':'Photograph displayed in '+title+'’s Ballotpedia person infobox; see source for attribution and rights','identitySource':final,'photoStatus':'verified-person-infobox'}
        # A matching page with no headshot is not a reason to try another person's page.
        return None
    return None

def one(item):
    name,p=item
    cachefile=CACHE/(hashlib.sha256(name.encode()).hexdigest()+'.json')
    if cachefile.exists():
        entry=json.loads(cachefile.read_text());cached=True
        if not entry.get('photo'):
            recovered=official(p)
            if recovered:
                entry={'name':name,**recovered,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
                cachefile.write_text(json.dumps(entry,ensure_ascii=False))
    else:
        cached=False
        entry=official(p)
        if not entry:entry=ballotpedia(name,contexts.get(name,set()))
        entry=entry or {'photo':None,'photoSource':None,'photoStatus':'unavailable','photoCredit':None,'identitySource':None}
        entry={'name':name,**entry,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        cachefile.write_text(json.dumps(entry,ensure_ascii=False))
    with lock:
        results[name]=entry;stats['done']+=1;stats['cached']+=cached
        stats['photo']+=bool(entry.get('photo'));stats['missing']+=not bool(entry.get('photo'));stats['official']+=entry.get('photoStatus')=='verified-official'
        if stats['done']%25==0:
            OUT.write_text(json.dumps(dict(sorted(results.items())),ensure_ascii=False,indent=2))
            print(json.dumps(stats),flush=True)
    return entry

def recover_ddhq():
    """Use named candidate metadata from the race's own DDHQ record.

    Images are checked as images, and identical placeholder bytes shared by
    unrelated candidate IDs are excluded. This never consumes race results.
    """
    aliases={'mike':'michael','bob':'robert','rob':'robert','bill':'william','dan':'daniel','joe':'joseph','dick':'richard','rick':'richard','jim':'james','matt':'matthew','chuck':'charles','tom':'thomas','deb':'debra','ben':'benjamin','cathy':'catherine','kate':'katherine','herb':'herbert','johnny':'john','chris':'christopher','clay':'clayton'}
    def nk(n):
        a=norm(n).split()
        while a and a[-1] in ('jr','sr','ii','iii','iv'):a.pop()
        return (aliases.get(a[0],a[0]),a[-1]) if a else None
    records=[]
    for office in ('house','senate','governor'):
        url='https://votes.decisiondeskhq.com/balance-of-power/2026/'+office
        path=CACHE/('dd'+office+'.html')
        if not path.exists():
            try:path.write_bytes(fetch(url,30)[0])
            except Exception:continue
        page=path.read_text()
        flight=''.join(json.loads(x)[1] for x in re.findall(r'self.__next_f.push\((\[1,.*?\])\)</script>',page,re.S))
        objs=[]
        for line in flight.splitlines():
            try:objs.append(json.loads(line.split(':',1)[1]))
            except Exception:pass
        def walk(x):
            if isinstance(x,dict):
                if x.get('stateAbb') and isinstance(x.get('results'),dict):
                    for c in x['results'].get('candidates',[]):
                        if c.get('image'):
                            records.append({'name':c.get('firstName','')+' '+c.get('lastName',''),'state':x['stateAbb'],'party':c.get('party',{}).get('abbrev'),'image':c['image'],'id':c['candId'],'source':'https://votes.decisiondeskhq.com/races/'+x['slug']+'/forecast'})
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
        walk(objs)
    targets={}
    party_map={'D':'DEM','R':'GOP','I':'IND'}
    for name,p in people.items():
        cachefile=CACHE/(hashlib.sha256(name.encode()).hexdigest()+'.json')
        if cachefile.exists() and json.loads(cachefile.read_text()).get('photo'):continue
        candidates=[r for r in records if r['state'] in contexts.get(name,set()) and nk(r['name'])==nk(name) and (p.get('party') not in party_map or r['party']==party_map[p['party']])]
        exact=[r for r in candidates if norm(r['name'])==norm(name)]
        if exact:candidates=exact
        ids={r['id'] for r in candidates}
        if len(ids)!=1:continue
        targets[name]=candidates[0]
    downloaded={}
    def get(item):
        name,r=item
        try:
            image_url='https://votes.decisiondeskhq.com/_next/image?'+urllib.parse.urlencode({'url':r['image'],'w':256,'q':75})
            b,_,h=fetch(image_url,12)
            if len(b)<700 or not h.get('content-type','').startswith('image/'):return
            from PIL import Image
            import io
            im=Image.open(io.BytesIO(b));im.verify()
            if min(im.size)<50:return
            digest=hashlib.sha256(b).hexdigest()
            with lock:
                downloaded[name]=(dict(r, servedImage=image_url),digest)
                if len(downloaded)%50==0:print(json.dumps({'ddhqImagesVerified':len(downloaded),'matched':len(targets)}),flush=True)
        except Exception:return
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(get,targets.items()))
    digests={}
    for name,(r,digest) in downloaded.items():digests.setdefault(digest,set()).add(r['id'])
    count=0
    for name,(r,digest) in downloaded.items():
        # Same image for different named candidates is usually the DDHQ default
        # silhouette. Reject it without needing to infer its visual identity.
        if len(digests[digest])>1:continue
        entry={'name':name,'photo':r.get('servedImage',r['image']),'originalPhoto':r['image'],'photoSource':r['source'],'photoCredit':'Candidate portrait supplied by Decision Desk HQ; see source for attribution and rights','identitySource':r['source'],'photoStatus':'verified-ddhq-race-record','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        (CACHE/(hashlib.sha256(name.encode()).hexdigest()+'.json')).write_text(json.dumps(entry,ensure_ascii=False));count+=1
    print(json.dumps({'ddhqMatched':len(targets),'ddhqVerified':count,'ddhqImages':len(downloaded),'duplicatePlaceholders':sum(len(v) for v in digests.values() if len(v)>1)}),flush=True)

def recover_historical():
    # Former members are not in the current membership roster; restrict the
    # match to recent service, state, full first-name alias, and surname.
    import yaml
    path=CACHE/'legislators-historical.yaml'
    if not path.exists():
        try:path.write_bytes(fetch('https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-historical.yaml',30)[0])
        except Exception:return
    former=yaml.safe_load(path.read_text())
    aliases={'mike':'michael','bob':'robert','rob':'robert','bill':'william','dan':'daniel','joe':'joseph','dick':'richard','rick':'richard','jim':'james','matt':'matthew','chuck':'charles','tom':'thomas','deb':'debra','ben':'benjamin'}
    def nk(n):
        a=norm(n).split()
        while a and a[-1] in ('jr','sr','ii','iii','iv'):a.pop()
        return (aliases.get(a[0],a[0]),a[-1]) if a else None
    recent={}
    for row in former:
        terms=[t for t in row.get('terms',[]) if str(t.get('end',''))>='1995']
        if not terms:continue
        n=row.get('name',{});full=n.get('official_full') or n.get('first','')+' '+n.get('last','')
        key=nk(full)
        for t in terms:
            if t.get('state'):recent.setdefault((key,t['state']),[]).append((row['id'].get('bioguide'),full))
    def work(item):
        name,person=item
        if name.startswith('Daniel J. Sullivan'):return
        path=CACHE/(hashlib.sha256(name.encode()).hexdigest()+'.json')
        if path.exists() and json.loads(path.read_text()).get('photo'):return
        matches=set()
        for st in contexts.get(name,set()):matches.update(recent.get((nk(name),st),[]))
        if len(matches)!=1:return
        bio,full=next(iter(matches))
        if not bio:return
        u='https://unitedstates.github.io/images/congress/225x275/'+bio+'.jpg'
        try:
            b,_,h=fetch(u,12)
            if len(b)<500 or not h.get('content-type','').startswith('image/'):return
        except Exception:return
        entry={'name':name,'photo':u,'photoSource':'https://github.com/unitedstates/images','photoCredit':'Official former congressional portrait via unitedstates/images','identitySource':'https://github.com/unitedstates/congress-legislators/blob/main/legislators-historical.yaml','photoStatus':'verified-former-member','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        path.write_text(json.dumps(entry,ensure_ascii=False))
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(work,people.items()))

if __name__=='__main__':
    recover_ddhq()
    recover_historical()
    tasks=sorted(people.items(),key=lambda kv:(priority.get(kv[0],3),kv[0]))
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for _ in pool.map(one,tasks):pass
    OUT.write_text(json.dumps(dict(sorted(results.items())),ensure_ascii=False,indent=2))
    print(json.dumps({'complete':True,**stats,'total':len(people),'output':str(OUT)}),flush=True)
