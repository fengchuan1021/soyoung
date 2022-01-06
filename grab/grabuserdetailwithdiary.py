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
        page=0
        while 1:
            page+=1
            time.sleep(5 if settings.DEBUG else 5)
            session = createsession()
            #try:
            if 1:
                #url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
                url=f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={model.ReviewerID}&type=1'
                print(url)

                ret=session.get(url).json()
                if 'data' in ret and 'redirect' in ret['data']:
                        break


            #except Exception as e:
                #print(e)
                #break

if __name__=="__main__":
    grab()