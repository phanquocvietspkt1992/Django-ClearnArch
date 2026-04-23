import uuid
from django.db import models
from .exceptions import DomainException


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=200, unique=True)
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    password_hash = models.CharField(max_length=256, default='')
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100, default='system')
    updated_by = models.CharField(max_length=100, default='system')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'

    @classmethod
    def create(cls, email, full_name, phone_number, password, created_by='system'):
        from django.contrib.auth.hashers import make_password
        instance = cls(
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            is_active=True,
            created_by=created_by,
            updated_by=created_by,
        )
        instance.password_hash = make_password(password)
        return instance

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password_hash)

    def set_password(self, raw_password, updated_by='system'):
        from django.contrib.auth.hashers import make_password
        from django.utils import timezone
        self.password_hash = make_password(raw_password)
        self.updated_by = updated_by
        self.updated_at = timezone.now()

    def update_profile(self, full_name, phone_number, updated_by='system'):
        from django.utils import timezone
        self.full_name = full_name
        self.phone_number = phone_number
        self.updated_by = updated_by
        self.updated_at = timezone.now()

    def activate(self, updated_by='system'):
        if self.is_active:
            raise DomainException('User is already active.')
        from django.utils import timezone
        self.is_active = True
        self.updated_by = updated_by
        self.updated_at = timezone.now()

    def deactivate(self, updated_by='system'):
        if not self.is_active:
            raise DomainException('User is already inactive.')
        from django.utils import timezone
        self.is_active = False
        self.updated_by = updated_by
        self.updated_at = timezone.now()
