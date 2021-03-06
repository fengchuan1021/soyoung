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

def gettext(data):
    try:
        data.encode("utf-8")
    except UnicodeEncodeError as e:
        if e.reason == 'surrogates not allowed':
            data = data.encode('utf-8', "backslashreplace").decode('utf-8')
    return data

def setusercollect_cnt(uid,cnt):
    try:
        if cache.get(f'u_collectcnt:{uid}'):
            return 0
        model=Reviewer.objects.get(ReviewerID=uid)
        model.ReviewerLikes=int(cnt)
        model.save()
        cache.set(f'u_collectcnt:{uid}',1,timeout=3600*24)
        return 1
    except Exception as e:
        pass
def checkproduct(pid):
    now = str(datetime.datetime.now())
    if 1 and cache.get(f'product:{pid}'):
        return 0
    cache.set(f'product::{pid}',1,timeout=3600*24*5)
    model=Product.objects.filter(ProductID=pid).first()
    if not model:
        model=Product()
        model.ProductID=pid
    model.PCrawlDate=now
    try:
        url=f"https://www.soyoung.com/cp{pid}"
        print(url)
        session=createsession()
        useragent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        session.headers.update({'user-agent': useragent})
        ret=session.get(url)

        b=js2py.eval_js(re.findall(r'(window\.__NUXT__.*?)</script>',ret.text)[0])
        soup=BeautifulSoup(ret.text,features="html.parser")
        #key=soup.select('.main')[0].attrs['data-fetch-key']
        key=soup.find(lambda x: x.has_attr("data-fetch-key") and not (x.has_attr('class') and 'search-header' in x['class'])).attrs['data-fetch-key']

        #exit(0)
        #print(b.fetch[key])
        model.ProductName=b.fetch[key].productData.title
        model.HospitalID_id=b.fetch[key].productData.product.hospital.id
        model.HospitalName=b.fetch[key].productData.product.hospital.name_cn
        model.HospitalRating=b.fetch[key].productData.product.hospital.satisfy
        model.DoctorNum=tmp[0] if (tmp:=re.findall(r'(\d+)',b.fetch[key].productData.product.hospital.doctor_cnt)) else 0
        model.HospitalAddress=b.fetch[key].productData.product.hospital.address
        model.ProductOPrice=b.fetch[key].productData.product.price_origin
        model.ProductPrice=b.fetch[key].productData.product.price_online
        model.ProductSale=b.fetch[key].productData.product.show_order_cnt
        #model.ReturnRatio=
        #?????????
        # try:
        #     for tmp in b.fetch["data-v-16523c62:0"].productData.product.recommend:
        #         try:
        #             tmpmodel=Product.objects.filter(ProductID=tmp['pid']).first()
        #             if not tmpmodel:
        #                 tmpmodel=Product()
        #                 tmpmodel.ProductID=tmp['pid']
        #             tmpmodel.ProductName=tmp['title']
        #             tmpmodel.ReturnRatio=tmp['over_30day']
        #             tmpmodel.save(update_fields=['ProductName','ReturnRatio'])
        #         except Exception as e:
        #             pass
        # except Exception as e:
        #     print(e)
        if b.fetch[key].productData.product.content.describe_other:
            for item in b.fetch[key].productData.product.content.describe_other:
                if item['name']=='????????????':
                    model.ProductAPrice=sum([float(i[0]) for tmp in item['list'] if (i:=re.findall(r'([0-9\.]+)',tmp['price']))])
        model.save()
        checkproductdiary(pid)
    except Exception as e:
        print(e)
    return 1
