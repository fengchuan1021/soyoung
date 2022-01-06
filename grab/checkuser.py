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
from grab.models import Product, Hospital, Reviewer,Diary,Doctor
import datetime, time
import re, json
import psutil
from django.conf import settings
from django.core.cache import cache
from dotmap import DotMap
from bs4 import BeautifulSoup
def setusercollect_cnt(uid,cnt):
    if cache.get(f'u_collectcnt:{uid}'):
        return 0
    model=Reviewer.objects.get(ReviewerID=uid)
    model.ReviewerLikes=int(cnt)
    model.save()
    cache.set(f'u_collectcnt:{uid}',1,timeout=3600*24)
    return 1
def checkdiary(pid):
    now = str(datetime.datetime.now())
    if cache.get(f'p:{pid}'):
        return 0
    cache.set(f'p:{pid}',1,timeout=3600*24*5)
    model=Diary.objects.filter(ReviewID=pid).first()
    if not model:
        model=Diary()
        model.ReviewerID_id=pid
    session=createsession()
    try:
    #if 1:
        ret=session.get(f'https://www.soyoung.com/p{pid}')
        print(f'https://www.soyoung.com/p{pid}')
        soup=BeautifulSoup(ret.text)
        try:
            model.ReviewContent=re.findall(r'html:"(.*?)",',ret.text)[0]
        except Exception as e:
            model.ReviewContent=''
        model.ReviewReplyNum=re.findall(r'评论：(\d+)',ret.text)[0]
        model.ReviewFollowNum=re.findall(r'收藏：(\d+)',ret.text)[0]
        model.ReviewLikeNum = re.findall(r'点赞：(\d+)', ret.text)[0]
        model.RCrawlDate=now
        model.IsCustom1Review=True if re.findall(r'通过新氧消费',ret.text) else False
        model.IsCustom2Review= True if re.findall(r'上传消费凭证', ret.text) else False
        model.IsEOReview=True if len(re.findall(r'体验官日记', ret.text))>=2 else False
        model.IsVideoReview =True if re.findall(r'video=\{',ret.text) else False
        model.IsImageReview=True if re.findall(r'swiper-container',ret.text) else False
        #model.ReviewDate=re.findall(r'create_date="(.*?)"',ret.text)[0]
        model.ReviewDate=re.findall(r'(\d+-\d+-\d+ \d+:\d+:\d+)',soup.select('p.post-create-date')[0].text)[0]
        model.ReviewViews=tmp[0] if (tmp:=re.findall(r'view_cnt="(\d+)"',ret.text)) else 0
        model.ReviewERating=tmp[0] if (tmp:=re.findall(r'机构环境：([0-9\.]+)',ret.text)) else 0
        model.ReviewSRating = tmp[0] if (tmp := re.findall(r'服务态度：([0-9\.]+)',ret.text)) else 0
        model.ReviewTRating=tmp[0] if (tmp := re.findall(r'项目效果：([0-9\.]+)',ret.text)) else 0
        model.ReviewPRating=tmp[0] if (tmp := re.findall(r'医生专业：([0-9\.]+)',ret.text)) else 0
        model.ReviewImageNum=len(tmp) if (tmp:=re.findall(r'class="blur-img"',ret.text)) else 0

        model.ReviewImage='#'.join(map(lambda x: x['src'],soup.select('div.blur-img img')))
        model.ReviewVideo=tmp[0] if (tmp:=re.findall(r'video=\{url:"(.*?)"',ret.text)) else ''

        model.HospitalResponseText = ''  # 机构回复
        model.ReviewAddText=''
        model.FollowReviewNum=0
        model.ReviewerID_id=re.findall(r'uid=(\d+)',ret.text)[0]
        model.ReviewID=pid
        try:
            setusercollect_cnt(model.ReviewerID_id,re.findall(r'favourite_collect_cnt=(\d+)',ret.text)[0])
        except Exception as e:
            print(e)
            pass
        model.save()
    except Exception as e:
        cache.set(f'p:{pid}',1, timeout=360)
        print(e)
