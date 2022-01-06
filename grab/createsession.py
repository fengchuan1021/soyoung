import requests
useragent='''Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'''
def createsession():
   session=requests.session()
   session.headers.update({'user-agent':useragent})
   # ret = session.get(
   #    'http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=81ee6adb3ca092a962aa8fe95b640a0e&orderNo=GL20220105215337psU7c529&count=1&isTxt=0&proxyType=1')
   # ip = ret['obj'][0]['ip']
   # port = ret['obj'][0]['port']
   return session