def checkproductdiary(pid):
    now = str(datetime.datetime.now())

    if 1 and cache.get(f'productdiary:{pid}'):
        return 0
    cache.set(f'productdiary::{pid}',1,timeout=3600*24*5)
    model=Product.objects.filter(ProductID=pid).first()
    if not model:
        model=Product()
        model.ProductID=pid
    model.PCrawlDate=now
    try:
        url=f"https://www.soyoung.com/yuehui/ProductShortComment?pid={pid}&range=10&index=0&tag_id=0&tag_type=all"
        session=createsession()
        ret=session.get(url).json()
        obj=DotMap(ret)

        model.PReviewNum=obj.total
        for item in obj.base_review_tag_list:
            if item.name=='???????????????':
                model.PPostReviewNum=int(item.cnt) if item.cnt else 0
            elif item.name=='??????':
                model.PNegReviewNum=int(item.cnt) if item.cnt else 0
            elif item.name=='??????':
                model.PAddReviewNum = int(item.cnt) if item.cnt else 0
            elif item.name=='??????':
                model.PImageReviewNum = int(item.cnt) if item.cnt else 0
            elif item.name == '?????????':
                model.PVideoReviewNum = int(item.cnt) if item.cnt else 0

        model.save()
        con = get_redis_connection('default')

        for item in obj.list:
            try:
                con.zadd('diary_list', {item['post_id']:int(time.time())})
                con.zadd('user_list',{item['post_user']['uid']:int(time.time())})
            except Exception as e:
                print(e)

    except Exception as e:
        print(e)
def checkdiaryreply(pid):
    if 1 and cache.get(f'diaryreply:{pid}'):
        return 0
    cache.set(f'diaryreply:{pid}',1,timeout=3600*24*5)
    try:
        url=f'https://www.soyoung.com/post/getreplylist?post_id={pid}&page=1&limit=15'
        sesson=createsession()
        ret=sesson.get(url).json()
        obj=DotMap(ret)
        flag=0
        model=Diary.objects.get(ReviewID=pid)
        con = get_redis_connection('default')
        for item in obj.responseData.list:
            if int(item['certified_type'])==2 and not flag:
                flag=1
                model.HospitalResponseText = item['content_new']  # ????????????
            elif  int(item['certified_type'])!=2 :
                con.zadd('user_list',{item['uid']:int(time.time())})
        model.save()
        try:
            con = get_redis_connection('default')
            for item in obj.responseData.list:
                con.zadd('user_list',{item['uid']:int(time.time())})
        except Exception as e:
            print(e)
    except Exception as e:
        print(127,e)
