from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from allauth.account.decorators import secure_admin_login
from allauth.account.models import EmailAddress
from faker import Faker
from djf_surveys.admin import UserAdmin

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class LocalUserAdmin(UserAdmin):

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]
    
    def add_10_random_users(self, request):
        fake = Faker()
        ids = []
        for index in range(10):
            user = User()
            user.username = fake.passport_number()
            user.password = fake.password()
            try:
               user.save()
            except IntegrityError:
                index -= 1
                continue
            email = EmailAddress.objects.create(user=user, email=fake.email(), verified=True)
            email.save()
            ids.append(user.id)
        return redirect("admin:show_added_users", str(ids))
