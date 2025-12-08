import os
import google.generativeai as genai
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import login
from dotenv import load_dotenv

# Import Models and Forms
from .models import *
from .forms import StudentSignupForm 

# --- CONFIGURATION ---
load_dotenv()
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

# --- AUTHENTICATION (The Missing Part) ---
def signup(request):
    if request.method == 'POST':
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentSignupForm()
    return render(request, 'webapp/signup.html', {'form': form})

# --- DASHBOARD ---
@login_required
def dashboard(request):
    user = request.user
    if user.role == 'PARENT':
        children = StudentProfile.objects.filter(parent=user)
        return render(request, 'webapp/parent_dashboard.html', {'children': children})

    if user.role == 'STUDENT':
        profile, created = StudentProfile.objects.get_or_create(user=user)
        config = AppConfig.objects.first()
        motivation = config.daily_motivation if config else "Keep Pushing!"
        
        today_study = StudySession.objects.filter(student=profile, start_time__date=timezone.now().date())
        total_mins = sum([s.duration_minutes for s in today_study])
        active_library_session = LibraryLog.objects.filter(student=profile, check_out_time__isnull=True).first()
        
        context = {
            'profile': profile,
            'motivation': motivation,
            'study_hours': round(total_mins / 60, 1),
            'active_lib_session': active_library_session,
        }
        return render(request, 'webapp/student_dashboard.html', context)
    
    return redirect('/admin/')

# --- PARENT FEATURE ---
@login_required
def link_child(request):
    if request.method == 'POST':
        code = request.POST.get('link_code')
        try:
            child_user = User.objects.get(link_code=code, role='STUDENT')
            child_user.student_profile.parent = request.user
            child_user.student_profile.save()
        except User.DoesNotExist:
            pass 
    return redirect('dashboard')

# --- LIBRARY ---
@login_required
def library_action(request):
    try:
        profile = request.user.student_profile
    except:
        return redirect('dashboard')

    if not profile.is_library_member:
        return redirect('dashboard')

    action = request.POST.get('action')
    if action == 'check_in':
        LibraryLog.objects.create(student=profile)
    elif action == 'check_out':
        log = LibraryLog.objects.filter(student=profile, check_out_time__isnull=True).last()
        if log:
            log.check_out_time = timezone.now()
            log.save()
    return redirect('dashboard')

# --- PREDICTOR ---
@login_required
def predictor(request):
    profile = request.user.student_profile
    prediction = None
    msg = ""

    if request.method == 'POST':
        try:
            last_marks = float(request.POST.get('last_marks', 0))
            study_hrs = float(request.POST.get('study_hrs', 0))
            pred_val = (last_marks * 0.6) + (study_hrs * 2.5) + 20 
            prediction = min(round(pred_val, 1), 99.9)
            
            if prediction >= profile.target_score_percent: msg = "Target is Safe ✅"
            elif prediction >= profile.target_score_percent - 10: msg = "Slightly Behind ⚠️"
            else: msg = "At Serious Risk 🚨"
                
            PredictionHistory.objects.create(student=profile, predicted_score=prediction, status_message=msg)
        except ValueError:
            msg = "Enter valid numbers."

    return render(request, 'webapp/predictor.html', {'prediction': prediction, 'msg': msg})

# --- AI CHAT ---
@login_required
def ai_chat(request):
    response_text = ""
    if request.method == 'POST':
        query = request.POST.get('query')
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"You are Azeez Sir. Student Class {request.user.student_profile.current_class}. Query: {query}. Reply in Hinglish."
        try:
            ai_response = model.generate_content(prompt)
            response_text = ai_response.text
            AIChatLog.objects.create(student=request.user.student_profile, query=query, response=response_text)
        except Exception as e:
            print(f"AI Error: {e}")
            response_text = "Server busy. Try again."
    return render(request, 'webapp/ai_chat.html', {'response': response_text})

# --- PLANNER ---
@login_required
def planner(request):
    profile = request.user.student_profile
    if request.method == 'POST' and 'add_task' in request.POST:
        StudyTask.objects.create(
            student=profile,
            subject=request.POST.get('subject'),
            topic=request.POST.get('topic'),
            estimated_minutes=int(request.POST.get('minutes'))
        )
        return redirect('planner')

    if request.method == 'POST' and 'toggle_task' in request.POST:
        task_id = request.POST.get('task_id')
        task = get_object_or_404(StudyTask, id=task_id)
        task.is_completed = not task.is_completed
        task.save()
        return redirect('planner')

    tasks = StudyTask.objects.filter(student=profile, date=timezone.now().date())
    return render(request, 'webapp/planner.html', {'tasks': tasks})

# --- TIMER ---
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