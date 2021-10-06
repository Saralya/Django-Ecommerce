from django.db import models

# to create a custom User model and admin panel
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy

# to automatically create one to one objects
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


""" ekhane amra django er by default User Model use na kore custom User model baniye use korbo & settings.py e seta declare kore dibo""" 
""" nicher kaj gulo korar por makemigrations korte hobe...er age kora jabe na """


class MyUserManager(BaseUserManager):
    # akta custom user banacchi jekhane email hobe unique identifier
    def _create_user(self, email, password, **extra_fields): 
        # _create_user() is a by default function that creates & saves a user with email & password
        if not email:
            raise ValueError("The Email must be set!")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False)
    is_staff = models.BooleanField(
        ugettext_lazy('staff status'), 
        default=False, 
        help_text=ugettext_lazy('Designates whether the user can log in this site')
    )

    is_active = models.BooleanField(
        ugettext_lazy('active'),
        default=True,
        help_text=ugettext_lazy('Designates whether the user should be treated as active. Unselect this instead of deleting accounts')

    )

    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def _str_(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email  


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField( max_length=264, blank=True)
    full_name = models.CharField( max_length=264, blank=True)
    address_1 = models.TextField(max_length=300, blank=True)
    city = models.CharField( max_length=50, blank=True)
    zipcode = models.CharField( max_length=10, blank=True)
    country = models.CharField( max_length=50, blank=True)
    phone = models.CharField( max_length=50, blank=True)
    date_joined= models.DateField(auto_now_add=True)

    def _str_(self):
        return self.username + "'s Profile"

    def is_fully_filled(self):  # ei function er kaj hocche kono user Profile model er sob field fill up korse kina check kora
        fields_names = [f.name for f in self._meta.get_fields()] # Profile model er sob gula field akhon fields_names e chole ashbe

        for field_name in fields_names:
            value = getattr(self, field_name)
            if value is None or value=='':
                return False  # kono field fill up na kora thakle false return korbe

        return True


# jokhon akta user cretae hobe, tar jonno automatically profile o create korar option chole ashbe..tar jonno:
@receiver(post_save, sender=User) 
# User model e jokhn akta new user create holo tokhon akta signal jabe ekhane..erpor create_profile function diye tar jonno profile create hobe
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()  # Profile model er user field er related_name attribute e j nam likhsilam seta
# etar kaj hocche, user model er j kono change er jonno profile model eo effect fela
        