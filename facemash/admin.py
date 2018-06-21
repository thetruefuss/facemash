from django.contrib import admin

from .models import FaceMash


class FaceMashAdmin(admin.ModelAdmin):
    list_display = ('photo', 'ratings', 'timestamp')
    list_filter = ('ratings',)
    date_hierarchy = 'timestamp'
admin.site.register(FaceMash, FaceMashAdmin)
