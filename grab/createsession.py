import random
import time

import requests
useragent='''Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'''
import os
import time,re
from django.core.cache import cache
dnsips='''125.44.162.62

中国 江苏 苏州 移动36.156.131.38

中国 陕西 安康 联通113.201.105.2

中国 河南 南阳 联通125.44.162.61


中国 安徽 合肥 联通211.91.76.19

中国 四川 成都 电信118.121.192.79

中国 广东 惠州 移动183.232.112.71

中国 陕西 安康 联通113.201.105.3

中国 山东 济宁 移动120.220.20.105

中国 广东 惠州 移动183.232.112.84

中国 湖北 仙桃 电信61.184.241.80

中国 湖北 仙桃 电信61.184.241.82

中国 安徽 合肥 联通211.91.76.15

中国 湖北 仙桃 电信61.184.241.81

中国 湖北 仙桃 电信61.184.241.77

中国 上海 宝山 电信218.78.243.231

中国 四川 成都 电信118.121.192.74

中国 江苏 苏州 移动36.156.131.55

中国 陕西 安康 联通113.201.105.7

中国 湖北 仙桃 电信61.184.241.68

中国 河南 南阳 联通125.44.162.59

中国 山东 济宁 移动120.220.20.116

中国 上海 宝山 电信218.78.243.232

中国 山东 济宁 移动120.220.20.100

中国 陕西 安康 联通113.201.105.6

中国 四川 成都 电信118.121.192.78

中国 安徽 合肥 联通211.91.76.4

中国 上海 宝山 电信218.78.243.226

中国 江苏 苏州 移动36.156.131.46

中国 湖北 仙桃 电信61.184.241.71

中国 湖北 仙桃 电信61.184.241.75

中国 广东 惠州 移动183.232.112.76'''
dnsips=re.findall(r'([0-9\.]+)',dnsips)
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
            time.sleep(1)
            print('not realchange')
            return 0
         cache.set('proxyflag',1,timeout=180)
         ret=requests.get(apistr).json()
         print(ret)
         print('proxyip:',ret['obj'][0])
         port=ret['obj'][0]['port']
         ip=ret['obj'][0]['ip']
         proxies={
            'http':f'{ip}:{port}',
            'https':f'{ip}:{port}'
            }
         cache.set('proxyip',proxies,timeout=240)
         #print(self.)
         self.session.cookies.clear()
         self.session.proxies=proxies
         print(self.session.proxies)
      except Exception as e:
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

               ret=self.session.post(*myarg,**kwargs)
            except Exception as e:
               print(e)
               self.session.proxies=None
               time.sleep(2)
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
               if 0 and '?' not in args[0]:

                  tarhost=re.findall(r'https?://(.*?)/',args[0])[0]
                  self.session.headers.update({'Host':tarhost})
                  myarg=list(args)
                  myarg[0]=myarg[0].replace(tarhost,random.choice(dnsips)).replace('https','http')

                  print(tarhost,myarg[0])
                  ret=self.session.get(*myarg,**kwargs)
               else:
                  ret = self.session.get(*args, **kwargs)

            except Exception as e:
               print(e)
               self.session.proxies=None
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
