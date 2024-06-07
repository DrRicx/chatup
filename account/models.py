from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from .managers import CustomUserManager

# Create your models here.
def get_profile_image_filepath(self, filename):
    """
    Returns the profile picture with the primary key
    :param self:
    :param filename:
    :return:
    """
    return f'profile_images/{self.pk}/{"profile_image.png"}'


def get_default_profile_image():
    """
    Set a default profile image for each user
    :return:
    """
    return "profilePictureDefault/default_profile.png"
class UserType(models.Model):
    EMPLOYEE = 'EMPLOYEE'
    STUDENT = 'STUDENT'
    USER_TYPE_CHOICES = [
        (EMPLOYEE, 'Employee'),
        (STUDENT, 'Student'),
    ]

    type = models.CharField(
        max_length=25,
        choices=USER_TYPE_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type

class CustomUser(AbstractBaseUser):
    user_number = models.CharField(max_length=12, unique=True)
    user_profile = models.OneToOneField('UserProfile', on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'user_number'
    REQUIRED_FIELDS = ['email']

    def has_perm(self, perm, obj=None):
        # Return False if the user is a student, True if the user is an employee
        return self.user_type.type == UserType.EMPLOYEE

    def has_module_perms(self, app_label):
        # Return False if the user is a student, True if the user is an employee
        return self.user_type.type == UserType.EMPLOYEE

    def __str__(self):
        return f"{self.user_number}"

class UserProfile(models.Model):
    profile_picture = models.ImageField(null=True, blank=True, upload_to=get_profile_image_filepath,
                                        default=get_default_profile_image)
    gender = models.CharField(
        max_length=6,
        choices=[('MALE', 'male'), ('FEMALE', 'female')]
    )
    first_name = models.CharField(max_length=12, null=True, blank=True)
    middle_name = models.CharField(max_length=12, null=True, blank=True)
    last_name = models.CharField(max_length=12, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.first_name

    def get_profile_filename(self):
        """
        Change the upload picture name into 'profile_image'
        :return:
        """
        return str(self.profile_picture)[str(self.profile_picture).index(f'profile_images/{self.pk}/'):]
