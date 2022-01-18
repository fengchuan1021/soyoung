from django.db import models

# Create your models here.
class Hospital(models.Model):
    HospitalID=models.BigIntegerField(primary_key=True)
    CrawlTime=models.DateTimeField(blank=True,null=True)

    HospitalName=models.CharField(max_length=64)

    ServiceNum=models.IntegerField(default=0,db_index=True)
    DoctorNum=models.IntegerField(default=0)
    HospitalAddress=models.CharField(max_length=512,default='')
    HospitalType=models.CharField(default='',blank=True,null=True,max_length=32)
    ReviewNum=models.IntegerField(default=0)
    DoctorNum=models.IntegerField(default=0)
    HospitalCity=models.CharField(max_length=32,default='')
    ReputNum=models.IntegerField(default=0)
    Reputation=models.CharField(default='',max_length=1024)
    RecodeYear=models.CharField(blank=True,null=True,default='',max_length=32)
    APatentNum=models.IntegerField(default=0)
    HospitalRating=models.FloatField(default=0)
    HospitalURating=models.FloatField(default=0)
    HospitalTRating = models.FloatField(default=0)
    HospitalSRating= models.FloatField(default=0)
    HospitalFollower=models.CharField(default='',max_length=32)
    ProjectNum=models.IntegerField(default=0)
    MGCNum=models.IntegerField(default=0)
    HReviewNum=models.IntegerField(default=0)
    HNegReviewNum=models.IntegerField(default=0)
    HAddReviewNum=models.IntegerField(default=0)
    HHQReviewNum=models.IntegerField(default=0)
    HImageReviewNum=models.IntegerField(default=0)
    HVideoReviewNum=models.IntegerField(default=0)
    HPostReviewNum=models.IntegerField(default=0)

class Product(models.Model):
    ProductID=models.BigIntegerField(primary_key=True)
    PCrawlDate=models.DateTimeField(blank=True,null=True)
    ProductName=models.CharField(max_length=128)

    HospitalID=models.ForeignKey(to=Hospital,db_column='HospitalID',on_delete=models.DO_NOTHING,db_index=True)
    HospitalName = models.CharField(max_length=64, default='')
    HospitalRating=models.FloatField(default=0)
    DoctorNum=models.IntegerField(default=0)
    HospitalAddress=models.CharField(max_length=512,default='')

    ProductOPrice=models.FloatField(default=0)
    ProductPrice=models.FloatField(default=0)
    ProductSale=models.IntegerField(default=0)
    ReturnRatio=models.FloatField(default=0)
    ProductAPrice=models.FloatField(default=0)

    PReviewNum=models.IntegerField(default=0)
    PPostReviewNum=models.IntegerField(default=0)
    PNegReviewNum=models.IntegerField(default=0)
    PAddReviewNum=models.IntegerField(default=0)
    PImageReviewNum=models.IntegerField(default=0)
    PVideoReviewNum=models.IntegerField(default=0)

    PFirstCommentTime=models.DateTimeField(blank=True,null=True)
    PAverageScore=models.FloatField(default=0)
class Reviewer(models.Model):
    ReviewerID=models.BigIntegerField(primary_key=True)
    ReviewerName=models.CharField(max_length=32)
    ReviewerAge=models.IntegerField(blank=True,null=True)
    ReviewerGender=models.CharField(blank=True,null=True,max_length=1)
    ReviewerCity=models.CharField(max_length=32)
    ReviewerPosts=models.IntegerField(default=0)
    ReviewerFollwer=models.IntegerField(default=0)
    ReviewerLikes=models.IntegerField(default=0)
    ReviewerFollowee=models.IntegerField(default=0)
    ReviewerExp=models.IntegerField(default=0)
    ReviewerLevel=models.IntegerField(default=0)
    ReviewerLikes2=models.IntegerField(default=0)
    IsEOuser=models.BooleanField(default=False)
    UserType=models.CharField(max_length=2,default='用户')
