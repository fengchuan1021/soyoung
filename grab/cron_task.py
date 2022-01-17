import sys
import django
import os
import pathlib
import js2py
from django_redis import get_redis_connection
if __name__ == "__main__":
    basedir = str(pathlib.Path(__file__).resolve().parent.parent)
    os.chdir(basedir)
    sys.path.append(basedir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'soyoung.settings'
    django.setup()

from grab.createsession import createsession
from grab.models import Product, Hospital, Reviewer,Diary,Doctor
import datetime, time
import re, json
import psutil
from django.conf import settings
from django.core.cache import cache
from dotmap import DotMap
from bs4 import BeautifulSoup
import sys
def beforecheck(name):
    pidfile = f'{name}.pid'
    if os.path.exists(os.path.join(settings.BASE_DIR, 'run', pidfile)):
        with open(os.path.join(settings.BASE_DIR, 'run', pidfile), 'r') as f:
            pid = int(f.read())
            try:
                p = psutil.Process(pid)
                if os.path.split(p.cmdline()[1])[-1]==os.path.split(__file__)[-1]:
                    exit(0)
            except Exception as e:
                print(e)
    with open(os.path.join(settings.BASE_DIR, 'run', pidfile), 'w') as f:
        f.write(str(os.getpid()))

from grab.checkuser import checkproduct,checkproductdiary,checkdiary,checkdiaryreply,checkhospital,checkdoctor,checkuser,checkdoctordiary,checkdoctorxiangmu

def task_checkdiary():
    con = get_redis_connection('default')
    beforecheck('task_checkdiary')
    while 1:
        arr=con.zrange('diary_list',0,100)
        for did in arr:
            checkdiary(did.decode())
        #time.sleep(0.01)
        con.zrem('diary_list', *arr)
        print('aftersleep')


def task_checkuser():
    con = get_redis_connection('default')
    beforecheck(sys._getframe().f_code.co_name)
    while 1:
        arr=con.zrange('user_list',0,100)
        for did in arr:
            tmp=checkuser(did.decode())
        #time.sleep(0.01)
        con.zrem('usesr_list',*arr)
        print('aftersleep')

def task_checkproduct():
    con = get_redis_connection('default')
    beforecheck(sys._getframe().f_code.co_name)
    while 1:
        arr=con.zrange('product_list',0,100)
        for did in arr:
            tmp=checkproduct(did.decode())
        #time.sleep(0.01)
        con.zrem('product_list', *arr)
        print('aftersleep')

def task_checkhospital():
    con = get_redis_connection('default')
    beforecheck(sys._getframe().f_code.co_name)
    while 1:
        arr=con.zrange('hospital_list',0,100)
        for did in arr:
            checkhospital(did.decode())
        #time.sleep(0.01)
        con.zrem('hospital_list', *arr)
        print('aftersleep')
from grab.checkuser import checkuserflow,checkuserfans
def task_checkdoctor():
    con = get_redis_connection('default')
    beforecheck(sys._getframe().f_code.co_name)
    while 1:
        arr=con.zrange('doctor_list',0,100)
        for did in arr:
            checkdoctor(did.decode())
        #time.sleep(0.01)
        con.zrem('doctor_list', *arr)
        print('aftersleep')
task_checkproduct()

#164361819