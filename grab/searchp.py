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
                if os.path.split(p.cmdline()[1])[-1]==os.path.split(__file__)[-1]:
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

    models=Product.objects.filter(ReturnRatio=0)

    for model in models:
        if cache.get(f'searhp:{model.ProductID}'):
            continue
        else:
            cache.set(f'searhp:{model.ProductID}',1,timeout=3600*24*5)
        session=createsession()
        try:
            ret=session.get(f'https://m.soyoung.com/searchNew/product?_json=1&keyword={model.ProductName}&page=1&cityId=1').json()
            for tmp in ret['responseData']['product']:
                try:
                    ReturnRatio=0
                    if int(tmp["order_cnt"])==0:
                        continue
                    ReturnRatio = '%.2f' % abs((int(tmp["order_cnt"]) - int(tmp["sold_cnt"])) / int(tmp["order_cnt"]))
                except Exception as e:
                    print(e)
                    pass
                try:
                    Product.objects.filter(ProductID=tmp['pid']).update(ReturnRatio=ReturnRatio)
                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)
            continue
if __name__=="__main__":
    grab()