def checkdiary(pid):
    now = str(datetime.datetime.now())
    if 1 and cache.get(f'diary:{pid}'):
        return 0
    cache.set(f'diary:{pid}',1,timeout=3600*24*5)
    model=Diary.objects.filter(ReviewID=pid).first()
    if not model:
        model=Diary()
        model.ReviewID=pid
    session=createsession()
    try:
    #if 1:
        print(f'https://www.soyoung.com/p{pid}')
        ret=session.get(f'https://www.soyoung.com/p{pid}')

        b = js2py.eval_js(re.findall(r'(window\.__NUXT__.*?)</script>', ret.text)[0])
        try:
            #model.ReviewContent=b.fetch["data-v-56804bd0:0"].res.content[0].raw_text
            key=re.findall(r'class="main".*data-fetch-key="(.*?)" class="post-page"',ret.text)[0]
            print(f'{key=}')
            model.ReviewContent='\n'.join([tmp['raw_text'] for tmp in b.fetch[key].res.content if 'raw_text' in tmp])
        except Exception as e:
            print(e)
        model.ReviewReplyNum=b.fetch[key].stat.comment_cnt
        model.ReviewFollowNum=b.fetch[key].stat.collection_cnt
        model.ReviewLikeNum = b.fetch[key].stat.real_favorite_cnt
        model.RCrawlDate=now


        try:
            if int(b.fetch[key].post_user.certified_type)==3:
                model.DoctorID=b.fetch[key].post_user.certified_id
        except Exception as e:
            pass
        if 'extension' in b.fetch[key] and  b.fetch[key].extension and b.fetch[key].extension.display_label_list:
            for item in b.fetch[key].extension.display_label_list:
                if item['name']=='??????????????????':
                    model.IsCustom1Review=True
                elif item['name']=='??????????????????':
                    model.IsCustom2Review = True
                elif item['name'] == '???????????????':
                    model.IsEOReview = True
                    try:
                        Reviewer.objects.filter(ReviewerID=b.fetch[key].post_user.uid).update(IsEOuser=True)
                    except Exception as e:
                        pass
                elif item['name']=='??????':
                    model.IsCase=True


        try:
            model.IsVideoReview =False if 'video' not in b.fetch[key].media else True
            model.IsImageReview=False if 'content_image_list' not in b.fetch[key].media else True
        except Exception as e:
            pass
        #model.ReviewDate=re.findall(r'create_date="(.*?)"',ret.text)[0]
        model.ReviewDate=b.fetch[key].base.create_date
        model.ReviewViews=b.fetch[key].stat.view_cnt

        if 'star_score' in b.fetch[key] and b.fetch[key].star_score:
            model.ReviewERating=b.fetch[key].star_score.environment
            model.ReviewSRating =b.fetch[key].star_score.service
            model.ReviewTRating=b.fetch[key].star_score.effect
            model.ReviewPRating=b.fetch[key].star_score.specialty
            model.ReviewRating = b.fetch[key].star_score.satisfy  # ????????????

        model.ReviewTextLen=b.fetch[key].stat.text_cnt
        model.ReviewImageNum=b.fetch[key].stat.image_cnt
        try:
            model.ReviewImage='' if 'content_image_list' not in b.fetch[key].media else '#'.join([ item['url'] for item in b.fetch[key].media.content_image_list])
            model.ReviewVideo='' if 'video' not in b.fetch[key].media else b.fetch[key].media.video.url
        except Exception as e:
            pass


        model.ReviewAddText='' if ('append' not in b.fetch[key] or not b.fetch[key].append) else '#'.join([item.content[0].raw_text for item in b.fetch[key].append])

        model.FollowReviewNum=b.fetch[key].res.collect_diary_list.diary_cnt if 'collect_diary_list' in  b.fetch[key].res else 0
        model.ReviewerID_id=b.fetch[key].post_user.uid
        con = get_redis_connection('default')

        try:
            if 'collect_diary_list' in b.fetch[key].res:
                model.CollectionID=b.fetch[key].res.collect_diary_list.collection_id

                for item in b.fetch[key].res.collect_diary_list.list:
                    try:
                        con.zadd('diary_list',{item['post_id']:int(time.time())})
                    except Exception as e:
                        print(e)
                        pass
        except Exception as e:
            pass
        model.ReviewID=pid
        if 'doctor_card' in b.fetch[key].attribute:
            model.DoctorID_id=b.fetch[key].attribute.doctor_card[0].doctor_id
            model.DoctorName=b.fetch[key].attribute.doctor_card[0].name_cn
            con.zadd('doctor_list',{model.DoctorID_id:int(time.time())})
        if 'hospital_card' in b.fetch[key].attribute:
            model.HospitalID_id=b.fetch[key].attribute.hospital_card[0].hospital_id
            model.HospitalName=b.fetch[key].attribute.hospital_card[0].name_cn
            con.zadd('hospital_list',{model.HospitalID_id:int(time.time())})

        if 'product_card' in b.fetch[key].attribute:
            model.ProductID_id=b.fetch[key].attribute.product_card[0].product.pid
            model.ProductName=b.fetch[key].attribute.product_card[0].product.title
            con.zadd('product_list',{model.ProductID_id:int(time.time())})
        model.IsHQReview=True if b.fetch[key].res.audit.quality_type and int(b.fetch[key].res.audit.quality_type)==2 else False #????????????

        # try:
        #     setusercollect_cnt(model.ReviewerID_id,b.fetch[key].post_user.favourite_collect_cnt)
        # except Exception as e:
        #     print(e)
        #     pass

        try:
            for item in b.fetch[key].recommend:
                if 'type' in item and item['type']==35:
                    con.zadd('diary_list',{item['data']['post_id']:int(time.time())})
                    con.zadd('user_list',{item['data']['uid']:int(time.time())})
        except Exception as e:
            print(e)


        model.save()

        try:
            checkdiaryreply(pid)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

