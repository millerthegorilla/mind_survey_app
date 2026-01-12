from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from allauth.account.decorators import secure_admin_login
from allauth.account.models import EmailAddress
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Case, When
from django.db.utils import IntegrityError
from django.shortcuts import redirect
from django.urls import path
from django.views.generic.list import ListView
from faker import Faker

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class LocalUserAdmin(auth_admin.UserAdmin):

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    change_list_template = "admin/change_list.html"
    actions = ["user_printview", "delete_inactive_temp_users"]
    fieldsets = (
        (None, {"fields": ("username", "temp_user_password", "password")}),
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
    
    def user_printview(self, request, queryset):
        return redirect(
            "admin:show_added_users", str(list(queryset.values_list("id", flat=True)))
        )
    
    def delete_inactive_temp_users(self, request, queryset):
        count, details = User.objects.filter(is_active=False).exclude(temp_user_password="").delete()
        count = details.get('users.User', 0)
        breakpoint()
        self.message_user(
            request,
            _("%(count)d inactive temporary users have been deleted.") % {"count": count},
        )

    def add_10_random_users(self, request):
        fake = Faker()
        ids = []
        for index in range(10):
            user = User()
            user.username = fake.passport_number()
            user.temp_user_password = fake.password()
            user.password = make_password(user.temp_user_password)
            try:
               user.save()
            except IntegrityError:
                index -= 1
                continue
            email = EmailAddress.objects.create(user=user, email=fake.email(), verified=True)
            email.save()
            ids.append(user.id)
        return redirect("admin:show_added_users", str(ids))
    
    def get_urls(self):
        urls = super(LocalUserAdmin, self).get_urls()
        my_urls = [
            path("addrand/", self.add_10_random_users),
            path(
                "show_added_users/<str:added_users>/",
                AddedUser.as_view(),
                name="show_added_users",
            ),
        ]
        return my_urls + urls


class AddedUser(LoginRequiredMixin,ListView):
    template_name = "admin/show_added_users.html"

    def get_queryset(self):
        pk_list = [int(id) for id in self.kwargs["added_users"][1:-1].split(",")]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        queryset = User.objects.filter(pk__in=pk_list).order_by(preserved)
        return queryset

try:
    admin.site.unregister(User)
    admin.site.register(User, LocalUserAdmin)
except NotRegistered:
    pass
