const fs=require('fs'),assert=require('assert'),d3=require('../dist/assets/d3.min.js');
const root=require('path').join(__dirname,'..'),data=JSON.parse(fs.readFileSync(root+'/dist/assets/forecast.json')),geo=JSON.parse(require('zlib').gunzipSync(fs.readFileSync(root+'/dist/assets/districts.geojson.gz')));
assert.equal(data.house.length,435);assert.equal(data.senate.length,35);assert.equal(data.governor.length,50);assert.equal(data.currentSenators.length,100);assert.equal(geo.features.length,435);
const ids=new Set(data.house.map(r=>r.id));assert.equal(ids.size,435);for(const f of geo.features){assert(ids.has(f.id),'Unknown shape '+f.id);assert.equal(f.properties.sourceLayer,f.properties.state==='MO'?119:120);}
for(const group of ['house','senate','governor'])for(const r of data[group]){assert(r.current.name);assert(r.qD>=0&&r.qD<=1);if(!r.notUp){assert(r.candidates.length>=1);for(const n of r.candidates)assert(data.people[n],`Missing ${n}`);assert(r.winnerUnresolved||r.candidates.includes(r.winner),`Missing winner ${r.id}`);assert.equal(r.party,r.qD>.5?'D':'R');}}
const count=rows=>rows.reduce((a,r)=>(a[r.party]=(a[r.party]||0)+1,a),{});assert.deepEqual(count(data.house),{D:236,R:199});assert.deepEqual(count(data.senate),{D:19,R:16});assert.deepEqual(count(data.governor),{D:29,R:21});
const current=count(data.house.map(r=>r.current));assert.deepEqual(current,{R:218,D:214,V:2,I:1});assert.equal(data.currentSenators.filter(s=>s.notUp).length,65);assert.equal(data.governor.filter(r=>!r.notUp).length,36);
const project=d3.geoAlbersUsa().translate([530,325]).scale(1230),path=d3.geoPath(project);let visible=0;for(const f of geo.features){if(d3.geoArea(f)>2*Math.PI){if(f.geometry.type==='Polygon')f.geometry.coordinates.forEach(r=>r.reverse());else f.geometry.coordinates.forEach(p=>p.forEach(r=>r.reverse()));}const svg=path(f);assert(svg&&!svg.includes('NaN'),f.id+' invalid SVG');const area=path.area(f);assert(area>0&&area<200000,f.id+' suspect projected area '+area);visible++;}assert.equal(visible,435);
console.log('PASS: 435 geographic districts, Missouri119 reversion, 585 current officeholders/seats, 36 governor contests, 35 Senate contests, complete candidate references, totals236/199,53/47,29/21.');
// Audit the frozen forecast against the separate election-night snapshot.
const night=JSON.parse(fs.readFileSync(root+'/dist/assets/election-night.json'));
assert.equal(require('crypto').createHash('sha256').update(fs.readFileSync(root+'/dist/assets/forecast.json')).digest('hex'),night.meta.baselineSHA256,'Original forecast changed after scoring');
assert.equal(Object.keys(night.races).length,506);
for(const office of ['house','senate','governor']){
 const original=new Map(data[office].map(r=>[r.id,r]));
 const rows=Object.entries(night.races).filter(([,r])=>r.office===office),called=rows.filter(([,r])=>r.called);
 assert.equal(called.length,night.score[office].called);
 assert.equal(called.filter(([,r])=>r.correctParty).length,night.score[office].correct);
 const totals=office==='senate'?{D:32,R:31,I:2}:office==='governor'?count(data.governor.filter(r=>r.notUp)):{};
 for(const [id,r]of rows){const b=original.get(id);assert(b,id);assert.equal(b.party,r.original.party);assert.equal(b.winner,r.original.winner);assert(r.percentIn>=0&&r.percentIn<=100);assert(r.totalVotes>=0);assert(r.source.startsWith('https://votes.decisiondeskhq.com/races/'));assert.equal(r.expectation.changed,r.expectation.party!==b.party);assert(r.expectation.qD>=0&&r.expectation.qD<=1);totals[r.expectation.party]=(totals[r.expectation.party]||0)+1;if(r.called){const winner=r.candidates.find(c=>c.called);assert(winner,id+' missing called winner');assert.equal(r.correctParty,b.party===winner.party);assert.equal(r.expectation.party,winner.party);}else assert.equal(r.correctParty,null);}
 assert.deepEqual(totals,night.totals[office]);
}
assert.deepEqual(night.totals.house,{D:261,R:174});assert.deepEqual(night.totals.senate,{D:53,R:45,I:2});assert.deepEqual(night.totals.governor,{D:31,R:19});
assert.deepEqual(night.score.house.misses,['AL-02','IN-05','OH-15']);assert.deepEqual(night.score.senate.misses,['SC-senate']);
console.log('PASS: immutable pre-election baseline, 506 election-night contests, call-only scoring, exact source references, updated map261/174,55 aligned/45,31/19.');