import js2py
def checkdoctorxiangmu(did):
    if int(did)==0:
        return 0
    if cache.get(f'dp:{did}'):
        return 0
    cache.set(f'dp:{did}')
    now = str(datetime.datetime.now())
    try:
        url='https://m.soyoung.com/doctor/infov3tabproduct'
        session=createsession()
        page=0
        while 1:
            page+=1
            ret=session.post(url,data=f'doctor_id={did}&index={page}').json()
            obj=DotMap(ret)
            model=Doctor.objects.filter(DoctorID=did).first()
            if not model:
                model = Doctor()
                model.DoctorID = did
            model.DoctorProjectNum=obj.total
            mdoel.DoctorSales=obj.order_cnt
            try:
                model.save()
            except Exception as e:
                pass

    except Exception as e:
        print(e)
    doctor_id
def checkdoctor(did):
    if int(did)==0:
        return 0
    if cache.get(f'd:{did}'):
        return 0
    cache.set(f'd:{did}',1,timeout=3600*24*5)
    now = str(datetime.datetime.now())
    try:
        url=f'https://www.soyoung.com/doctor/{did}/'
        session=createsession()
        ret=session.get(url)
        #session.post('https://m.soyoung.com/doctor/infov3tabproduct')
        b=js2py.eval_js(re.findall(r'(window\.__NUXT__.*?);</script>',ret.text)[0])

        #soup=BeautifulSoup(ret.text)
        model=Doctor.objects.filter(DoctorID=did).first()
        if not model:
            model=Doctor()
            model.DoctorID=did
        model.DCrawlDate=now
        model.DoctorName=b.fetch["data-v-625304e2:0"].info.doctor.name_cn
        model.DoctorCity=b.fetch["data-v-625304e2:0"].info.doctor.hospital_city
        model.ProfessionalTitle=b.fetch["data-v-625304e2:0"].info.doctor.extend.positionName
        model.WorkYear=b.fetch["data-v-625304e2:0"].info.doctor.career
        try:
            model.HospitalID_id=b.fetch["data-v-625304e2:0"].info.doctor.main_hospital[0].hospital_id
            model.HospitalName=b.fetch["data-v-625304e2:0"].info.doctor.main_hospital[0].hospital_name

        except Exception as e:
            pass
        model.DoctorGender=b.fetch["data-v-625304e2:0"].info.doctor.gender
        model.DoctorRating=b.fetch["data-v-625304e2:0"].info.doctor_card.five_stars_score.satisfy
        model.DGCNum=b.fetch["data-v-625304e2:0"].info.statistics.official_cnt
        model.ExpertArea='#'.join([item.name for item in b.fetch["data-v-625304e2:0"].info.doctor.extend.expert_all])
        model.DoctorBio=b.fetch["data-v-625304e2:0"].info.doctor.intro
        model.DoctorSRating=b.fetch["data-v-625304e2:0"].info.doctor_card.five_stars_score.service
        model.DoctorPRating=b.fetch["data-v-625304e2:0"].info.doctor_card.five_stars_score.specialty
        model.DoctorTRating=b.fetch["data-v-625304e2:0"].info.doctor_card.five_stars_score.effect
        model.DoctorReviewNum=b.fetch["data-v-625304e2:0"].info.statistics.diary_cnt
        model.DoctorFollower=b.fetch["data-v-625304e2:0"].info.statistics.fans_cnt
        model.DoctorPosrate=b.fetch["data-v-625304e2:0"].info.koubeiAndDiary.avg_info.high_percent
        for tmp in b.fetch["data-v-625304e2:0"].info.face_consultation_card.list:
            if tmp.allow_yn:
                if tmp.type==2:
                    model.VideoService=True
                    model.VideoPrice=tmp.price_str
                elif tmp.type==3:
                    model.VoiceService=True
                    model.VideoPrice=tmp.price_str
                elif tmp.type==1:
                    model.TextService=True
                    model.TextPrice=tmp.price_str


        model.DReviewNum=
        model.DAddNum=
        model.DNegReviewNum=
        model.DImageReviewNum=
        model.DVideoReviewNum=
        model.DPostReviewNum=

        model.DoctorConsultation=b.fetch["data-v-625304e2:0"].info.statistics.patient_cnt



    except Exception as e:
        print(e)
    pass
