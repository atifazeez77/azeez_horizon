from django.contrib import admin
from .models import User, StudentProfile, StudyTask, StudySession, TestExam, TestResult, LibraryLog, AppConfig

# Custom Admin View for Users to see Roles easily
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'phone', 'link_code')
    list_filter = ('role',)

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_exam', 'is_library_member', 'is_azeez_class_student')

admin.site.register(User, UserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(TestExam)
admin.site.register(TestResult)
admin.site.register(LibraryLog)
admin.site.register(AppConfig)