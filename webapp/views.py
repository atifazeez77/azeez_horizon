import os
import google.generativeai as genai
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import *
from dotenv import load_dotenv

load_dotenv()
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

# --- DASHBOARD (Requirement 2 & 8) ---
@login_required
def dashboard(request):
    user = request.user
    
    # 1. Parent View Logic
    if user.role == 'PARENT':
        # Find children linked to this parent
        children = StudentProfile.objects.filter(parent=user)
        return render(request, 'webapp/parent_dashboard.html', {'children': children})

    # 2. Student View Logic
    if user.role == 'STUDENT':
        profile, created = StudentProfile.objects.get_or_create(user=user)
        config = AppConfig.objects.first()
        
        # Get Stats
        today_study = StudySession.objects.filter(student=profile, start_time__date=timezone.now().date())
        total_mins = sum([s.duration_minutes for s in today_study])
        
        # Check active library session
        active_library_session = LibraryLog.objects.filter(student=profile, check_out_time__isnull=True).first()
        
        context = {
            'profile': profile,
            'motivation': config.daily_motivation if config else "Keep Pushing!",
            'study_hours': round(total_mins / 60, 1),
            'active_lib_session': active_library_session,
        }
        return render(request, 'webapp/student_dashboard.html', context)
    
    return redirect('/admin/') # Teachers/Admins go to panel for now

# --- LIBRARY MODULE (Requirement 6) ---
@login_required
def library_action(request):
    profile = request.user.student_profile
    if not profile.is_library_member:
        return redirect('dashboard') # Security check

    action = request.POST.get('action')
    
    if action == 'check_in':
        # Create new log
        LibraryLog.objects.create(student=profile)
        
    elif action == 'check_out':
        # Find open session and close it
        log = LibraryLog.objects.filter(student=profile, check_out_time__isnull=True).last()
        if log:
            log.check_out_time = timezone.now()
            log.save()
            
    return redirect('dashboard')

# --- SCORE PREDICTOR (Requirement 3) ---
@login_required
def predictor(request):
    profile = request.user.student_profile
    prediction = None
    msg = ""

    if request.method == 'POST':
        # Simplified Logic (Replace with your ML Model later)
        last_marks = float(request.POST.get('last_marks')) # Out of 100
        study_hrs = float(request.POST.get('study_hrs'))
        
        # Formula: 60% weight to marks + 10% per hour of study (capped)
        pred_val = (last_marks * 0.6) + (study_hrs * 2.5) + 20 
        prediction = min(round(pred_val, 1), 99.9)
        
        # Status Logic
        if prediction >= profile.target_score_percent:
            msg = "Target is Safe ✅"
        elif prediction >= profile.target_score_percent - 10:
            msg = "Slightly Behind ⚠️"
        else:
            msg = "At Serious Risk 🚨"
            
        # Save History
        PredictionHistory.objects.create(student=profile, predicted_score=prediction, status_message=msg)

    return render(request, 'webapp/predictor.html', {'prediction': prediction, 'msg': msg})

# --- AI MENTOR (Requirement 7) ---
@login_required
def ai_chat(request):
    response_text = ""
    if request.method == 'POST':
        query = request.POST.get('query')
        
        # Azeez Persona Prompt
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"""
        You are Azeez Sir. 
        Student Profile: Class {request.user.student_profile.current_class}, Target: {request.user.student_profile.target_exam}.
        Student Query: {query}
        Reply in Hinglish. Be direct and motivating.
        """
        try:
            ai_response = model.generate_content(prompt)
            response_text = ai_response.text
        except:
            response_text = "Check internet connection."
    return render(request, 'webapp/ai_mentor.html', {'response': response_text})
# --- PASTE THIS AT THE BOTTOM OF views.py ---

@login_required
def planner(request):
    profile = request.user.student_profile
    
    # Handle New Task
    if request.method == 'POST' and 'add_task' in request.POST:
        StudyTask.objects.create(
            student=profile,
            subject=request.POST.get('subject'),
            topic=request.POST.get('topic'),
            estimated_minutes=int(request.POST.get('minutes'))
        )
        return redirect('planner')

    # Handle Task Completion
    if request.method == 'POST' and 'toggle_task' in request.POST:
        task = StudyTask.objects.get(id=request.POST.get('task_id'))
        task.is_completed = not task.is_completed
        task.save()
        return redirect('planner')

    tasks = StudyTask.objects.filter(student=profile, date=timezone.now().date())
    return render(request, 'webapp/planner.html', {'tasks': tasks})

@login_required
def study_timer(request):
    return render(request, 'webapp/timer.html')

@login_required
def save_session(request):
    if request.method == 'POST':
        minutes = float(request.POST.get('minutes'))
        subject = request.POST.get('subject')
        StudySession.objects.create(
            student=request.user.student_profile,
            subject=subject,
            duration_minutes=minutes
        )
    return redirect('dashboard')