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
        did=int(con.spop('diary_list'))
        checkdiary(did)
        time.sleep(5)
        print('aftersleep')


def task_checkuser():
    con = get_redis_connection('default')
    beforecheck(sys._getframe().f_code.co_name)
    while 1:
        did=int(con.spop('user_list'))
        tmp=checkuser(did)
        time.sleep(5 if tmp else 1)
        print('aftersleep')

def task_checkproduct():
    con = get_redis_connection('default')
    beforecheck(sys._getframe().f_code.co_name)
    while 1:
        did=int(con.spop('product_list'))
        tmp=checkproduct(did)
        time.sleep(10 if tmp else 1)
        print('aftersleep')

def task_checkhospital():
    con = get_redis_connection('default')
    beforecheck(sys._getframe().f_code.co_name)
    while 1:
        did=int(con.spop('hospital_list'))
        checkhospital(did)
        time.sleep(5)
        print('aftersleep')
from grab.checkuser import checkuserflow,checkuserfans
def task_checkdoctor():
    con = get_redis_connection('default')
    beforecheck(sys._getframe().f_code.co_name)
    while 1:
        did=int(con.spop('doctor_list'))
        checkdoctor(did)
        time.sleep(5)
        print('aftersleep')
