from django.db import models
import random
from django.urls import reverse
from django.utils import timezone
import time
from django.contrib.auth.models import AbstractUser
from django.utils.dateparse import parse_datetime


# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=70, null=False, blank=False)
    history = models.TextField(max_length=1000, null=True, blank=True, default='No History')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("hrms:dept_detail", kwargs={"pk": self.pk})


class Employee(models.Model):
    LANGUAGE = (('english', 'ENGLISH'), ('yoruba', 'YORUBA'), ('hausa', 'HAUSA'), ('french', 'FRENCH'))
    GENDER = (('male', 'MALE'), ('female', 'FEMALE'), ('other', 'OTHER'))
    emp_id = models.CharField(max_length=70, default='emp' + str(random.randrange(100, 999, 1)))
    thumb = models.ImageField(blank=True, null=True)
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(max_length=125, null=False)
    address = models.TextField(max_length=100, default='')
    emergency = models.CharField(max_length=11)
    gender = models.CharField(choices=GENDER, max_length=10)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    joined = models.DateTimeField(default=timezone.now)
    language = models.CharField(choices=LANGUAGE, max_length=10, default='english')
    number = models.CharField(max_length=10, default='0123456789')
    bank = models.CharField(max_length=25, default='Santander UK')
    salary = models.CharField(max_length=16, default='00,000.00')

    def __str__(self):
        return self.first_name

    def get_absolute_url(self):
        return reverse("hrms:employee_view", kwargs={"pk": self.pk})


class User(AbstractUser):
    thumb = models.ImageField()


class Attendance(models.Model):
    STATUS = (('PRESENT', 'PRESENT'), ('ABSENT', 'ABSENT'), ('UNAVAILABLE', 'UNAVAILABLE'))
    date = models.DateField(auto_now_add=True)
    first_in = models.TimeField()
    last_out = models.TimeField(null=True)
    status = models.CharField(choices=STATUS, max_length=15)
    staff = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.first_in = timezone.localtime()
        super(Attendance, self).save(*args, **kwargs)

    def __str__(self):
        return 'Attendance -> ' + str(self.date) + ' -> ' + str(self.staff)


class Leave(models.Model):
    STATUS = (('approved', 'APPROVED'), ('unapproved', 'UNAPPROVED'), ('decline', 'DECLINED'))
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    start = models.CharField(blank=False, max_length=15)
    end = models.CharField(blank=False, max_length=15)
    status = models.CharField(choices=STATUS, default='Not Approved', max_length=15)




class LeaveApplication(models.Model):
    name = models.CharField(max_length=25)
    email = models.EmailField()
    apply_date = models.DateField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()
    no_of_days = models.IntegerField(default=1)
    hr_status = models.CharField(max_length=15, default="Pending")
    hr_comment = models.TextField(blank=True, null=True, default="None")


class Recruitment(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    position = models.CharField(max_length=40)
    email = models.EmailField(max_length=25)
    phone = models.CharField(max_length=11)

    def __str__(self):
        return self.first_name + ' - ' + self.position


def is_duration_valid(start_time, end_time):
    start_time_obj = parse_datetime(start_time)
    end_time_obj = parse_datetime(end_time)
    return end_time_obj > start_time_obj


def get_overtime_application_hours(start_time, end_time) -> int:
    difference = end_time - start_time
    hours = difference.seconds / 3600
    return hours


class OvertimeApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Rejected', 'Rejected'),
        ('Approved', 'Approved'),
        ('Expired', 'Expired'),
    ]

    status = models.CharField(max_length=10, default="Pending", choices=STATUS_CHOICES)
    date = models.DateField(auto_now=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField()
    supervisor_approval = models.CharField(max_length=10, default="Pending")
    HOD_approval = models.CharField(max_length=10, default="Pending")
    HR_approval = models.CharField(max_length=10, default="Pending")
    cfo_approval = models.CharField(max_length=10, default="Pending")
    ceo_approval = models.CharField(max_length=10, default="Pending")
    expired = models.BooleanField(default=False)
    applicant = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='supervisor', blank=True)

    def __str__(self):
        return "{}'s holiday {} {}".format(self.applicant.first_name, self.start_time, self.end_time)

    @property
    def number_of_hours(self):
        hours = get_overtime_application_hours(self.start_time, self.end_time)
        return round(hours, 2)

    @property
    def is_on_sunday(self):
        """Bug: end_time datetime object converts to the day before if datetime is between midnignt and 6 a.m"""
        return self.end_time.weekday() == 6

    @property
    def is_on_holiday(self):
        """Bug: end_time datetime object converts to the day before if datetime is between midnignt and 6 a.m"""
        return is_on_holiday(self.end_time)

    @property
    def date_of_work(self):
        """Bug: end_time datetime object converts to the day before if datetime is between midnignt and 6 a.m"""
        return self.end_time.date()

    @property
    def overtime_pay(self):
        if self.is_on_holiday or self.is_on_sunday:
            overtime_amount = self.number_of_hours * 2 * self.applicant. \
                overtime_hourly_rate
            return int(overtime_amount)
        else:
            overtime_amount = self.number_of_hours * 1.5 * self.applicant. \
                overtime_hourly_rate
            return int(overtime_amount)


class OvertimePlan(models.Model):
    applicant = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True)
    date = models.DateField(auto_now=True)
    HR_approval = models.CharField(max_length=10, default="Pending")
    cfo_approval = models.CharField(max_length=10, default="Pending")
    status = models.CharField(max_length=10, default="Pending")


class OvertimeSchedule(models.Model):
    overtime_plan = models.ForeignKey(OvertimePlan, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    number_of_hours = models.IntegerField(blank=True)
    description = models.TextField()


class TestCronJob(models.Model):
    task = models.CharField(max_length=20)
    description = models.TextField()
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.task}'


def create_holiday(date, name):
    holiday = Holiday.objects.create(
        date=date,
        name=name
    )

    return holiday


def is_on_holiday(date_time):
    # Check if date is a holiday
    date = date_time.date()
    holiday = Holiday.objects.filter(date=date)

    if holiday:
        return True
    else:
        return False


def get_all_holidays():
    holidays = Holiday.objects.all()
    return holidays


def get_holiday(holiday_id):
    holiday = Holiday.objects.get(pk=holiday_id)
    return holiday


class Holiday(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class JobAdvertisement(models.Model):
    position = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='title')
    education = models.CharField(max_length=20)
    vacancy = models.IntegerField()
    experience = models.IntegerField()
    post_date = models.DateField(auto_now=True)
    description = models.TextField()
    show_salary = models.BooleanField(default=True)
    deadline = models.DateField()

    def __str__(self):
        return self.position.name

    @property
    def number_of_applications(self):
        return self.jobapplication_set.count()


class JobApplication(models.Model):
    job_ad = models.ForeignKey(JobAdvertisement, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    position = models.CharField(max_length=40)
    email = models.EmailField(max_length=25)
    phone = models.CharField(max_length=11)
    cv = models.FileField(upload_to='cvs/')