def checkuser(uid):
    if int(uid)==0:
        return 0
    if cache.get(f'u:{uid}'):
        return 0
    cache.set(f'u:{uid}',1,timeout=3600*24*7)
    page = 0
    while 1:
        page += 1
        time.sleep(5 if settings.DEBUG else 5)
        session = createsession()
        try:
        #if 1:
            # url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
            url = f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&type=1'
            print(url)

            ret = session.get(url).json()
            if 'data' in ret and 'redirect' in ret['data']:
                if (tmp:=re.findall(r'd(\d+)',ret['data']['redirect'])):
                    checkdoctor(tmp[0])
                return 0
            model=Reviewer.objects.filter(ReviewerID=ret['data']['info']['uid']).first()
            if not model:
                model=Reviewer()
                model.ReviewerID=ret['data']['info']['uid']
            model.ReviewerName=ret['data']['info']['user_name']
            model.ReviewerLevel=ret['data']['info']['xy_money']
            model.ReviewerExp = ret['data']['info']['experience']
            model.ReviewerAge=ret['data']['info']['age']
            model.ReviewerGender='女' if int(ret['data']['info']['gender'])==0 else '男'
            obj=DotMap(ret)
            model.ReviewerFollwer=obj.data.info.type_total.fans_total
            model.ReviewerPosts=obj.data.info.type_total.pub_post_total
            model.ReviewerFollowee=obj.data.info.type_total.follow_total
            model.save()
            #print('len:',obj.data.person_post.responseData.post_list.list)
            if len(obj.data.person_post.responseData.post_list.list)==0:
                break
            for item in obj.data.person_post.responseData.post_list.list:
                checkdiary(item.post_id)
                time.sleep(2)
        except Exception as e:
            print(e)
            break


def checkuserfans(uid):
    if int(uid)==0:
        return 0
    if cache.get(f'ufans:{uid}'):
        return 0
    cache.set(f'ufans:{uid}',1,timeout=3600*24*7)
    page = 0
    while 1:
        page += 1
        time.sleep(5 if settings.DEBUG else 5)
        session = createsession()
        try:
        #if 1:
            # url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
            url = f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&type=1'
            url=f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&flag=2'
            print(url)

            ret = session.get(url).json()
            if 'data' in ret and 'redirect' in ret['data']:
                return 0
            obj=DotMap(ret)

            #print('len:',obj.data.person_post.responseData.post_list.list)
            if len(obj.data.person_fans.responseData.user_info)==0:
                return 0
            for item in obj.data.person_fans.responseData.user_info:
                checkuser(item.uid)
                time.sleep(2)
        except Exception as e:
            print(e)
            break

def checkuserflow(uid):
    if int(uid)==0:
        return 0
    if cache.get(f'uflow:{uid}'):
        return 0
    cache.set(f'uflow:{uid}',1,timeout=3600*24*7)
    page = 0
    while 1:
        page += 1
        time.sleep(5 if settings.DEBUG else 5)
        session = createsession()
        try:
        #if 1:
            # url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
            url = f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&type=1'
            url=f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&flag=1'
            print(url)

            ret = session.get(url).json()
            if 'data' in ret and 'redirect' in ret['data']:
                return 0
            obj=DotMap(ret)

            #print('len:',obj.data.person_post.responseData.post_list.list)
            if len(obj.data.person_fans.responseData.user_info)==0:
                return 0
            for item in obj.data.person_fans.responseData.user_info:
                checkuser(item.uid)
                time.sleep(2)
        except Exception as e:
            print(e)
            break


checkuser(148250195)