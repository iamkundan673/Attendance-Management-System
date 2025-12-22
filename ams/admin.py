from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Adduser,Attendance,LeaveRequest

@admin.register(Adduser)
class AdduserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'Full_Name', 'is_staff')
    list_filter = ('is_staff',)
    search_fields = ('username', 'email', 'Full_Name')

admin.site.register(Attendance)
admin.site.register(LeaveRequest)