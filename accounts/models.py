import traceback
from django.db import models
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels
from django_resized import ResizedImageField
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from uuid import uuid4
import os
from django.contrib.contenttypes.models import ContentType


# Create your models here.
def path_and_rename(instance, filename):
    upload_to = 'complex'
    ext = filename.split('.')[-1]  
    filename = '{}.{}'.format(uuid4().hex, ext)
    return os.path.join(upload_to, filename)


def get_default_complex_rate():
    return dict(rate=0, rateCount=0)

def get_default_worker_permission():
    return ['menu']

class customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='customer')
    birthDate = jmodels.jDateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phoneNumber = models.CharField(max_length=14)
    acceptedRules = models.BooleanField(default=False)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    update_at = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ آخرین آپدیت")
    
    def __str__(self):
        return str(self.user.first_name) + " "+str (self.user.last_name)

class worker(models.Model):
    complex= models.ForeignKey("complex", on_delete=models.CASCADE, verbose_name='محل کار', null=True, blank=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='worker')
    phoneNumber = models.CharField(max_length=14)
    roleName = models.CharField(verbose_name='وظیفه', max_length=255, null=True, blank=True)
    permission = models.JSONField(verbose_name='دسترسی ها', blank=True, null=True, default = get_default_worker_permission)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    update_at = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ آخرین آپدیت")

    def __str__(self):
        return str(self.user.first_name) + " "+str(self.user.last_name)

class complex(models.Model):
    #TODO update documentation for bank
    owner = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    merchant_code = models.CharField(max_length=36)
    # bankName = models.CharField(max_length=255, verbose_name="بانک", default="ملی")
    # shabaNumber = models.CharField(max_length=300, verbose_name='شماره شبا', default='1234567789')

    states =((0,"Isfahan"),)
    citys = ((0,"Isfahan"),)

    state = models.IntegerField(choices=states,default=0)
    city = models.IntegerField(choices=citys,default=0)
    neighborhood = models.TextField()

    dark_mode = models.BooleanField(default=False, verbose_name="نمایش دارک منو")
    customer_ordering = models.BooleanField(default=True, verbose_name="ثبت سفارش سمت مشتری")
    address = models.TextField()
    telephone = models.CharField(max_length=11)

    logo = models.ImageField(null= True, upload_to=path_and_rename)
    logo_tumbnail =  ResizedImageField(size=[515, 478], upload_to=path_and_rename, blank=True, null=True, quality=10,
                                         crop=['middle', 'center'])
    color = models.CharField(max_length=16,default="009dad")                           
    phoneNumber = models.CharField(max_length=14)
    #shoaar
    Slogan = models.CharField(max_length=64)
    socialMedia=models.JSONField()
    emergencyCall = models.CharField(max_length=14)
    location = models.JSONField()
    
    complexImage = models.ManyToManyField('image',related_name='picture',through="imageShip",blank=True)

    MEMBERSHIP_CHOICES = ( ("Premium", "pre"),("Free", "free"))
    membership_type = models.CharField(choices=MEMBERSHIP_CHOICES, default="Free",max_length=12)
    workTime = models.JSONField()

    rate =models.JSONField(verbose_name="امتیاز رستوران", blank=True, null=True, default=get_default_complex_rate)
    bio = models.TextField(verbose_name="بیوگرافی مجموعه", blank=True, null=True, default="bio")
    website = models.URLField()
    
    banner = models.ManyToManyField('image', verbose_name="بنر ها", through="bannerShip", blank=True)

    tax_choices = (("item", "item"), ('order', 'order'))
    taxType = models.CharField(choices=tax_choices, default="item",max_length=12)

    qrCode = models.ImageField(null= True, blank=True, upload_to=path_and_rename)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ افتتاح حساب")
    update_at = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ آخرین تغییرات")
    
    def __str__(self) :
        return str(self.name)

class image(models.Model):
    pic = models.ImageField("image", upload_to=path_and_rename)
    pic_tumbnail = ResizedImageField(size=[1000, 350], upload_to=path_and_rename, blank=True, null=True, quality=100,crop=['middle', 'center'])
    title = models.CharField(max_length=32, null=True, default='تصویر')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    def __str__(self):
        return str(self.title) + str(self.id)

    @property
    def pic_url(self):
        return str(self.pic.url)
    @property
    def pic_tumbnail_url(self):
        return str(self.pic_tumbnail.url)

class imageShip(models.Model):
    foodcomplex = models.ForeignKey("complex", on_delete=models.CASCADE)
    image = models.ForeignKey("image", on_delete=models.CASCADE)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    def __str__(self):
        return str(self.image.title) +str(self.image.id)+"+"+self.foodcomplex.name        

class bannerShip(models.Model):
    foodcomplex = models.ForeignKey("complex", on_delete=models.CASCADE)
    banner = models.ForeignKey("image", on_delete=models.CASCADE)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    def __str__(self):
        return f"{self.banner.title} for {self.foodcomplex.name}"

