from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    def create_user(self, school_email, name, student_id, major, password=None):
        if not school_email:
            raise ValueError('Users must have an email address')

        user = self.model(
            school_email=self.normalize_email(school_email),
            name=name,
            student_id=student_id,
            major=major,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school_email = models.EmailField(
        verbose_name='school email',
        max_length=255,
        unique=True,
    )

    name = models.CharField(max_length=100, default="이름")
    student_id = models.CharField(max_length=20, unique=True)
    major = models.CharField(max_length=100, default="미지정")
    date_joined = models.DateTimeField(default=timezone.now)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'school_email'
    REQUIRED_FIELDS = ['name', 'student_id', 'major']

    def __str__(self):
        return self.school_email


class EmailVerification(models.Model):
    TYPE_CHOICES = (
        ('registration', '회원가입'),
        ('password_reset', '비밀번호 변경'),
    )

    user_email = models.EmailField()
    verification_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='registration')

    def __str__(self):
        return f"{self.user_email} - {self.verification_code}"

    def is_valid(self):
        return timezone.now() <= self.expires_at