class Diary(models.Model):
    ReviewID=models.BigIntegerField(primary_key=True)
    RCrawlDate = models.DateTimeField(blank=True, null=True)
    IsCustom1Review=models.BooleanField(blank=True,null=True,default=False)
    IsCustom2Review = models.BooleanField(blank=True, null=True,default=False)
    IsHQReview = models.BooleanField(blank=True, null=True,db_index=True)
    IsEOReview= models.BooleanField(blank=True, null=True,default=False)
    IsImageReview= models.BooleanField(blank=True, null=True,default=False)
    IsVideoReview = models.BooleanField(blank=True, null=True,default=False)
    ReviewDate=models.DateTimeField(db_index=True)
    ReviewViews=models.IntegerField(default=0)
    ReviewRating=models.FloatField(default=0,db_index=True)
    ReviewERating=models.FloatField(default=0)
    ReviewSRating = models.FloatField(default=0)
    ReviewTRating = models.FloatField(default=0)
    ReviewPRating = models.FloatField(default=0)
    ReviewImageNum=models.IntegerField(default=0)
    ReviewContent=models.TextField(default='',blank=True,null=True)
    ReviewTextLen=models.IntegerField(default=0)
    ReviewLikeNum=models.IntegerField(default=0)
    ReviewFollowNum=models.IntegerField(default=0)
    ReviewReplyNum=models.IntegerField(default=0)
    ReviewerID=models.ForeignKey(to=Reviewer,db_column='ReviewerID',on_delete=models.DO_NOTHING,blank=True,null=True)
    ReviewImage=models.TextField(default='',blank=True)
    ReviewVideo=models.TextField(default='',blank=True)
    IsCase=models.BooleanField(default=False,blank=True,null=True)
    FollowReviewNum=models.IntegerField(default=0)
    CollectionID=models.BigIntegerField(blank=True,null=True)
    ReviewAddText=models.CharField(default='',max_length=1024)
    ProductID=models.ForeignKey(to=Product,db_column='ProductID',on_delete=models.DO_NOTHING,blank=True,null=True,db_index=True)
    ProductName=models.CharField(default='',max_length=64)
    DoctorID=models.ForeignKey(to='Doctor',db_column='DoctorID',on_delete=models.DO_NOTHING,blank=True,null=True)
    DoctorName=models.CharField(default='',max_length=128)

    HospitalID=models.ForeignKey(to='Hospital',db_column='HospitalID',on_delete=models.DO_NOTHING,blank=True,null=True,db_index=True)
    HospitalName=models.CharField(default='',max_length=128)

class Doctor(models.Model):
    DoctorID=models.BigIntegerField(primary_key=True)
    DCrawlDate=models.DateTimeField(blank=True,null=True)
    DoctorName=models.CharField(max_length=32)
    ProfessionalTitle=models.CharField(max_length=32)
    DoctorCity=models.CharField(max_length=32)
    WorkYear=models.IntegerField(default=0)
    HospitalID=models.ForeignKey(to=Hospital,db_column='HospitalID',on_delete=models.DO_NOTHING,blank=True,null=True,db_index=True)
    HospitalName=models.CharField(max_length=64)
    DoctorGender=models.CharField(max_length=1)
    DoctorRating=models.FloatField(default=0)
    DoctorConsultation=models.IntegerField(default=0)
    DGCNum=models.IntegerField(default=0)
    ExpertArea=models.CharField(max_length=255,default='')
    DoctorBio=models.TextField(default='')
    DoctorSRating=models.FloatField(default=0)
    DoctorPRating = models.FloatField(default=0)
    DoctorTRating = models.FloatField(default=0)

    DoctorReviewNum=models.IntegerField(default=0)
    DoctorFollower=models.IntegerField(default=0)
    DoctorPosrate=models.FloatField(default=0)
    VideoService=models.BooleanField(blank=True,null=True)
    VideoPrice=models.CharField(default='',max_length=32)
    TextService=models.BooleanField(blank=True,null=True)
    TextPrice=models.CharField(default='',max_length=32)
    DoctorProjectNum=models.IntegerField(default=0)
    DoctorSales=models.IntegerField(default=0)
    VoiceService=models.BooleanField(default=0)
    VoicePrice= models.CharField(default='', max_length=32)
    DReviewNum=models.IntegerField(default=0)
    DAddNum=models.IntegerField(default=0)
    DNegReviewNum=models.IntegerField(default=0)
    DImageReviewNum=models.IntegerField(default=0)
    DVideoReviewNum=models.IntegerField(default=0)
    DPostReviewNum=models.IntegerField(default=0)

class Case(models.Model):
    CaseID=models.BigIntegerField(primary_key=True)
    CCrawlDate=models.DateTimeField()
    DoctorID=models.ForeignKey(to=Doctor,on_delete=models.DO_NOTHING,db_column='DoctorID')
    DoctorName=models.CharField(max_length=32)
    CaseDate=models.DateTimeField()
    IsImageCase=models.BooleanField(blank=True,null=True)
    IsVedioCase = models.BooleanField(blank=True, null=True)
    CaseImage=models.IntegerField(default=0)
    CaseLikes = models.IntegerField(default=0)
    CaseFollow = models.IntegerField(default=0)
    CaseReply = models.IntegerField(default=0)
    CaseText=models.TextField(default='')

    CaseImage=models.TextField(default='')
    CaseVideo=models.TextField(default='')
