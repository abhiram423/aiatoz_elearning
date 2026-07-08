from django.contrib import admin
from .models import Course, UserProfile, QuizResponse


admin.site.register(Course)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'mobile', 'get_linked_auth_user')

    def get_linked_auth_user(self, obj):
        # Gracefully handle if the OneToOne User mapping is broken
        if obj.user:
            return obj.user.username
        return "⚠️ Broken Profile (No Auth User)"
    
    get_linked_auth_user.short_description = 'Auth Account Status'

admin.site.register(UserProfile, UserProfileAdmin)

class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_student_email', 'question', 'created_at')

    def get_student_email(self, obj):
        # Safely fetch email without jumping deep into broken foreign relations
        if obj.user_profile:
            return obj.user_profile.email
        return "⚠️ Orphaned Response (No Profile)"
    
    get_student_email.short_description = 'Student Email'

admin.site.register(QuizResponse, QuizResponseAdmin)