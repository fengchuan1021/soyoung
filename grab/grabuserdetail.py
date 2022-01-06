import sys
import django
import os
import pathlib
if __name__=="__main__":
    basedir=str(pathlib.Path(__file__).resolve().parent.parent)
    os.chdir(basedir)
    sys.path.append(basedir)
    os.environ['DJANGO_SETTINGS_MODULE']='soyoung.settings'
    django.setup()

from grab.createsession import createsession
from grab.models import Product,Hospital,Reviewer
import datetime,time
import re,json
import psutil
from django.conf import settings
def check():
    pidfile=os.path.split(__file__)[-1]+'.pid'
    if os.path.exists(os.path.join(settings.BASE_DIR,'run',pidfile)):
        with open(os.path.join(settings.BASE_DIR,'run',pidfile),'r') as f:
            pid=int(f.read())
            try:
                p=psutil.Process(pid)
                if os.path.split(p.cmdline()[1])[-1]==os.path.split(__file__)[-1]:
                    exit(0)
            except Exception as e:
                print(e)
    with open(os.path.join(settings.BASE_DIR,'run',pidfile),'w') as f:
        f.write(str(os.getpid()))
from bs4 import BeautifulSoup
def grab():
    check()
    models=Reviewer.objects.all()

    now = str(datetime.datetime.now())
    p=re.compile(r'id="globalData" type="text/json">(.*?)</script>',re.M)
    for model in models:
        if model.ReviewerID==0:
            continue
        time.sleep(5 if settings.DEBUG else 5)
        session = createsession()
        #try:
        if 1:
            #url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
            url=f'https://www.soyoung.com/u{model.ReviewerID}'
            print(url)

            ret=session.get(url)
            if 'https://www.soyoung.com/doctor' in ret.url:
                model.UserType='医生'
                model.save()
                continue
            if 'soyoung.com/hospital' in ret.url:
                model.UserType='机构'
                model.save()
                continue
            if ret.url.endswith('www.soyoung.com/'):
                model.UserType='匿名'
                model.save()
                continue
            text=ret.text
            soup=BeautifulSoup(text,features="html.parser")
            #print(soup.select('div'))

            model.ReviewerName=soup.select('div.titname')[0].string
            arr=soup.select('div.titother')[0].text
            arr=[i.strip() for i in arr.split('\n') if i.strip()]
            model.ReviewerGender=arr[0]
            if len(arr)>=2:
                if  arr[1]=='未知':
                    model.ReviewerAge=0
            else:
                model.ReviewerAge = 0
            model.ReviewerPosts=re.findall(r'发表（(\d+)）',text)[0]
            model.ReviewerFollowee=re.findall(r'关注（(\d+)）',text)[0]
            model.ReviewerFollwer=re.findall(r'粉丝（(\d+)）',text)[0]
            model.ReviewerExp=re.findall(r'经验值 (\d+)',text)[0]
            model.ReviewerLevel=re.findall(r'氧分 (\d+)',text)[0]
            model.save()

        #except Exception as e:
            #print(e)
            #break

if __name__=="__main__":
    grab()