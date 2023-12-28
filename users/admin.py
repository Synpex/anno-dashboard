from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .forms.custom_user_creation_form import CustomUserCreationForm
from .models.profile_model import UserProfile

# Your existing UserProfileAdmin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telephone', 'picture_tag')
    search_fields = ['user__username', 'user__email', 'telephone']

    def picture_tag(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="width: 45px; height:45px;" />', obj.picture.url)
        return "-"
    picture_tag.short_description = 'Picture'

# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    inlines = (UserProfileInline,)


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'telephone', 'picture'),
        }),
    )
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your UserProfile admin
admin.site.register(UserProfile, UserProfileAdmin)