class customerClub(models.Model):
    complex =  models.ForeignKey(complex, on_delete=models.CASCADE)
    slug = models.SlugField(null=True, blank=True)
    MEMBERSHIP_CHOICES = ( ("Premium", "pre"),("Ordinary", "ordinary"))
    membership_type = models.CharField(choices=MEMBERSHIP_CHOICES, default="Ordinary",max_length=12)
    def __str__(self):
       return str(self.complex.name) + " " +  str(self.membership_type)

class UserMembership(models.Model):
    user = models.ForeignKey(customer, on_delete=models.CASCADE)
    membership = models.ForeignKey(customerClub,on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=False)

    def __str__(self):
       return str(self.user.username) + " "+ str(self.membership.complex.name)
    
class SystemLog(models.Model):
    action_list = (
        ('none', 'none'),
        ('Create', 'Create'),
        ('Update', 'Update'),
        ('Delete', 'Delete'),
    )
    level_list = (
        ("TRACE", "5"),
        ("DEBUG", "10"),
        ("INFO", "20"),
        ("SUCCESS", "25"),
        ("WARNING", "30"),
        ("ERROR", "40"),
        ("CRITICAL", "50"),
    )
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    complex = models.ForeignKey(complex, on_delete=models.CASCADE, related_name='which_complex_log', null=True, blank=True)
    worker = models.ForeignKey(worker, on_delete=models.CASCADE, related_name='which_worker_log', null=True, blank=True)
    action = models.CharField(max_length=50, choices = action_list, default ='none')
    level = models.CharField(max_length=50, choices = level_list, default ='TRACE')
    message = models.TextField(null=True, blank=True)
    model = models.CharField(max_length=50, null=True, blank=True)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

@receiver(post_save, sender=customer)
@receiver(post_save, sender=worker )
@receiver(post_save, sender=complex )
@receiver(post_save, sender=image )
@receiver(post_save, sender=imageShip )
@receiver(post_save, sender=bannerShip )
def log(sender, instance, created, **kwargs):
    try:
        import inspect
        for frame_record in inspect.stack():
            if frame_record[3]=='get_response':
                request = frame_record[0].f_locals['request']
                break
        else:
            request = None
    except:
        print("OOPS ...")
    
    try:
        model_name = ContentType.objects.get_for_model(sender)
        if created:
            if request:
                user = request.user
                text = f"USER:{user} - CREATED:{model_name} - ID: {instance.id}"
                system_log = SystemLog()
                if complex.objects.filter(owner=request.user).exists():
                    system_log.complex =complex.objects.get(owner=request.user)
                elif worker.objects.filter(user = request.user).exists():
                    system_log.worker =worker.objects.get(user=request.user)
                system_log.action = "Create"
                system_log.level = "INFO"
                system_log.message = text
                system_log.model = sender.__name__
                system_log.save()
            else:
                text = f"USER:AnonymousUser - CREATED:{model_name} - ID:{instance.id}"
                system_log = SystemLog()
                system_log.action = "Create"
                system_log.level = "INFO"
                system_log.message = text
                system_log.model = sender.__name__
                system_log.save()

        else:
            if request:
                user = request.user
                text = f"USER:{user} - UPDATED:{model_name} - ID:{instance.id}"
                system_log = SystemLog()
                if complex.objects.filter(owner=request.user).exists():
                    system_log.complex =complex.objects.get(owner=request.user)
                elif worker.objects.filter(user = request.user).exists():
                    system_log.worker =worker.objects.get(user=request.user)
                system_log.action = "Update"
                system_log.level = "INFO"
                system_log.message = text
                system_log.model = sender.__name__
                system_log.save()

            else:
                text = f"USER:AnonymousUser - UPDATED:{model_name} - ID:{instance.id}"
                system_log = SystemLog()
                system_log.action = "Update"
                system_log.level = "INFO"
                system_log.message = text
                system_log.model = sender.__name__
                system_log.save()

    except Exception as e:
        print("OOPS ...")


@receiver(post_delete, sender=customer)
@receiver(post_delete, sender=worker )
@receiver(post_delete, sender=complex )
@receiver(post_delete, sender=image )
@receiver(post_delete, sender=imageShip )
@receiver(post_delete, sender=bannerShip )
def log(sender, instance, **kwargs):
    try:
        import inspect
        for frame_record in inspect.stack():
            if frame_record[3]=='get_response':
                request = frame_record[0].f_locals['request']
                break
        else:
            request = None
    except:
        print("OOPS ...")
    
    try:
        model_name = ContentType.objects.get_for_model(sender)
        if request:
            user = request.user
            text = f"USER:{user} - DELETED:{model_name} - INSTANCE: {instance}"
            system_log = SystemLog()
            if complex.objects.filter(owner=request.user).exists():
                system_log.complex =complex.objects.get(owner=request.user)
            elif worker.objects.filter(user = request.user).exists():
                system_log.worker =worker.objects.get(user=request.user)
            system_log.action = "Delete"
            system_log.level = "INFO"
            system_log.message = text
            system_log.model = sender.__name__
            system_log.save()

        else:
            text = f"USER:AnonymousUser - DELETED:{model_name} - INSTANCE:{instance}"
            system_log = SystemLog()
            system_log.action = "Delete"
            system_log.level = "INFO"
            system_log.message = text
            system_log.model = sender.__name__
            system_log.save()

    except Exception as e:
        print("OOPS ...")
