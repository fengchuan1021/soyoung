import time

import requests
useragent='''Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'''
import os
import time
from django.core.cache import cache
class mysession:
   def __init__(self):
      self.session = requests.session()
      if proxyip:=cache.get('proxyip'):
         self.session.proxies=proxyip
      self.session.headers.update({'user-agent': useragent})
      pass
   def changeip(self):
      try:
         print('chagnip')
         apistr=os.getenv('IPAPI')
         print(apistr)
         if cache.get('proxyflag'):
            return 0
         cache.set('proxyflag',1,timeout=2)
         ret=requests.get(apistr).json()
         print(ret)
         print('proxyip:',ret['obj'][0])
         port=ret['obj'][0]['port']
         ip=ret['obj'][0]['ip']
         proxies={
            'http':f'{ip}:{port}',
            'https':f'{ip}:{port}'
            }
         cache.set('proxyip',proxies)
         self.session.proxies=proxies
      except Exception as e:
         print(e)
   @property
   def headers(self):
      return self.session.headers
   def post(self,*args,**kwargs):
      try:
         while 1:
            try:
               ret=self.session.post(*args,**kwargs)
            except Exception as e:
               self.changeip()
               time.sleep(2)
               continue
            if 'ERROR: ACCESS DENIED' in ret.text:
               self.changeip()
            else:
               break
         return ret
      except Exception as e:
         print(35,e)
         return ret
      pass
   def get(self,*args,**kwargs):
      try:
         while 1:
            try:
               ret=self.session.get(*args,**kwargs)
            except Exception as e:
               print(e)
               self.changeip()
               time.sleep(0.01)
               continue
            if 'ERROR: ACCESS DENIED' in ret.text:
               self.changeip()
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
