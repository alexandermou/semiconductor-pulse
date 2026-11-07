"""Collect public market data for the GitHub Pages artifact. No API keys required."""
import json, time, re, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
BASE='https://alexandermou.github.io/semiconductor-pulse/'
SYMBOLS=['SOXL','NVDA','AMD','INTC','MU','QCOM']
NOW=int(time.time()*1000)
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 SemiconductorPulse/1.0','Accept':'application/json, application/rss+xml, */*'})
    with urllib.request.urlopen(req,timeout=12) as r:return r.read().decode()
def prior(name,default):
    try:return json.loads(get(BASE+name+'?v='+str(NOW)))
    except Exception:
        try:return json.loads((Path('docs')/name).read_text())
        except Exception:return default
old=prior('data.json',{})
history=prior('history.json',{'snapshots':[]})
def quote(symbol):
    try:
        try:j=json.loads(get(f'https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d&includePrePost=true'))
        except Exception:j=json.loads(get(f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d&includePrePost=true'))
        d=j['chart']['result'][0];m=d['meta'];q=d['indicators']['quote'][0];prev=m.get('chartPreviousClose');regular=m.get('regularMarketPrice')
        pts=[{'t':t,'p':q['close'][i],'v':(q.get('volume') or [0]*len(d['timestamp']))[i] or 0} for i,t in enumerate(d.get('timestamp',[])) if isinstance(q['close'][i],(int,float))]
        sessions=[]
        for label,start,end in [('Pre-market',240,570),('Regular',570,960),('After-hours',960,1200)]:
            ps=[]
            for p in pts:
                t=datetime.fromtimestamp(p['t'],ZoneInfo('America/New_York'));minute=t.hour*60+t.minute
                if start<=minute<end:ps.append(p)
            last=ps[-1] if ps else {};price=regular if label=='Regular' else last.get('p');at=m.get('regularMarketTime') if label=='Regular' else last.get('t');base=regular if label=='After-hours' else prev
            sessions.append({'name':label,'price':price,'at':at,'change':(price/base-1)*100 if price is not None and base else None,'volume':sum(p['v'] for p in ps) if any(p['v'] for p in ps) else None})
        return {'symbol':symbol,'price':regular,'change':(regular/prev-1)*100 if regular is not None and prev else None,'at':m.get('regularMarketTime'),'volume':m.get('regularMarketVolume'),'previousClose':prev,'sessions':sessions,'points':[[p['t'],p['p']] for p in pts],'source':f'https://finance.yahoo.com/quote/{symbol}/','error':None}
    except Exception as e:
        last=next((q for q in old.get('quotes',[]) if q['symbol']==symbol),{'symbol':symbol,'sessions':[],'points':[]})
        return {**last,'error':str(e),'stale':True}
def classify(symbol,title,url,publisher,at,source_url=''):
    spec=bool(re.search(r'rumou?r|speculat|could|may |might|reportedly|sources say|in talks|prediction|price target|analyst|should you|rating|stock to buy|upside|upgrade|downgrade|buy right now|better buy|buy now|buy the dip|why i|i think|will be|worth by|next\?',title,re.I))
    official=bool(re.match(r'https?://([a-z0-9-]+\.)*(nvidia\.com|amd\.com|intel\.com|micron\.com|qualcomm\.com|direxion\.com|sec\.gov)(/|$)',source_url,re.I))
    category='Guidance' if re.search(r'guidance|outlook|forecast',title,re.I) else 'Earnings' if re.search(r'earning|quarter|results|revenue|profit',title,re.I) else 'Industry' if re.search(r'launch|announc|chip|export|tariff|fab|partnership',title,re.I) else 'Market news'
    impact='High' if re.search(r'guidance|earning|export|ban|tariff|acquisition|plunge|surge|results',title,re.I) else 'Medium' if re.search(r'launch|partnership|chip|revenue',title,re.I) else 'Low'
    affected=[s for s in SYMBOLS if s==symbol or re.search(r'\b'+s+r'\b',title,re.I)]
    if symbol!='SOXL' and 'SOXL' not in affected:affected.append('SOXL')
    why={'Guidance':'Forward expectations can reprice future revenue and margins.','Earnings':'Results can change expectations for demand, profitability and valuation.','Industry':'Supply, policy and product developments can affect semiconductor demand and competition.','Market news':'Market positioning and sentiment can influence near-term semiconductor prices.'}[category]
    return {'id':symbol+':'+url,'at':at,'symbol':symbol,'title':title,'url':url,'source':publisher,'sourceUrl':source_url,'status':'Confirmed' if official else 'Speculation' if spec else 'Reported','category':category,'impact':impact,'why':why,'affected':affected}
def news(symbol):
    try:
        try:
            root=ET.fromstring(get('https://news.google.com/rss/search?q='+urllib.parse.quote('Micron stock' if symbol=='MU' else symbol)+'&hl=en-US&gl=US&ceid=US:en'));items=root.findall('./channel/item')[:14]
            if not items:raise ValueError('No RSS headlines')
            result=[]
            for n in items:
                title=n.findtext('title','');url=n.findtext('link','');source=n.find('source');at=int(parsedate_to_datetime(n.findtext('pubDate')).timestamp()*1000)
                if symbol=='MU' and not re.search(r'Micron|\bMU stock\b|NASDAQ:MU',title,re.I):continue
                if title and url:result.append(classify(symbol,title,url,source.text if source is not None else 'Google News',at,source.get('url','') if source is not None else ''))
            return result
        except Exception:
            j=json.loads(get(f'https://query2.finance.yahoo.com/v1/finance/search?q={symbol}&quotesCount=0&newsCount=30'));patterns={'SOXL':r'SOXL|semiconductor|chip|Nvidia|AMD|Intel|Micron|Qualcomm','NVDA':r'NVDA|Nvidia','AMD':r'AMD|Advanced Micro','INTC':r'INTC|Intel','MU':r'Micron|\bMU\b','QCOM':r'QCOM|Qualcomm'}
            ns=[n for n in j.get('news',[]) if re.search(patterns[symbol],n['title'],re.I)]
            if not ns:raise ValueError('No relevant headlines returned')
            return [classify(symbol,n['title'],n['link'],n.get('publisher','Yahoo Finance'),n['providerPublishTime']*1000,urllib.parse.urlsplit(n['link']).scheme+'://'+urllib.parse.urlsplit(n['link']).netloc) for n in ns[:14]]
    except Exception as e:return {'symbol':symbol,'error':str(e)}
with ThreadPoolExecutor(max_workers=12) as pool:
    qs=list(pool.map(quote,SYMBOLS));ns=list(pool.map(news,SYMBOLS))
checked=int(time.time()*1000);cutoff=checked-30*86400000
merged={e['id']:e for e in old.get('events',[]) if e.get('title') and e.get('at',0)>=cutoff and (e.get('symbol')!='MU' or re.search(r'Micron|\bMU stock\b|NASDAQ:MU',e['title'],re.I))}
for batch in ns:
    if isinstance(batch,list):
        for e in batch:
            if e['at']>=cutoff:merged[e['id']]=e
payload={'checkedAt':checked,'quotes':qs,'events':sorted(merged.values(),key=lambda e:e['at'],reverse=True)[:500],'errors':[n for n in ns if isinstance(n,dict)],'collection':'GitHub Actions: target every 5 minutes; scheduling and deployment can be delayed. Page checks for a new snapshot every minute.'}
# Avoid falsely advancing observation time when every price retrieval failed.
if all(q.get('error') for q in qs) and old.get('checkedAt'):payload['checkedAt']=old['checkedAt'];payload['lastAttemptAt']=checked
snap={'at':payload['checkedAt'],'quotes':[{k:v for k,v in q.items() if k!='points'} for q in qs]}
h={s['at']:s for s in history.get('snapshots',[]) if s.get('at',0)>=cutoff};h[snap['at']]=snap
Path('docs').mkdir(exist_ok=True)
Path('docs/data.json').write_text(json.dumps(payload,separators=(',',':')))
Path('docs/history.json').write_text(json.dumps({'snapshots':sorted(h.values(),key=lambda s:s['at'],reverse=True)[:500]},separators=(',',':')))
print(json.dumps({'quotes':sum(not q.get('error') for q in qs),'headlines':len(payload['events']),'source_errors':payload['errors'],'checkedAt':payload['checkedAt']}))
