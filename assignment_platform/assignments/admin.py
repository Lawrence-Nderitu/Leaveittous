from django.contrib import admin
from .models import Assignment, Bid

@admin.register(Assignment) # Use decorator for registration
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'writer', 'status', 'deadline', 'budget', 'submitted_at', 'rating', 'created_at') # Added created_at
    list_filter = ('status', 'deadline', 'student', 'writer', 'subject', 'rating') # subject was already there
    search_fields = ('title', 'description', 'student__username', 'writer__username', 'subject') # Added subject
    readonly_fields = ('created_at', 'updated_at', 'submitted_at') # created_at, updated_at already here

    fieldsets = (
        (None, {'fields': ('title', 'description', 'subject', 'student')}),
        ('Requirement Files', { # New fieldset for requirement files
            'fields': ('requirement_file_1', 'requirement_file_2'),
            'classes': ('collapse',), # Optional: make it collapsible
        }),
        ('Assignment Details', {'fields': ('budget', 'deadline')}),
        ('Assignment State', {'fields': ('status', 'writer')}),
        ('Submission Details', {'fields': ('submitted_work', 'submission_notes', 'submitted_at')}),
        ('Student Review', {'fields': ('rating', 'review_comments')}),
        ('Timestamps', { # Added Timestamps fieldset
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    raw_id_fields = ('student', 'writer')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'writer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'writer', 'assignment')
    search_fields = ('assignment__title', 'writer__username', 'proposal')
    readonly_fields = ('created_at',)
    raw_id_fields = ('assignment', 'writer')
    list_editable = ('status',)
