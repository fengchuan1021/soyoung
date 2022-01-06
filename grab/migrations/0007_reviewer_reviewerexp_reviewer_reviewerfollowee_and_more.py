# Generated by Django 4.0.1 on 2022-01-05 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grab', '0006_alter_hospital_recodeyear'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewer',
            name='ReviewerExp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reviewer',
            name='ReviewerFollowee',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reviewer',
            name='ReviewerLevel',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('DoctorID', models.BigIntegerField(primary_key=True, serialize=False)),
                ('DCrawlDate', models.DateTimeField()),
                ('DoctorName', models.CharField(max_length=32)),
                ('ProfessionalTitle', models.CharField(max_length=32)),
                ('DoctorCity', models.CharField(max_length=32)),
                ('WorkYear', models.IntegerField(default=0)),
                ('HospitalName', models.CharField(max_length=64)),
                ('DoctorGender', models.CharField(max_length=1)),
                ('DoctorRating', models.FloatField(default=0)),
                ('DoctorConsultation', models.IntegerField(default=0)),
                ('DGCNum', models.IntegerField(default=0)),
                ('ExpertArea', models.CharField(default='', max_length=255)),
                ('DoctorBio', models.TextField(default='')),
                ('DoctorSRating', models.FloatField(default=0)),
                ('DoctorPRating', models.FloatField(default=0)),
                ('DoctorTRating', models.FloatField(default=0)),
                ('DoctorReviewNum', models.IntegerField(default=0)),
                ('DoctorFollower', models.IntegerField(default=0)),
                ('DoctorPosrate', models.FloatField(default=0)),
                ('VideoService', models.BooleanField(blank=True, null=True)),
                ('VideoPrice', models.FloatField(default=0)),
                ('TextService', models.BooleanField(blank=True, null=True)),
                ('TextPrice', models.FloatField(default=0)),
                ('DoctorProjectNum', models.IntegerField(default=0)),
                ('DoctorSales', models.IntegerField(default=0)),
                ('DReviewNum', models.IntegerField(default=0)),
                ('DAddNum', models.IntegerField(default=0)),
                ('DNegReviewNum', models.IntegerField(default=0)),
                ('DImageReviewNum', models.IntegerField(default=0)),
                ('DVideoReviewNum', models.IntegerField(default=0)),
                ('DPostReviewNum', models.IntegerField(default=0)),
                ('HospitalID', models.ForeignKey(db_column='HospitalID', on_delete=django.db.models.deletion.DO_NOTHING, to='grab.hospital')),
            ],
        ),
        migrations.CreateModel(
            name='Case',
            fields=[
                ('CaseID', models.BigIntegerField(primary_key=True, serialize=False)),
                ('CCrawlDate', models.DateTimeField()),
                ('DoctorName', models.CharField(max_length=32)),
                ('CaseDate', models.DateTimeField()),
                ('IsImageCase', models.BooleanField(blank=True, null=True)),
                ('IsVedioCase', models.BooleanField(blank=True, null=True)),
                ('CaseLikes', models.IntegerField(default=0)),
                ('CaseFollow', models.IntegerField(default=0)),
                ('CaseReply', models.IntegerField(default=0)),
                ('CaseText', models.TextField(default='')),
                ('CaseImage', models.TextField(default='')),
                ('CaseVideo', models.TextField(default='')),
                ('DoctorID', models.ForeignKey(db_column='DoctorID', on_delete=django.db.models.deletion.DO_NOTHING, to='grab.doctor')),
            ],
        ),
    ]
