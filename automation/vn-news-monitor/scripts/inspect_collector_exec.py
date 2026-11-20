import json,sys
sys.path.insert(0,'scripts')
from n8n_exec import unflatten
from collections import Counter
ex=json.load(open(sys.argv[1]))
d=unflatten(json.loads(ex['data']))
rd=d['resultData']['runData']
err=d['resultData'].get('error')
print('status',ex['status'],'error',err and err.get('message'))
for n,runs in rd.items():
    cnt=[len((r.get('data') or {}).get('main',[[]])[0] or []) if r.get('data') and 'main' in r['data'] else '-' for r in runs]
    print(f"{n:28s} runs={len(runs)} items={cnt} status={[r.get('executionStatus') for r in runs][:3]} {[(r.get('error') or {}).get('message','')[:120] for r in runs if r.get('error')]}")
def items(n,run=0,out=0):
    try: return [i['json'] for i in rd[n][run]['data']['main'][out]]
    except Exception: return []
saved=[]
for r in range(len(rd.get('Luu tin',[]))): saved+=items('Luu tin',r)
print('saved by classified_by', Counter(i.get('classified_by') for i in saved))
print('importance', Counter(i.get('importance') for i in saved if str(i.get('classified_by','')).startswith('ai:')))
print('run_log', items('Ghi run_log'))
print('ai_usage', items('Ghi ai_usage'))
