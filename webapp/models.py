from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

# --- 1. GLOBAL ROLES & AUTHENTICATION ---
class User(AbstractUser):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent'),
        ('TEACHER', 'Teacher'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=15, unique=True, null=True)
    
    # Parent-Child Linking Code
    link_code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.link_code:
            self.link_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

# --- 2. PROFILES ---
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    # Academic Details
    BOARD_CHOICES = (('CBSE', 'CBSE'), ('ICSE', 'ICSE'), ('UP', 'UP Board'))
    EXAM_TARGET_CHOICES = (('10TH', '10th Board'), ('12TH', '12th Board'), ('NEET', 'NEET'), ('JEE', 'JEE'))
    
    current_class = models.CharField(max_length=10)
    board = models.CharField(max_length=10, choices=BOARD_CHOICES)
    target_exam = models.CharField(max_length=10, choices=EXAM_TARGET_CHOICES)
    target_score_percent = models.FloatField(default=90.0)
    
    # Azeez Status
    is_azeez_class_student = models.BooleanField(default=False)
    is_library_member = models.BooleanField(default=False)
    batch_id = models.CharField(max_length=20, blank=True) # E.g., "Batch A"

    def __str__(self):
        return f"{self.user.username} ({self.current_class})"

# --- 4. STUDY PLANNER & TIMER ---
class StudyTask(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    topic = models.CharField(max_length=200)
    estimated_minutes = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)

class StudySession(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.FloatField(default=0.0)
    
    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = round(delta.total_seconds() / 60, 2)
        super().save(*args, **kwargs)

# --- 5. TESTS & RESULTS ---
class TestExam(models.Model):
    name = models.CharField(max_length=100) # e.g., "Physics Unit Test 1"
    date = models.DateField()
    subject = models.CharField(max_length=50)
    max_marks = models.FloatField()
    batch_code = models.CharField(max_length=20, blank=True) # For Azeez Classes

class TestResult(models.Model):
    exam = models.ForeignKey(TestExam, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    
    # Allows students to add "Self Mock Tests" without an Admin creating an Exam first
    exam_name_custom = models.CharField(max_length=100, blank=True) 
    
    marks_obtained = models.FloatField()
    total_marks = models.FloatField()
    date_taken = models.DateField(default=timezone.now)

    @property
    def percentage(self):
        return (self.marks_obtained / self.total_marks) * 100

# --- 6. LIBRARY MODULE ---
class LibraryLog(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    duration_hours = models.FloatField(default=0.0)
    
    def save(self, *args, **kwargs):
        if self.check_out_time and self.check_in_time:
            delta = self.check_out_time - self.check_in_time
            self.duration_hours = round(delta.total_seconds() / 3600, 2)
        super().save(*args, **kwargs)

# --- 3. SCORE PREDICTOR & 7. AI LOGS ---
class PredictionHistory(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    predicted_score = models.FloatField()
    status_message = models.CharField(max_length=200) # "On Track", "At Risk"

class AIChatLog(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# --- 12. CONFIG (Global Settings) ---
class AppConfig(models.Model):
    daily_motivation = models.TextField(default="Work hard in silence, let success make the noise.")
    library_open = models.BooleanField(default=True)