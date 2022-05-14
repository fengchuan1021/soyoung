import sys
import django
import os
import pathlib,time

if __name__=="__main__":
    basedir=str(pathlib.Path(__file__).resolve().parent.parent)
    os.chdir(basedir)
    sys.path.append(basedir)
    os.environ['DJANGO_SETTINGS_MODULE']='soyoung.settings'
    django.setup()
from django_redis import get_redis_connection
from grab.createsession import createsession
from grab.models import Product,Hospital
from django.conf import settings
import datetime
import psutil
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
def grab():
    check()

    page=0
    now=str(datetime.datetime.now())
    con = get_redis_connection('default')
    while 1:
        page += 1
        session = createsession()
        url=f'https://www.soyoung.com/searchApi/product?page={page}'

        print(url)
        try:
            ret=session.get(url).json()
            print(ret)
            if 'responseData' in ret and ret['responseData']:
                for obj in ret['responseData']['list']:
                    p=Product.objects.filter(ProductID=obj['pid']).first()
                    if not p:
                        p=Product()
                        p.ProductID=obj['pid']
                    #p.PCrawlDate=now
                    p.ProductName=obj['title']
                    p.HospitalID_id=obj['hospital_id']
                    p.HospitalName=obj['hospital_name']
                    p.ProductOPrice=obj['price_origin']
                    p.ProductPrice=obj['price_online']
                    p.ProductSale=obj['sold_cnt']
                    p.HospitalRating=obj['hospital_score']
                    try:
                        p.ReturnRatio= '%.2f' % abs((int(obj["order_cnt"])-int(obj["sold_cnt"]))/int(obj["order_cnt"]))
                    except Exception as e:
                        print(e)
                        pass
                    h=Hospital.objects.filter(HospitalID=p.HospitalID_id).first()
                    if not h:
                        h=Hospital()
                        h.HospitalID=p.HospitalID_id
                        h.HospitalName=obj['hospital_name']
                        h.save()
                    p.save()
                    con.zadd('product_list',{p.ProductID:int(time.time())})
                    con.zadd('hospital_list',{h.HospitalID:int(time.time())})

            else:
                break
        except Exception as e:
            print(e)
            break

if __name__=="__main__":
    grab()