def checkhospital(pid):
    now = str(datetime.datetime.now())
    if 1 and cache.get(f'hospital:{pid}'):
        return 0
    cache.set(f'hospital:{pid}',1,timeout=3600*24*5)
    model=Hospital.objects.filter(HospitalID=pid).first()
    if not model:
        model=Hospital()
        model.HospitalID=pid
    try:
        session = createsession()
        ret = session.get(f'https://m.soyoung.com/y/hospital/{pid}')
        soup = BeautifulSoup(ret.text,features="html.parser")
        base=DotMap(json.loads(soup.select_one('#globalData', features="html.parser").string))

        url=f'https://m.soyoung.com/hospital/HospitalMoreInfo?hospital_id={pid}&json=1'

        ret=session.get(url).json()
        obj=DotMap(ret)
        model.CrawlTime=now
        model.HospitalName=base.hospital_info.name_cn
        model.HospitalRating=base.hospital_info.satisfy
        model.HospitalURating=base.hospital_info.post_effect
        model.HospitalTRating=base.hospital_info.post_environment
        model.HospitalSRating=base.hospital_info.post_service
        model.HospitalAddress=base.hospital_info.address
        model.HospitalCity=base.hospital_info.district2_name
        model.Reputation='#'.join([item.award_title for item in base.hospital_info.award])
        model.ReputNum=0 if 'award' not in base.hospital_info else len(base.hospital_info.award)
        model.RecodeYear=base.hospital_info.record_date
        model.DoctorNum=obj.data.hospital_info.doctor_cnt
        model.HospitalFollower=base.hospital_info.fansCnt
        #try:
            #model.HospitalType=int(obj.data.hospital_info.institution_type)
        # except Exception as e:
        #     pass

        model.MGCNum=0#??????????????????
        try:
            ret=session.get(f'https://m.soyoung.com/hospital/profession?hospital_id={pid}')

            model.APatentNum=tmp[0] if (tmp:=re.findall(r'(\d+)?????????',ret.text)) else 0
        except Exception as e:
            print(e)
        model.save()
        try:
            checkhospitalproject(pid)
        except Exception as e:
            print(e)
        try:
            checkhospitaldiary(pid)
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)

    pass
def checkhospitalproject(id):
    now = str(datetime.datetime.now())
    if cache.get(f'hostpital_project:{id}'):
        return 0
    cache.set(f'hostpital_project:{id}',1,timeout=3600*24*5)
    try:
        page=0
        con = get_redis_connection('default')
        while 1:
            page+=1
            try:
                url=f'https://m.soyoung.com/hospital/product?hospital_id={id}&page={page}&limit=20&menu1_id=&uid=&is_home=0'
                session=createsession()
                #time.sleep(0.01)
                ret=session.get(url).json()
                obj=DotMap(ret)
                model=Hospital.objects.get(HospitalID=id)
                model.ProjectNum=obj.data.total
                model.save(update_fields=['ProjectNum'])
                for item in obj.data.list:
                    try:
                        con.zadd('product_list',{item['pid']:int(time.time())})
                    except Exception as e:
                        pass
                if not obj.data.has_more:
                    break

            except Exception as e:
                print(e)
                break
    except Exception as e:
        print(e)

