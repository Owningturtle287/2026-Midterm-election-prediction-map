import json,pathlib,csv,collections,math
root=pathlib.Path(__file__).resolve().parents[1];d=json.loads((root/'dist/assets/forecast.json').read_text());docs=root/'docs';docs.mkdir(exist_ok=True)
rows=[]
for key in ['governor','senate','house']:
 for r in d[key]:rows.append([key,d['states'][r['state']],r['id'],r['current']['name'],r['current']['party'],r['winner'],r['party'],'Not up'if r.get('notUp')else str(round(max(r['qD'],1-r['qD'])*100))+'%','Yes'if r['flip']else'No','Yes'if r.get('boundaryChanged')else'No',r['note'],' | '.join(d['sources'][s]['url']for s in r['sources'])])
for s in d['currentSenators']:
 if s['notUp']:rows.append(['senate',d['states'][s['state']],s['state']+' '+s['class'],s['name'],s['party'],s['name'],s['party'],'Not up','No','No','Current seat outside the election; subsequent appointments may change the person, not assumed party balance.',d['sources']['senate-roster']['url']])
cols=['Office','State','Seat','Current officeholder','Current party','Predicted winner or retained incumbent','Predicted party','Judgmental favorite probability','Party change','Boundary changed','Rationale','Sources']
with (docs/'2026-midterm-comparison.csv').open('w',newline='',encoding='utf-8-sig')as f:w=csv.writer(f);w.writerow(cols);w.writerows(sorted(rows,key=lambda r:(r[0],r[1],r[2])))
text='''# 2026 Midterm Forecast — November 3, 5:55 p.m. CST

This is an independent editorial forecast, not live results or a race call. It uses only pre-cutoff evidence. Probabilities are subjective judgments, not a backtested fitted model. The information cutoff is **2026-11-03T17:55:00-06:00**.

## National comparison

| Office | Current balance | Favorite-picks map | Change |
|---|---|---|---|
| House | 214 D, 218 R, 1 I, 2 vacancies | **236 D, 199 R** | D +22 vs current occupied membership; +21 vs 2024 election |
| Senate | 45 D, 53 R, 2 I | **51 D, 47 R, 2 I** | D +6; Democratic-aligned 53–47 |
| Governors | 24 D, 26 R | **29 D, 21 R** | D +5 |

Both sitting Senate independents caucus with Democrats. Kevin Kiley is the current House independent and caucuses with Republicans. House vacancies are FL-20 and TX-23. Counting party caucuses is different from counting formal party labels.

**Control assessment:** approximately 90% Democratic House control and 65% Democratic-aligned Senate control. These are judgmental estimates. A 50–50 Senate leaves Republicans with the vice-presidential tie-breaker.

**Favorite picks are not averages:** the Senate picks total 53 Democratic-aligned, but uncertainty-weighted expectations sit nearer 51–52. Picking every slight favorite does not make that exact national outcome likely. Broad plausible ranges are 220–252 House Democrats, 47–55 Democratic-aligned senators, and 25–31 Democratic governors; these are not calibrated confidence intervals.

## Evidence and recalibration

1. Prefer original releases to copied aggregator numbers. Siena's PA-01 release says Harvie 48–Fitzpatrick 46; a secondary reproduction overstated that lead. Original Siena and Emerson Texas results differ substantially, so Talarico is a narrow favorite rather than a safe call.
2. Exclude Wedgewood and Median Strategies from original-poll review. Wedgewood admitted fabrication; the primary FiftyPlusOne investigation documents it. AP documents Median Strategies. This is evidence about named firms, not evidence that all polls or the election are rigged.
3. Use third-party forecasts as cross-checks, not independent confirmations: models and markets often ingest the same polls. The House anchor is Call the Map's November 2 district forecast, with four winner overrides: MI-10, PA-01, IA-03 and FL-22. Other confidence estimates are revised without changing the winner. I cannot certify removal of every fake or low-quality poll from third-party models without their complete input archives. This is not a clean-room reconstruction of every polling average.
4. Preserve split-ticket behavior. Kansas favors Hamilton for Senate and Masterson for governor. Iowa favors Sand for governor and narrowly Hinson for Senate. Texas favors Talarico for Senate but Abbott for governor.
5. Allow shared polling error. A national Republican overperformance could flip several closely favored Senate seats together. Conversely, a larger anti-administration wave could expand the Democratic map. Uniform error scenarios are sensitivity tests, not newly calibrated forecasts.
6. Public indexed social posts, local newsroom reporting and early-vote analysis were checked. X/Reddit coverage was incomplete. No private communities, dark-web sources or unindexed information were accessed. Viral posts, rally size and likes were not converted into votes. Ralston's original Nevada work mildly supports Ford; party-registration ballots do not reveal candidate choices.
7. Candidate quality, incumbency, fundraising, district composition and election mechanics inform sparse-poll races. Speculative gut leans are kept close to 50%, not used to create unsupported certainty.

## Fragile calls and strongest counterarguments

- **Senate AK Peltola 57%:** original Siena 48–46, but Alaska's electorate, ranked-choice transfers and incumbent Sullivan's strength make this the weakest Democratic flip.
- **Senate TX Talarico 61%:** Siena 50–43 is much more favorable than Emerson 48–46, or 49–48 with leaners. A residual Republican turnout advantage can reverse the pick.
- **Senate KS Hamilton 65%:** Siena 49–44 and Emerson 49–45 corroborate an unusual Democratic opportunity. Republican state fundamentals and Libertarian vote consolidation remain counterweights.
- **Senate OH Brown 67%:** Brown's personal crossover appeal and Siena 49–44 support him, but Ohio's recent Republican lean makes an automatic Democratic sweep unsafe.
- **Senate ME Jackson 72%:** Siena 51–45 supports a flip; Collins' history of outperforming polls is a serious counterargument.
- **Senate IA Hinson 54%:** Siena has Turek 48–47 while earlier Emerson favored Hinson. A genuine toss-up with a small Republican lean; this is the first additional Democratic pickup in a stronger wave.
- **Senate SC Graham 66% / NE Ricketts 75%:** Siena's tied South Carolina race deserves attention, but Nebraska's 49–43 Ricketts poll argues against substituting enthusiasm narratives for measurements.
- **Governor GA Bottoms 53%, NV Ford 58%, VT Janoo 55%:** three very fragile Democratic calls. Ralston supports Ford narrowly; UNH puts Janoo ahead, but Scott's crossover history and conflicting surveys warrant caution. Vermont may require legislative selection if no candidate wins a majority.
- **Governor KS Masterson 57% / TX Abbott 63%:** incumbency or Republican fundamentals and Emerson polling support Republicans despite much closer or Democratic-favoring Siena results.
- **House MI-10 Hines 54%, PA-01 Harvie 53%, IA-03 Trone Garriott 56%, FL-22 Dandiya 52%:** the four independent winner overrides are narrow. CO-05 remains Crank 54%, MO-02 Wagner 53%, MI-04 Huizenga 55%, FL-13 Luna 70%, FL-27 Salazar 70%.

## Geography and important election rules

The House map uses official Census TIGERweb 120th congressional districts except Missouri, which uses the 119th plan because its new plan was discarded for this general election. The nine changed-map states are AL, CA, FL, LA, NC, OH, TN, TX, UT. Current members are compared by district number; a party change under new lines is not necessarily a swing in an unchanged electorate. Alaska and Hawaii use lower-left insets. DC and territories are excluded from the 435 voting House seats.

Alaska and Maine can require ranked-choice counts. Vermont's governor needs a majority or legislative selection. Louisiana's all-party House primary may lead to a December 12 runoff. **LA-05 and LA-06 are Republican party forecasts; the evidence does not justify a confident individual-winner prediction.** All named candidates are listed in the map. Subsequent appointments after sitting senators become governors can change officeholder names; party totals assume like-party replacements where applicable.

'''
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join('---'for _ in headers)+' |\n'+''.join('| '+' | '.join(str(x).replace('|','/')for x in r)+' |\n'for r in rows)+'\n'
text+='## All 50 governors: current versus forecast\n\n'
text+=table(['State','Current governor','Party','Predicted winner / retained','Party','Favorite chance'],[[r['label'],r['current']['name'],r['current']['party'],r['winner'],r['party'],'Not up'if r.get('notUp')else str(round(max(r['qD'],1-r['qD'])*100))+'%']for r in sorted(d['governor'],key=lambda r:r['label'])])
text+='## All 35 Senate contests\n\n'
text+=table(['State / race','Current senator','Party','Predicted winner','Party','Favorite chance'],[[r['label']+(' (special)'if r.get('special')else''),r['current']['name'],r['current']['party'],r['winner'],r['party'],str(round(max(r['qD'],1-r['qD'])*100))+'%']for r in sorted(d['senate'],key=lambda r:r['label'])])
text+='## All 100 current senators\n\n'
text+=table(['State','Senator','Party','2026 seat status'],[[d['states'][s['state']],s['name'],s['party'],'Not up'if s['notUp']else'Seat on ballot']for s in sorted(d['currentSenators'],key=lambda r:(d['states'][r['state']],r['name']))])
text+='## House totals by state\n\n'
stateRows=[]
for st,name in sorted(d['states'].items(),key=lambda r:r[1]):
 cur=collections.Counter(r['current']['party']for r in d['house']if r['state']==st);pred=collections.Counter(r['party']for r in d['house']if r['state']==st)
 stateRows.append([name,' / '.join(str(cur[p])+' '+p for p in ['D','R','I','V']if cur[p]),str(pred['D'])+' D / '+str(pred['R'])+' R'])
text+=table(['State','Current House delegation (V=vacant)','Forecast'],stateRows)
text+='## All 435 House seats: current versus forecast\n\n'
text+=table(['District','Current representative','Party','Predicted winner','Party','Favorite chance'],[[r['id'],r['current']['name'],r['current']['party'],r['winner'],r['party'],str(round(max(r['qD'],1-r['qD'])*100))+'%'+(' (party)'if r.get('winnerUnresolved')else'')]for r in sorted(d['house'],key=lambda r:r['id'])])
text+='## Source register\n\n'+''.join('- ['+s['title']+']('+s['url']+') — '+s['role']+'.\n'for s in d['sources'].values())
text+='\n## Portrait attribution and limitations\n\nReal official or candidate portraits are used when sourced; missing or unavailable images render labeled initials. Individual portrait sources are preserved in dist/assets/portraits.json and linked from the race panel. No candidate images are generated. External images retain their original copyrights; reuse permissions are not implied.\n'
(docs/'FORECAST.md').write_text(text)
print('exported',len(rows),'comparison rows and full report')
