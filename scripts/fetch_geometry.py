import urllib.request,urllib.parse,json,pathlib,concurrent.futures,gzip
root=pathlib.Path(__file__).resolve().parents[1];base='https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer/'
def get(layer,where,cd):
 q=urllib.parse.urlencode({'where':where,'outFields':'GEOID,STATE,'+cd+',NAME','outSR':'4326','geometryPrecision':4,'maxAllowableOffset':'.001','returnGeometry':'true','f':'geojson'})
 url=base+str(layer)+'/query?'+q
 with urllib.request.urlopen(url,timeout=90) as r:obj=json.load(r)
 if 'features' not in obj:raise ValueError(obj)
 return obj['features']
with concurrent.futures.ThreadPoolExecutor(2) as ex:
 a=ex.submit(get,0,"STATE<>'29'",'CD120');b=ex.submit(get,4,"STATE='29'",'CD119');fs=a.result()+b.result()
fips={'01':'AL','02':'AK','04':'AZ','05':'AR','06':'CA','08':'CO','09':'CT','10':'DE','12':'FL','13':'GA','15':'HI','16':'ID','17':'IL','18':'IN','19':'IA','20':'KS','21':'KY','22':'LA','23':'ME','24':'MD','25':'MA','26':'MI','27':'MN','28':'MS','29':'MO','30':'MT','31':'NE','32':'NV','33':'NH','34':'NJ','35':'NM','36':'NY','37':'NC','38':'ND','39':'OH','40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD','47':'TN','48':'TX','49':'UT','50':'VT','51':'VA','53':'WA','54':'WV','55':'WI','56':'WY'}
out=[]
for f in fs:
 p=f['properties'];st=fips.get(p['STATE']);num=p.get('CD120') or p.get('CD119')
 if not st or num in ['ZZ','98','99']:continue
 id=st+'-'+('AL' if num=='00' else num)
 f['id']=id;f['properties']={'id':id,'state':st,'sourceLayer':119 if st=='MO' else 120};out.append(f)
assert len(out)==435,(len(out),len(fs))
(root/'dist/assets/districts.geojson.gz').write_bytes(gzip.compress(json.dumps({'type':'FeatureCollection','features':out},separators=(',',':')).encode(),compresslevel=9,mtime=0))
(root/'dist/assets/geometry-provenance.json').write_text(json.dumps({'source':base,'vintage':'2026 election,120th Congress; Missouri119th plan','retrievedFor':'2026-11-03T17:55:00-06:00','simplificationDegrees':.001,'counts':{'districts':len(out)},'note':'Census120th geometry outside Missouri,119th Missouri geometry because the2025plan was discarded for the general election.'},indent=2))
print('saved',len(out),'districts')