def checkhospitaldiary(id):
    now = str(datetime.datetime.now())
    if cache.get(f'hostpital_diary:{id}'):
        return 0
    cache.set(f'hostpital_diary:{id}',1,timeout=3600*24*5)
    try:
        model = Hospital.objects.get(HospitalID=id)
        try:
            url='https://m.soyoung.com/collection/getDetail?is_ajax=1'
            session=createsession()
            ret=session.get(url,data=f'collection_id={id}&range=20&order_type=2&page=0').json()
            model.MGCNum=ret['collection_info']['diary_cnt']
        except Exception as e:
            print(e)
        page=-1
        con = get_redis_connection('default')

        while 1:
            page+=1
            try:
                url=f'https://m.soyoung.com/hospital/postComment?index={page}&range=10&review_tag_id=&tag_id=0&tag_type=all&hospital_id={id}&menu_id=&official_post=0&uid=&is_home=0&menu1_id='
                session=createsession()
                #time.sleep(0.01)
                ret=session.get(url).json()
                obj=DotMap(ret)

                model.HReviewNum=obj.data.total

                model.HHQReviewNum=0 #????????????
                for item in obj.data.base_review_tag_list:
                    if item.name=='??????':
                        model.HNegReviewNum=item.cnt
                    elif item.name=='??????':
                        model.HAddReviewNum=item.cnt
                    elif item.name == '??????':
                        model.HImageReviewNum=item.cnt
                    elif item.name == '?????????':
                        model.HVideoReviewNum=item.cnt
                    elif item.name == '???????????????':
                        model.HPostReviewNum=item.cnt
                model.save(update_fields=['HReviewNum','HNegReviewNum','HAddReviewNum','HImageReviewNum','HVideoReviewNum','HPostReviewNum','MGCNum'])
                try:
                   for item in obj.data.list:
                       con.zadd('diary_list',{item['post_id']:int(time.time())})
                       con.zadd('user_list',{item['uid']:int(time.time())})
                except Exception as e:
                    print(e)
                if not obj.data.has_more:
                    break


            except Exception as e:
                print(e)
                break
    except Exception as e:
        print(e)
import requests
def checkdoctorxiangmu(did):
    if int(did)==0:
        return 0
    if 1 and cache.get(f'dp:{did}'):
        return 0
    cache.set(f'dp:{did}',1,timeout=3600*24*5)
    now = str(datetime.datetime.now())
    try:
        url='https://m.soyoung.com/doctor/infov3tabproduct'
        print(url)
        session=createsession()
        session.headers.update({'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Mobile Safari/537.36',
                                'x-requested-with': 'XMLHttpRequest',
                                'sec-ch-ua-platform': '"Android"',
                                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                })
        page=0
        model = Doctor.objects.filter(DoctorID=did).first()

        if not model:
            model = Doctor()
            model.DoctorID = did
        while 1:
            page+=1
            ret=session.post(url,data=f'doctor_id={did}&index={page}').json()
            obj=DotMap(ret)

            # try:
            #     for item in obj.list:
            #         try:
            #             con.zadd('product_list',item['pid'])
            #         except Exception as e:
            #             pass
            #         try:
            #             p=Product.objects.filter(ProductID=item['pid']).first()
            #             if not p:
            #                 p=Product()
            #                 p.ProductID=item['pid']
            #             p.title=item['title']
            #             p.ReturnRatio=item['over_30day']
            #             p.HospitalName=item['hospital_name']
            #             p.HospitalID_id=item['hospital_id']
            #             p.save()
            #         except Exception as e:
            #             print(e)
            # except Exception as e:
            #     print(e)

            model.DoctorProjectNum=obj.total
            model.DoctorSales=obj.order_cnt
            try:
                model.save()
            except Exception as e:
                print(e)
            break
    except Exception as e:
        print(e)
def checkdoctordiary(did):
    if int(did==0):
        return 0
    if 1 and cache.get(f'dictor_diary:{did}'):
        return 0
    cache.set(f'dictor_diary:{did}',1,timeout=3600*24*5)
    model=Doctor.objects.get(DoctorID=did)
    con = get_redis_connection('default')
    try:
        page=0
        url=f'https://m.soyoung.com/doctor/InfoV4TabDiary?index={page}&range=10&review_tag_id=&tag_id=0&tag_type=all&doctor_id={did}'
        print(url)
        session=createsession()
        ret=session.get(url).json()
        obj=DotMap(ret)
        model.DReviewNum = obj.total
        for item in obj.base_review_tag_list:
            if item.name=='??????':
                model.DAddNum =item.cnt
            elif item.name=='??????':
                model.DNegReviewNum =item.cnt
            elif item.name=='??????':
                model.DImageReviewNum =item.cnt
            elif item.name=='?????????':
                model.DVideoReviewNum =item.cnt
            elif item.name=='???????????????':
                model.DPostReviewNum =item.cnt
        model.save()
        for item in obj.list:
            try:
                con.zadd('diary_list',{item['post_id']:int(time.time())})
                con.zadd('user_list',{item['uid']:int(time.time())})
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)








