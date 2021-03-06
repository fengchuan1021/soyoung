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
from grab.models import Product,Hospital,Doctor
import datetime,time
from django.conf import settings
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

    page=0
    now=str(datetime.datetime.now())
    while 1:
        #time.sleep(1)
        session = createsession()
        page += 1
        url=f'https://m.soyoung.com/calendardoctor/getdoc?index={page}'#&calendar_type=3&menu1_id=undefined&select_id=undefined
        print(url)
        try:
        #if 1:
            ret=session.get(url).json()
            print(ret)
            if 'responseData' in ret  and 'dpdoctor' in ret['responseData']:
                for obj in ret['responseData']['dpdoctor']:
                    h=Doctor.objects.filter(DoctorID=obj['doctor_id']).first()
                    if not h:
                        h=Doctor()
                        h.DoctorID=obj['doctor_id']
                    h.DCrawlDate=now
                    h.DoctorID=obj['doctor_id']
                    h.DoctorName=obj['name_cn']
                    if obj['hospital_id']:
                        hospital=Hospital.objects.filter(HospitalID=obj['hospital_id']).first()
                        if not hospital:
                            hospital=Hospital()
                            hospital.HospitalID=obj['hospital_id']
                            hospital.HospitalName=obj['hospital_name']
                            hospital.save()
                    h.HospitalID_id=obj['hospital_id']
                    h.HospitalName=obj['hospital_name']
                    h.save()


                if not  ret['has_more']:
                    break
            else:
                break
        except Exception as e:
            print(e)
            break

if __name__=="__main__":
    grab()