from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

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

#     change_list_template = "djf_surveys/admin/change_list.html"
#     actions = ['user_printview']
    
#     # def get_changeform_initial_data(self, request):
#     #     return {'dave':'dave'}

#     def user_printview(self, request, queryset):
#         return redirect("admin:show_added_users", str(list(queryset.values_list('id', flat=True))))

#     def add_10_random_users(self, request):
#         fake = Faker()
#         ids = []
#         for index in range(10):
#             user = User()
#             user.username = fake.passport_number()
#             user.password = fake.password()
#             try:
#                 user.save()
#                 ids.append(user.id)
#             except IntegrityError:
#                 index -= 1
#                 continue
#         return redirect("admin:show_added_users", str(ids))

#     def get_urls(self):
#         urls = super(AuthUserAdmin, self).get_urls()
#         my_urls = [
#             path("addrand/", self.add_10_random_users),
#             path("show_added_users/<str:added_users>/", AddedUser.as_view(), name="show_added_users")
#         ]
#         return my_urls + urls
    

# class AddedUser(ListView):
#     template_name = "djf_surveys/admin/show_added_users.html"

#     def get_queryset(self):
#         pk_list = [ int(id) for id in self.kwargs['added_users'][1:-1].split(',') ]
#         preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
#         queryset = User.objects.filter(pk__in=pk_list).order_by(preserved)
#         return queryset