def checkdoctor(did):
    if int(did)==0:
        return 0
    if 1 and cache.get(f'doctor:{did}'):
        return 0
    cache.set(f'doctor:{did}',1,timeout=3600*24*5)
    now = str(datetime.datetime.now())
    try:
        url=f'https://www.soyoung.com/doctor/{did}/'
        session=createsession()
        ret=session.get(url)
        #session.post('https://m.soyoung.com/doctor/infov3tabproduct')
        b=js2py.eval_js(re.findall(r'(window\.__NUXT__.*?)</script>',ret.text)[0])
        key=re.findall(r'class="main".*data-fetch-key="(.*?)" class="doctor-home',ret.text)[0]
        #soup=BeautifulSoup(ret.text)
        model=Doctor.objects.filter(DoctorID=did).first()
        if not model:
            model=Doctor()
            model.DoctorID=did
        model.DCrawlDate=now
        model.DoctorName=b.fetch[key].info.doctor.name_cn
        model.DoctorCity=b.fetch[key].info.doctor.hospital_city
        model.ProfessionalTitle=b.fetch[key].info.doctor.extend.positionName
        model.WorkYear=b.fetch[key].info.doctor.career
        try:
            model.HospitalID_id=b.fetch[key].info.doctor.main_hospital[0].hospital_id
            model.HospitalName=b.fetch[key].info.doctor.main_hospital[0].hospital_name

        except Exception as e:
            print(e)

        model.DoctorGender=b.fetch[key].info.doctor.gender
        model.DoctorRating=b.fetch[key].info.doctor_card.five_stars_score.satisfy
        try:
            model.DGCNum=int(b.fetch[key].info.statistics.official_cnt)
        except Exception as e:
            pass
        model.ExpertArea='#'.join([item['name'] for item in b.fetch[key].info.doctor.extend.expert_all])
        model.DoctorBio=b.fetch[key].info.doctor.intro
        model.DoctorSRating=b.fetch[key].info.doctor_card.five_stars_score.service
        model.DoctorPRating=b.fetch[key].info.doctor_card.five_stars_score.specialty
        model.DoctorTRating=b.fetch[key].info.doctor_card.five_stars_score.effect
        model.DoctorReviewNum=b.fetch[key].info.statistics.diary_cnt
        model.DoctorFollower=b.fetch[key].info.statistics.fans_cnt
        model.DoctorPosrate=b.fetch[key].info.koubeiAndDiary.avg_info.high_percent
        for tmp in b.fetch[key].info.face_consultation_card.list:
            if 'allow_yn' in tmp and tmp['allow_yn']:
                if tmp['type']==2:
                    model.VideoService=True
                    model.VideoPrice=tmp['price_str']
                elif tmp['type']==3:
                    model.VoiceService=True
                    model.VoicePrice=tmp['price_str']
                elif tmp['type']==1:
                    model.TextService=True
                    model.TextPrice=tmp['price_str']

        model.DoctorConsultation=b.fetch[key].info.statistics.patient_cnt
        model.save()
        checkdoctordiary(did)
        checkdoctorxiangmu(did)



    except Exception as e:
        print(e)

