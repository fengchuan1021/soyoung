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
        print(ret.url)
        b=js2py.eval_js(re.findall(r'(window\.__NUXT__.*?)</script>',ret.text)[0])
        soup=BeautifulSoup(ret.text,features="html.parser")
        #key=soup.select('.main')[0].attrs['data-fetch-key']
        key=soup.find(lambda x: x.has_attr("data-fetch-key") and not (x.has_attr('class') and 'search-header' in x['class'])).attrs['data-fetch-key']
        print(key)
        print(b.fetch)
        #exit(0)
        model.ProductName=b.fetch[key].productData.title
        model.HospitalID_id=b.fetch[key].productData.product.hospital.id
        model.HospitalName=b.fetch[key].productData.product.hospital.name_cn
        model.HospitalRating=b.fetch[key].productData.product.hospital.satisfy
        model.DoctorNum=tmp[0] if (tmp:=re.findall(r'(\d+)',b.fetch[key].productData.product.hospital.doctor_cnt)) else 0
        model.HospitalAddress=b.fetch[key].productData.product.hospital.address
        model.ProductOPrice=b.fetch[key].productData.product.price_origin
        model.ProductPrice=b.fetch[key].productData.product.price_online
        model.ProductSale=b.fetch[key].productData.product.show_order_cnt
        #退单率
        model.ReturnRatio=0
        if b.fetch[key].productData.product.content.describe_other:
            for item in b.fetch[key].productData.product.content.describe_other:
                if item['name']=='额外费用':
                    model.ProductAPrice=sum([float(i[0]) for tmp in item['list'] if (i:=re.findall(r'([0-9\.]+)',tmp['price']))])
        model.save()
        checkproductdiary(pid)
    except Exception as e:
        print(e)
    return 1
