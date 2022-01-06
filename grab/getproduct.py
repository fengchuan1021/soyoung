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
import datetime
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
        page += 1
        url=f'https://www.soyoung.com/searchApi/product?page={page}'
        print(url)
        try:
            ret=session.get(url).json()
            print(ret)
            if ret['responseData']:
                for obj in ret['responseData']['list']:
                    p=Product()


                    p.PCrawlDate=now
                    p.ProductID=obj['pid']
                    p.ProductName=obj['title']
                    p.HospitalID_id=obj['hospital_id']
                    p.ProductOPrice=obj['price_origin']
                    p.ProductPrice=obj['price_online']
                    p.ProductSale=obj['sold_cnt']

                    h=Hospital.objects.filter(HospitalID=p.HospitalID_id).first()
                    if not h:
                        h=Hospital()
                        h.HospitalID=p.HospitalID_id
                        h.HospitalName=obj['hospital_name']
                        h.save()
                    p.save()

            else:
                break
        except Exception as e:
            print(e)
            break

if __name__=="__main__":
    grab()