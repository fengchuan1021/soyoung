#信息流
import sys
import django
import os
import pathlib

if __name__ == "__main__":
    basedir = str(pathlib.Path(__file__).resolve().parent.parent)
    os.chdir(basedir)
    sys.path.append(basedir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'soyoung.settings'
    django.setup()

from grab.createsession import createsession
from grab.models import Product, Hospital, Doctor,Diary,Reviewer
import datetime, time
from django.conf import settings
import psutil


def check():
    pidfile = os.path.split(__file__)[-1] + '.pid'
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


def grab():
    check()
    session = createsession()
    session.headers.update({'content-type': 'application/x-www-form-urlencoded'})
    page = 0
    now = str(datetime.datetime.now())
    while 1:
        time.sleep(1 if settings.DEBUG else 5)
        page += 1
        url = f'https://m.soyoung.com/site/index-ajax-feed?page={page}&menu_id=0&menu_name=%E6%8E%A8%E8%8D%90&part=2&cityId=0&newFeed=1'  # &calendar_type=3&menu1_id=undefined&select_id=undefined
        print(url)
        try:
            # if 1:
            ret = session.get(url).json()
            print(ret)
            if 'feed_list' in ret and ret['feed_list']:
                for obj in ret['feed_list']:
                    diaryid=obj['data']['post_id']
                    m=Diary.objects.filter(ReviewID=diaryid).first()
                    if not m:
                        m=Diary()
                        m.ReviewID=diaryid
                    m.RCrawlDate=now
                    m.ReviewImageNum=len(obj['data']['content_imgs'])
                    m.IsImageReview=True if len(obj['data']['content_imgs']) else False
                    m.IsVideoReview=True if obj['data']['post_video_url'] else False
                    m.ReviewDate=obj['data']['create_date']
                    m.ReviewImage='' if len(obj['data']['content_imgs'])==0 else '#'.join([item['u'] for item in obj['data']['content_imgs']])
                    m.ReviewVideo=obj['data']['post_video_url']
                    m.ReviewViews=obj['data']['view_cnt']
                    uid=obj['data']['uid']
                    user=Reviewer.objects.filter(ReviewerID=uid).first()
                    if not user:
                        user=Reviewer()
                        user.ReviewerID=uid
                        #user.ReviewerLevel=obj['data']['user']['level'] if obj['data']['user']['level'] else 0
                        user.ReviewerName=obj['data']['user']['user_name']
                        user.save()
                    m.ReviewerID=user
                    m.save()
            else:
                break
            if not int(ret['has_more']):
                break
        except Exception as e:
            print(e)
            break


if __name__ == "__main__":
    grab()