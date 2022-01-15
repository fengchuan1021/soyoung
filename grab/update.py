import django
import os
import pathlib
from grab.createsession import createsession
import sys
import datetime, time
import psutil
from django.db import connection

if __name__ == "__main__":
    basedir = str(pathlib.Path(__file__).resolve().parent.parent)
    os.chdir(basedir)
    sys.path.append(basedir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'soyoung.settings'
    django.setup()
from grab.models import Product, Hospital, Doctor,Diary,Reviewer
from django.conf import settings
def updatedb():

    with connection.cursor() as cur:
        sql = 'update grab_hospital a join (select HospitalID,count(HospitalID) as n from grab_diary where IsHQReview=1 GROUP BY HospitalID ) b on a.HospitalID=b.HospitalID set a.HHQReviewNum=b.n'
        cur.execute(sql)
        cur.execute('update (select  min(ReviewDate) as ReviewDate,ProductID from  grab_diary where !ISNULL(ProductID) GROUP BY ProductID) a join grab_product b on a.ProductID =b.ProductID  set b.PFirstCommentTime=a.ReviewDate')
        cur.execute('update (select  ROUND(AVG(ReviewRating),1) as avgscore,ProductID from  grab_diary where !ISNULL(ProductID) GROUP BY ProductID) a join grab_product b on a.ProductID =b.ProductID  set b.PAverageScore=a.avgscore')
