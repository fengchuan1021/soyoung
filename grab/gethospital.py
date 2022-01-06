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
    session=createsession()
    page=0
    now=str(datetime.datetime.now())
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
                    h=Hospital.objects.filter(HospitalID=obj['hospital_id']).first()
                    if not h:
                        h=Hospital()
                        h.HospitalID=obj['hospital_id']
                    h.CrawlTime=now
                    h.HospitalAddress=obj['address']
                    h.HospitalName=obj['name_cn']
                    h.DoctorNum=obj['doctor_cnt']
                    h.save()


                if not  ret['result']['view']['has_more']:
                    break
            else:
                break
        except Exception as e:
            print(e)
            break

if __name__=="__main__":
    grab()