def checkproductdiary(pid):
    now = str(datetime.datetime.now())
    print(11)
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
        print(22)
        model.PReviewNum=obj.total
        for item in obj.base_review_tag_list:
            if item.name=='消费后日记':
                model.PPostReviewNum=int(item.cnt) if item.cnt else 0
            elif item.name=='差评':
                model.PNegReviewNum=int(item.cnt) if item.cnt else 0
            elif item.name=='追评':
                model.PAddReviewNum = int(item.cnt) if item.cnt else 0
            elif item.name=='有图':
                model.PImageReviewNum = int(item.cnt) if item.cnt else 0
            elif item.name == '有视频':
                model.PVideoReviewNum = int(item.cnt) if item.cnt else 0
        print(222222)
        model.save()
        con = get_redis_connection('default')

        for item in obj.list:
            try:
                con.sadd('diary_list', item['post_id'])
                con.sadd('user_list',item['post_user']['uid'])
            except Exception as e:
                print(e)
                pass
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
                model.HospitalResponseText = item['content_new']  # 机构回复
            elif  int(item['certified_type'])!=2 :
                con.sadd('user_list',item['uid'])
        model.save()
        try:
            con = get_redis_connection('default')
            for item in obj.responseData.list:
                con.sadd('user_list',item['uid'])
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

        ret=session.get(f'https://www.soyoung.com/p{pid}')
        print(f'https://www.soyoung.com/p{pid}')
        b = js2py.eval_js(re.findall(r'(window\.__NUXT__.*?)</script>', ret.text)[0])

        model.ReviewContent=b.fetch["data-v-56804bd0:0"].res.content[0].raw_text
        print('why')
        model.ReviewReplyNum=b.fetch["data-v-56804bd0:0"].stat.reply_cnt
        model.ReviewFollowNum=b.fetch["data-v-56804bd0:0"].stat.collection_cnt
        model.ReviewLikeNum = b.fetch["data-v-56804bd0:0"].stat.real_favorite_cnt
        model.RCrawlDate=now
        print(111111111111111111)
        print(b.fetch["data-v-56804bd0:0"].extension)
        if 'extension' in b.fetch["data-v-56804bd0:0"] and  b.fetch["data-v-56804bd0:0"].extension and b.fetch["data-v-56804bd0:0"].extension.display_label_list:
            for item in b.fetch["data-v-56804bd0:0"].extension.display_label_list:
                if item['name']=='通过新氧消费':
                    model.IsCustom1Review=True
                elif item['name']=='上传消费凭证':
                    model.IsCustom2Review = True
                elif item['name'] == '体验官日记':
                    model.IsEOReview = True
                    try:
                        Reviewer.objects.filter(ReviewerID=b.fetch["data-v-56804bd0:0"].post_user.uid).update(IsEOuser=True)
                    except Exception as e:
                        pass
                elif item['name']=='案例':
                    model.IsCase=True

        print('debug1222222222222222222')
        try:
            model.IsVideoReview =False if 'video' not in b.fetch["data-v-56804bd0:0"].media else True
            model.IsImageReview=False if 'content_image_list' not in b.fetch["data-v-56804bd0:0"].media else True
        except Exception as e:
            pass
        #model.ReviewDate=re.findall(r'create_date="(.*?)"',ret.text)[0]
        model.ReviewDate=b.fetch["data-v-56804bd0:0"].base.create_date
        model.ReviewViews=b.fetch["data-v-56804bd0:0"].stat.view_cnt
        print('333333333333')
        print(b.fetch["data-v-56804bd0:0"].star_score)
        if 'star_score' in b.fetch["data-v-56804bd0:0"] and b.fetch["data-v-56804bd0:0"].star_score:
            model.ReviewERating=b.fetch["data-v-56804bd0:0"].star_score.environment
            model.ReviewSRating =b.fetch["data-v-56804bd0:0"].star_score.service
            model.ReviewTRating=b.fetch["data-v-56804bd0:0"].star_score.effect
            model.ReviewPRating=b.fetch["data-v-56804bd0:0"].star_score.specialty
            model.ReviewRating = b.fetch["data-v-56804bd0:0"].star_score.satisfy  # 日记评分

        model.ReviewTextLen=b.fetch["data-v-56804bd0:0"].stat.text_cnt
        model.ReviewImageNum=b.fetch["data-v-56804bd0:0"].stat.image_cnt
        try:
            model.ReviewImage='' if 'content_image_list' not in b.fetch["data-v-56804bd0:0"].media else '#'.join([ item['url'] for item in b.fetch["data-v-56804bd0:0"].media.content_image_list])
            model.ReviewVideo='' if 'video' not in b.fetch["data-v-56804bd0:0"].media else b.fetch["data-v-56804bd0:0"].media.video.url
        except Exception as e:
            pass
        print(99999999)

        model.ReviewAddText='' if ('append' not in b.fetch["data-v-56804bd0:0"] or not b.fetch["data-v-56804bd0:0"].append) else '#'.join([item.content[0].raw_text for item in b.fetch["data-v-56804bd0:0"].append])
        print(8888888)
        model.FollowReviewNum=b.fetch["data-v-56804bd0:0"].res.collect_diary_list.diary_cnt if 'collect_diary_list' in  b.fetch["data-v-56804bd0:0"].res else 0
        model.ReviewerID_id=b.fetch["data-v-56804bd0:0"].post_user.uid
        con = get_redis_connection('default')
        print('debug111111111111111111')
        try:
            if 'collect_diary_list' in b.fetch["data-v-56804bd0:0"].res:
                model.CollectionID=b.fetch["data-v-56804bd0:0"].res.collect_diary_list.collection_id

                for item in b.fetch["data-v-56804bd0:0"].res.collect_diary_list.list:
                    try:
                        con.sadd('diary_list',item['post_id'])
                    except Exception as e:
                        print(e)
                        pass
        except Exception as e:
            pass
        model.ReviewID=pid
        if 'doctor_card' in b.fetch["data-v-56804bd0:0"].attribute:
            model.DoctorID_id=b.fetch["data-v-56804bd0:0"].attribute.doctor_card[0].doctor_id
            model.DoctorName=b.fetch["data-v-56804bd0:0"].attribute.doctor_card[0].name_cn
            con.sadd('doctor_list',model.DoctorID_id)
        if 'hospital_card' in b.fetch["data-v-56804bd0:0"].attribute:
            model.HospitalID_id=b.fetch["data-v-56804bd0:0"].attribute.hospital_card[0].hospital_id
            model.HospitalName=b.fetch["data-v-56804bd0:0"].attribute.hospital_card[0].name_cn
            con.sadd('hospital_list',model.HospitalID_id)
        print('444444')
        if 'product_card' in b.fetch["data-v-56804bd0:0"].attribute:
            model.ProductID_id=b.fetch["data-v-56804bd0:0"].attribute.product_card[0].product.pid
            model.ProductName=b.fetch["data-v-56804bd0:0"].attribute.product_card[0].product.title
            con.sadd('product_list',model.ProductID_id)
        model.IsHQReview=True if b.fetch["data-v-56804bd0:0"].res.audit.quality_type and int(b.fetch["data-v-56804bd0:0"].res.audit.quality_type)==2 else False #优质评价
        print('22211111111')
        # try:
        #     setusercollect_cnt(model.ReviewerID_id,b.fetch["data-v-56804bd0:0"].post_user.favourite_collect_cnt)
        # except Exception as e:
        #     print(e)
        #     pass

        try:
            for item in b.fetch["data-v-56804bd0:0"].recommend:
                if 'type' in item and item['type']==35:
                    con.sadd('diary_list',item['data']['post_id'])
                    con.sadd('user_list',item['data']['uid'])
        except Exception as e:
            print(e)
            print(b.fetch["data-v-56804bd0:0"].recommend)
            pass
        print('beforesave')
        model.save()
        print('aftersave')
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

        model.MGCNum=0#机构动态数量
        try:
            ret=session.get(f'https://m.soyoung.com/hospital/profession?hospital_id={pid}')
            print(ret.text)
            model.APatentNum=tmp[0] if (tmp:=re.findall(r'(\d+)项专利',ret.text)) else 0
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
                time.sleep(5)
                ret=session.get(url).json()
                obj=DotMap(ret)
                model=Hospital.objects.get(HospitalID=id)
                model.ProjectNum=obj.data.total
                model.save(update_fields=['ProjectNum'])
                for item in obj.data.list:
                    try:
                        con.sadd('product_list',item['pid'])
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
                time.sleep(5)
                ret=session.get(url).json()
                obj=DotMap(ret)

                model.HReviewNum=obj.data.total

                model.HHQReviewNum=0 #优质日记
                for item in obj.data.base_review_tag_list:
                    if item.name=='差评':
                        model.HNegReviewNum=item.cnt
                    elif item.name=='追评':
                        model.HAddReviewNum=item.cnt
                    elif item.name == '有图':
                        model.HImageReviewNum=item.cnt
                    elif item.name == '有视频':
                        model.HVideoReviewNum=item.cnt
                    elif item.name == '消费后日记':
                        model.HPostReviewNum=item.cnt
                model.save(update_fields=['HReviewNum','HNegReviewNum','HAddReviewNum','HImageReviewNum','HVideoReviewNum','HPostReviewNum','MGCNum'])
                try:
                   for item in obj.data.list:
                       con.sadd('diary_list',item['post_id'])
                       con.sadd('user_list',item['uid'])
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
            print(ret)
            try:
                for item in obj.list:
                    try:
                        con.sadd('product_list',item['pid'])
                    except Exception as e:
                        pass
                    try:
                        p=Product.objects.filter(ProductID=item['pid']).first()
                        if not p:
                            p=Product()
                            p.ProductID=item['pid']
                        p.title=item['title']
                        p.ReturnRatio=item['over_30day']
                        p.HospitalName=item['hospital_name']
                        p.HospitalID_id=item['hospital_id']
                        p.save()
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

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
            if item.name=='追评':
                model.DAddNum =item.cnt
            elif item.name=='差评':
                model.DNegReviewNum =item.cnt
            elif item.name=='有图':
                model.DImageReviewNum =item.cnt
            elif item.name=='有视频':
                model.DVideoReviewNum =item.cnt
            elif item.name=='消费后日记':
                model.DPostReviewNum =item.cnt
        model.save()
        for item in obj.list:
            try:
                con.sadd('diary_list',item['post_id'])
                con.sadd('user_list',item['uid'])
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
            print(e)
            pass
        model.DoctorGender=b.fetch["data-v-625304e2:0"].info.doctor.gender
        model.DoctorRating=b.fetch["data-v-625304e2:0"].info.doctor_card.five_stars_score.satisfy
        model.DGCNum=b.fetch["data-v-625304e2:0"].info.statistics.official_cnt
        model.ExpertArea='#'.join([item['name'] for item in b.fetch["data-v-625304e2:0"].info.doctor.extend.expert_all])
        model.DoctorBio=b.fetch["data-v-625304e2:0"].info.doctor.intro
        model.DoctorSRating=b.fetch["data-v-625304e2:0"].info.doctor_card.five_stars_score.service
        model.DoctorPRating=b.fetch["data-v-625304e2:0"].info.doctor_card.five_stars_score.specialty
        model.DoctorTRating=b.fetch["data-v-625304e2:0"].info.doctor_card.five_stars_score.effect
        model.DoctorReviewNum=b.fetch["data-v-625304e2:0"].info.statistics.diary_cnt
        model.DoctorFollower=b.fetch["data-v-625304e2:0"].info.statistics.fans_cnt
        model.DoctorPosrate=b.fetch["data-v-625304e2:0"].info.koubeiAndDiary.avg_info.high_percent
        for tmp in b.fetch["data-v-625304e2:0"].info.face_consultation_card.list:
            if 'allow_yn' in tmp and tmp['allow_yn']:
                if tmp['type']==2:
                    model.VideoService=True
                    model.VideoPrice=tmp['price_str']
                elif tmp['type']==3:
                    model.VoiceService=True
                    model.VideoPrice=tmp['price_str']
                elif tmp['type']==1:
                    model.TextService=True
                    model.TextPrice=tmp['price_str']

        model.DoctorConsultation=b.fetch["data-v-625304e2:0"].info.statistics.patient_cnt
        model.save()
        checkdoctordiary(did)
        checkdoctorxiangmu(did)



    except Exception as e:
        print(e)

