from django.contrib import admin
from django.contrib.sessions.models import Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'expire_date', 'get_data')
    readonly_fields = ['session_key', 'expire_date', 'get_data']

    def get_data(self, obj):
        # Helper function to display session data. This might be a large output!
        return obj.get_decoded()
    get_data.short_description = 'Data'
