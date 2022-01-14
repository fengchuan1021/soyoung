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
from django_redis import get_redis_connection
def grab():
    check()
    session=createsession()
    page=0
    now=str(datetime.datetime.now())
    con = get_redis_connection('default')
    while 1:
        time.sleep(1)
        page += 1
        url=f'https://m.soyoung.com/hospitalsearch?ajax=1&index={page}'#&calendar_type=3&menu1_id=undefined&select_id=undefined
        print(url)
        try:
            ret=session.get(url).json()
            print(ret)
            if 'result' in ret and 'view' in ret['result'] and 'dphospital' in ret['result']['view']:
                for obj in ret['result']['view']['dphospital']:
                    model=Hospital.objects.filter(HospitalID=obj['hospital_id']).first()
                    if not model:
                        model=Hospital()
                        model.HospitalID=obj['hospital_id']

                    model.ServiceNum= obj['hospital_pid_cnt']
                    model.ReviewNum=obj['calendar_group_cnt']
                    model.HospitalName=obj['name_cn']
                    model.HospitalType=obj['type']
                    model.CrawlTime=now
                    model.save()
                    con.sadd('hospital_list',obj['hospital_id'])



                if not  ret['result']['view']['has_more']:
                    break
            else:
                break
        except Exception as e:
            print(e)
            break

if __name__=="__main__":
    grab()