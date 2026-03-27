from django.contrib import admin
from .models import IssueReport, Message, Notification


@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'title', 'category', 'status', 'priority', 'reporter', 'created_at']
    list_filter = ['status', 'category', 'priority']
    search_fields = ['title', 'reference_number', 'location', 'reporter__username']
    readonly_fields = ['reference_number', 'created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['report', 'sender', 'timestamp', 'is_official_response', 'is_read']
    list_filter = ['is_official_response', 'is_read']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read']