def checkuser(uid):
    if int(uid)==0:
        return 0
    if 1 and cache.get(f'u:{uid}'):
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
        ret=session.get(f'https://m.soyoung.com/home/userhome?uid={uid}')
        soup=BeautifulSoup(ret.text,features="html.parser")
        try:
            model.ReviewerLikes2==tmp[0] if (tmp:=re.findall(r'喜欢(\d+)',ret.text)) else 0
            model.ReviewerLikes=soup.select('div.zan span.em')[0].string
            model.ReviewerPosts=tmp[0] if (tmp:=re.findall(r'动态(\d+)',ret.text)) else 0
            print('psot:',model.ReviewerPosts)
        except Exception as e:
            print(e)
    except Exception as e:
        pass
    while 1:
        page += 1
        time.sleep(5)
        session = createsession()
        try:
        #if 1:
            # url=f'https://m.soyoung.com/y/hospital/{model.HospitalID}/'
            url = f'https://www.soyoung.com/home/person?_json=1&page={page}&is_new=1&uid={uid}&type=1'
            print(url)

            ret = session.get(url).json()
            if 'data' in ret and 'redirect' in ret['data']:
                if (tmp:=re.findall(r'd(\d+)',ret['data']['redirect'])):
                    con.sadd('doctor_list',tmp[0])
                return 0

            try:
                model.ReviewerAge=None if int(ret['data']['info']['age'])>=18 else ret['data']['info']['age']
            except Exception as e:
                pass
            try:
                model.ReviewerCity=ret['data']['info']['city_name']
            except Exception as e:
                pass
            model.ReviewerGender='女' if int(ret['data']['info']['gender'])==0 else '男'
            obj=DotMap(ret)
            model.ReviewerFollwer=obj.data.info.type_total.fans_total
            model.ReviewerFollowee=obj.data.info.type_total.follow_total
            model.save()
            #print('len:',obj.data.person_post.responseData.post_list.list)
            if len(obj.data.person_post.responseData.post_list.list)==0:
                break
            for item in obj.data.person_post.responseData.post_list.list:
                con.sadd('diary_list',item['post_id'])

        except Exception as e:
            print(e)
            break
    try:

        checkuserfans(uid)
    except Exception as e:
        print(e)
    try:
        checkuserflow(uid)

    except Exception as e:
        print(e)
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
        time.sleep( 5)
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
                    con.sadd('doctor_list',tmp[0])
                return 0
            obj=DotMap(ret)

            #print('len:',obj.data.person_post.responseData.post_list.list)
            if not obj.data.person_fans.responseData.user_info or len(obj.data.person_fans.responseData.user_info)==0:
                return 0
            for item in obj.data.person_fans.responseData.user_info:
                print('add',item['uid'])
                con.sadd('user_list',item['uid'])
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
        time.sleep( 5)
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
                    con.sadd('doctor_list',tmp[0])
                return 0
            obj=DotMap(ret)

            #print('len:',obj.data.person_post.responseData.post_list.list)
            if not obj.data.person_fans.responseData.user_info or len(obj.data.person_fans.responseData.user_info)==0:
                return 0
            for item in obj.data.person_fans.responseData.user_info:
                con.sadd('user_list',item['uid'])
        except Exception as e:
            print(e)
            break

