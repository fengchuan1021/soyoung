#日记推荐
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
from grab.models import Product,Hospital,Doctor,Reviewer,Diary
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
    session=createsession()
    session.headers.update({'content-type':'application/x-www-form-urlencoded'})
    page=0
    now=str(datetime.datetime.now())
    while 1:
        time.sleep(1 if settings.DEBUG else 5)
        page += 1
        data=f'uid=0&post_id=31317049&limit=20&index={page}'
        url=f'https://m.soyoung.com/post/getRePost'#&calendar_type=3&menu1_id=undefined&select_id=undefined
        print(url)
        try:
        #if 1:
            ret=session.post(url,data=data).json()
            print(ret)
            if 'responseData' in ret and 'list' in ret['responseData']:
                for obj in ret['responseData']['list']:
                    id=obj['data']['post_id']
                    m=Diary.objects.filter(ReviewID=id).first()
                    if not m:
                        m=Diary()
                        m.ReviewID=id
                    m.ParentId_id=None if not int(obj['data']['base']['related_id']) else int(obj['data']['base']['related_id'])
                    #m.FollowReviewNum=0 if obj['data']['stat']['collection_cnt']==1 else obj['data']['stat']['collection_cnt']
                    m.ReviewReplyNum=obj['data']['stat']['comment_cnt']
                    m.ReviewFollowNum=obj['data']['stat']['collection_cnt'] #['favorite_cnt' 'ReviewLikeNum']
                    m.ReviewLikeNum=obj['data']['stat']['favorite_cnt']
                    m.ReviewImageNum=obj['data']['stat']['image_cnt']
                    m.ReviewViews=obj['data']['stat']['view_cnt']
                    uid=obj['data']['post_user']['uid']
                    if uid:
                        user=Reviewer.objects.filter(ReviewerID=uid).first()
                        if not user:
                            user=Reviewer()
                            user.ReviewerID=uid

                        user.ReviewerAge=obj['data']['post_user']['age']

                        user.ReviewerName=obj['data']['post_user']['user_name']
                        user.ReviewerGender='女' if obj['data']['post_user']['gender']=="0" else "男"
                        user.save()
                        m.ReviewerID_id = user.ReviewerID

                    m.ReviewDate=obj['data']['base']['create_date']
                    m.save()
            else:
                break
            if 'responseData' in ret and 'has_more' in ret['responseData'] and int(ret['responseData']['has_more'])==0:
                break
        except Exception as e:
            print(e)
            break

if __name__=="__main__":
    grab()