from django.contrib import admin
from .models import Assignment, Bid

@admin.register(Assignment) # Use decorator for registration
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'writer', 'status', 'deadline', 'budget', 'submitted_at')
    list_filter = ('status', 'deadline', 'student', 'writer', 'subject') # Added subject here
    search_fields = ('title', 'description', 'student__username', 'writer__username')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at') # submitted_at is set by logic

    fieldsets = (
        (None, {'fields': ('title', 'description', 'subject', 'student')}),
        ('Assignment Details', {'fields': ('budget', 'deadline')}),
        ('Assignment State', {'fields': ('status', 'writer')}),
        ('Submission Details', {'fields': ('submitted_work', 'submission_notes', 'submitted_at')}),
    )
    # raw_id_fields can be useful for student and writer if user list is very long
    raw_id_fields = ('student', 'writer')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'writer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'writer', 'assignment')
    search_fields = ('assignment__title', 'writer__username', 'proposal')
    readonly_fields = ('created_at',)
    raw_id_fields = ('assignment', 'writer')
    list_editable = ('status',)
