"""Оновлює kfk_rozklad.json: список викладачів коледжу і розклад кожного з
https://kfk.sumdu.edu.ua/studentu/rozklad-dlia-vykladacha-koledzhu/ (форма POST teacher=...).
Запуск: python3 update_rozklad.py  → потім перепублікувати артефакт з files={"kfk_rozklad.json": ...}.
Застосунок не може ходити на сайт сам (немає CORS), тому бере цей знімок."""
import re,html,json,time,datetime,subprocess
URL='https://kfk.sumdu.edu.ua/studentu/rozklad-dlia-vykladacha-koledzhu/'
def get(*args): return subprocess.run(['curl','-s','-A','Mozilla/5.0',*args,URL],capture_output=True,timeout=60).stdout.decode('utf-8','ignore')
form=get()
sel=re.search(r'<select[^>]*id="teacher"[^>]*>(.*?)</select>',form,re.S).group(1)
names=[n for n in dict.fromkeys(html.unescape(v).strip() for v in re.findall(r'<option value="([^"]*)"',sel)) if n]
out={}
for n in names:
    t=get('--data-urlencode','teacher='+n,'--data-urlencode','submit=OK')
    rows=[]
    for x in re.findall(r'<table.*?</table>',t,re.S)[:1]:
        for r in re.findall(r'<tr.*?</tr>',x,re.S):
            cs=[html.unescape(re.sub(r'<[^>]+>','',c)).strip() for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>',r,re.S)]
            if len(cs)>=6 and cs[0]!='Предмет': rows.append(cs[:6])
    out[n]=rows; time.sleep(0.8)
import pathlib
p=pathlib.Path(__file__).with_name('kfk_rozklad.json')
p.write_text(json.dumps({'source':URL,'fetched':datetime.date.today().isoformat(),'teachers':out},ensure_ascii=False),'utf-8')
print(len(out),'викладачів,',sum(len(v) for v in out.values()),'рядків →',p)
