import random
import time

import requests
useragent='''Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'''
import os
import time,re
from django.core.cache import cache
import random
import re

class mysession:
   proxyips=[]
   def __init__(self):
      self.session = requests.session()

      self.session.headers.update({'user-agent': useragent})
      if self.__class__.proxyips:
         self.session.proxies=random.choice(self.proxyips)
   def changeip(self):
      try:

         ret=requests.get('http://proxy.httpdaili.com/apinew.asp?ddbh=2535043392946477733')
         tmparr=re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)',ret.text)
         self.__class__.proxyips=[{'http':proxy,'https':proxy} for proxy in tmparr]
         proxy=random.choice(self.__class__.proxyips)
         print(proxy)
         self.session.cookies.clear()
         self.session.proxies=proxy
      except Exception as e:
         self.session.proxies = None
         print(e)
   @property
   def headers(self):
      return self.session.headers
   def post(self,*args,**kwargs):
      kwargs['timeout']=2
      try:
         while 1:
            try:
               # tarhost=re.findall(r'https?://(.*?)/',args[0])[0]
               # self.session.headers.update({'Host':tarhost})
               # myarg=list(args)
               # myarg[0]=myarg[0].replace(tarhost,random.choice(dnsips)).replace('https','http')

               ret=self.session.post(*args,**kwargs)
            except Exception as e:
               print(e)
               self.session.proxies=None
               self.changeip()
               time.sleep(0.1)
               continue
            if 'ERROR: ACCESS DENIED' in ret.text or 'verification.soyoung.com' in ret.text:
               pass
               self.changeip()
            else:
               break
         return ret
      except Exception as e:
         print(35,e)
         return ret
      pass
   def get(self,*args,**kwargs):
      kwargs['timeout'] = 2
      try:
         while 1:
            try:

               ret=self.session.get(*args,**kwargs)


            except Exception as e:
               print(e)
               self.changeip()
               time.sleep(0.01)
               continue
            if 'ERROR: ACCESS DENIED' in ret.text  or 'verification.soyoung.com' in ret.text:
               print('deny?????')
               pass
               self.changeip()
            elif '<h1>404 Not Found</h1>' in ret.text:
               self.changeip()
               continue
            else:
               break
         return ret
      except Exception as e:
         return ret
      pass
def createsession():
   session=mysession()



   # ret = session.get(
   #    'http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=81ee6adb3ca092a962aa8fe95b640a0e&orderNo=GL20220105215337psU7c529&count=1&isTxt=0&proxyType=1')
   # ip = ret['obj'][0]['ip']
   # port = ret['obj'][0]['port']
   return session
