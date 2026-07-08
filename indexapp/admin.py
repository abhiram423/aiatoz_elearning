from django.contrib import admin
from .models import Course, UserProfile, QuizResponse

admin.site.register(Course)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_username')

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return "⚠️ Ghost Profile (No User Attached)"
    
    # Sets the column header text in admin dashboard
    get_username.short_description = 'User' 

admin.site.register(UserProfile, UserProfileAdmin)

class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_username')

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return "⚠️ Ghost Response (No User Attached)"
    
    get_username.short_description = 'User'

admin.site.register(QuizResponse, QuizResponseAdmin)