def checkuser(uid):
    if int(uid)==0:
        return 0
    if 1 and cache.get(f'u:{uid}'):
        print('has get!')
        return 0
    cache.set(f'u:{uid}',1,timeout=3600*24*7)
    page = 0
    con = get_redis_connection('default')

    try:
        model = Reviewer.objects.filter(ReviewerID=uid).first()
        if not model:
            model = Reviewer()
            model.ReviewerID =uid
        session=createsession()
        print(f'https://m.soyoung.com/home/userhome?uid={uid}')
        ret=session.get(f'https://m.soyoung.com/home/userhome?uid={uid}')

        soup=BeautifulSoup(ret.text,features="html.parser")
        try:
            model.ReviewerLikes2==tmp[0] if (tmp:=re.findall(r'??????(\d+)',ret.text)) else 0
            model.ReviewerLikes=soup.select('div.zan span.em')[0].string
            model.ReviewerPosts=tmp[0] if (tmp:=re.findall(r'??????(\d+)',ret.text)) else 0
            model.RCrawlDate=datetime.datetime.now()
        except Exception as e:
            print(e)
    except Exception as e:
        print(e,644)
        pass
    while 1:
        page += 1
        #time.sleep(0.01)
        session = createsession()
        try:
        #if 1:
            # url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
            url = f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&type=1'
            print(url)

            ret = session.get(url).json()
            if 'data' in ret and 'redirect' in ret['data']:
                if (tmp:=re.findall(r'd(\d+)',ret['data']['redirect'])):
                    con.zadd('doctor_list',{tmp[0]:int(time.time())})
                return 0

            try:
                model.ReviewerAge=None if int(ret['data']['info']['age'])>=18 else ret['data']['info']['age']
            except Exception as e:
                pass
            try:
                model.ReviewerCity=ret['data']['info']['city_name']
            except Exception as e:
                pass
            model.ReviewerGender='???' if int(ret['data']['info']['gender'])==0 else '???'
            obj=DotMap(ret)
            model.ReviewerFollwer=obj.data.info.type_total.fans_total
            model.ReviewerFollowee=obj.data.info.type_total.follow_total
            model.save()
            #print('len:',obj.data.person_post.responseData.post_list.list)
            if len(obj.data.person_post.responseData.post_list.list)==0:
                break
            for item in obj.data.person_post.responseData.post_list.list:
                con.zadd('diary_list',{item['post_id']:int(time.time())})

        except Exception as e:
            print(e,681)
            break
    try:

        checkuserfans(uid)
    except Exception as e:
        print(e,687)
    try:
        checkuserflow(uid)

    except Exception as e:
        print(e,692)
    return 1
def checkuserfans(uid):
    if int(uid)==0:
        return 0
    if cache.get(f'ufans:{uid}'):
        return 0
    cache.set(f'ufans:{uid}',1,timeout=3600*24*7)
    page = 0
    con = get_redis_connection('default')
    while 1:
        page += 1
        #time.sleep(0.01)
        session = createsession()
        try:
        #if 1:
            # url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
            url = f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&type=1'
            url=f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&flag=2'
            print(url)

            ret = session.get(url).json()
            if 'data' in ret and 'redirect' in ret['data']:
                if (tmp:=re.findall(r'd(\d+)',ret['data']['redirect'])):
                    con.zadd('doctor_list',{tmp[0]:int(time.time())})
                return 0
            obj=DotMap(ret)

            #print('len:',obj.data.person_post.responseData.post_list.list)
            if not obj.data.person_fans.responseData.user_info or len(obj.data.person_fans.responseData.user_info)==0:
                return 0
            for item in obj.data.person_fans.responseData.user_info:

                con.zadd('user_list',{item['uid']:int(time.time())})
        except Exception as e:
            print(e)
            break

def checkuserflow(uid):
    if int(uid)==0:
        return 0
    if 1 and cache.get(f'uflow:{uid}'):
        return 0
    cache.set(f'uflow:{uid}',1,timeout=3600*24*7)
    page = 0
    con = get_redis_connection('default')
    while 1:
        page += 1
        #time.sleep(0.01)
        session = createsession()
        try:
        #if 1:
            # url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
            url = f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&type=1'
            url=f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&flag=1'
            print(url)

            ret = session.get(url).json()

            if 'data' in ret and 'redirect' in ret['data']:
                if (tmp:=re.findall(r'd(\d+)',ret['data']['redirect'])):
                    con.zadd('doctor_list',{tmp[0]:int(time.time())})
                return 0
            obj=DotMap(ret)

            #print('len:',obj.data.person_post.responseData.post_list.list)
            if not obj.data.person_fans.responseData.user_info or len(obj.data.person_fans.responseData.user_info)==0:
                return 0
            for item in obj.data.person_fans.responseData.user_info:
                con.zadd('user_list',{item['uid']:int(time.time())})
        except Exception as e:
            print(e)
            break

if __name__=='__main__':
    checkdoctor('54090')