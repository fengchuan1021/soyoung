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
from grab.models import Product,Hospital
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
def grab():
    check()
    session = createsession()
    models=Hospital.objects.all()

    now = str(datetime.datetime.now())
    p=re.compile(r'id="globalData" type="text/json">(.*?)</script>',re.M)
    for model in models:
        time.sleep(5)
        try:
            url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'

            ret=session.get(url)
            model.CrawlTime=now
            if jsondata:=p.findall(ret.text):
                print(jsondata)
                data=json.loads(jsondata[0])
                model.HospitalName=data['hospital_info']['name_cn']
                model.HospitalRating=data['hospital_info']['satisfy']
                model.HospitalURating = data['hospital_info']['post_effect']
                model.HospitalTRating= data['hospital_info']['post_environment']
                model.HospitalSRating = data['hospital_info']['post_service']
                model.HospitalCity=data['hospital_info']['district2_name'] or data['hospital_info']['district_2_name'] or ''
                model.RecodeYear=data['hospital_info']['record_date']
                model.save()
        except Exception as e:
            print(e)
            break

if __name__=="__main__":
    grab()