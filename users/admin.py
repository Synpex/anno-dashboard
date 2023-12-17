# Django admin configuration for the users app
from django.contrib import admin
from django.utils.html import format_html
from .models.profile_model import UserProfile

# Define the admin class for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display = ('user', 'telephone', 'picture_tag')
    # Enable a search bar for user profiles
    search_fields = ['user__username', 'user__email', 'telephone']

    def picture_tag(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="width: 45px; height:45px;" />', obj.picture.url)
        return "-"
    picture_tag.short_description = 'Picture'

# Register the UserProfile model with the UserProfileAdmin options
admin.site.register(UserProfile,UserProfileAdmin)
