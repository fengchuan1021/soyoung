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
import psutil
from django.conf import settings
from django.core.cache import cache
def check():
    pidfile=os.path.split(__file__)[-1]+'.pid'
    if os.path.exists(os.path.join(settings.BASE_DIR,'run',pidfile)):
        with open(os.path.join(settings.BASE_DIR,'run',pidfile),'r') as f:
            pid=int(f.read())
            try:
                p=psutil.Process(pid)

                exit(0)
            except Exception as e:
                print(e)
    with open(os.path.join(settings.BASE_DIR,'run',pidfile),'w') as f:
        f.write(str(os.getpid()))
from django_redis import get_redis_connection
def grab():
    check()

    page=0
    now=str(datetime.datetime.now())

    models=Hospital.objects.filter(ServiceNum=0)

    for model in models:
        if cache.get(f'searhh:{model.HospitalID}'):
            continue
        else:
            cache.set(f'searhh:{model.HospitalID}',1,timeout=3600*24*5)
        session=createsession()
        try:
            ret=session.get(f'https://m.soyoung.com/searchNew/hospital?_json=1&keyword={model.HospitalName}&page=1&cityId=1').json()
            print('ret:',ret)
            for tmp in ret['responseData']['hospital_list']:
                try:
                    Hospital.objects.filter(HospitalID=tmp['hospital_id']).update(ServiceNum=tmp['hospital_pid_cnt'],ReviewNum=tmp['calendar_group_cnt'],
                                                                                  HospitalRating=tmp['satisfy'],HospitalType=tmp['type']
                                                                                  )
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)
            continue
if __name__=="__main__":
    grab()