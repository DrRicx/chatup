from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where user_number is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, user_number, password, **extra_fields):
        """
        Create and save a User with the given user_number and password.
        """
        if not user_number:
            raise ValueError('The User Number field must be set')
        UserType = apps.get_model('account', 'UserType')
        student_type = UserType.objects.get(type='STUDENT')
        extra_fields.setdefault('user_type', student_type)
        user = self.model(user_number=user_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given user_number and password.
        """
        UserType = apps.get_model('account', 'UserType')
        employee_type = UserType.objects.get(type='EMPLOYEE')
        extra_fields.setdefault('user_type', employee_type)
        return self.create_user(user_number, password, **extra_fields)