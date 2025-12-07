import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StudentProfile

# --- SETUP YOUR API KEY HERE ---
GENAI_API_KEY = "AIzaSyCyCVNBEL43u7oGF_-uvlz5zIH7q14lrqQ" 
genai.configure(api_key=GENAI_API_KEY)

def home(request):
    return render(request, 'webapp/home.html')

@login_required
def dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    context = {'student': request.user, 'profile': profile}
    return render(request, 'webapp/dashboard.html', context)

def ai_mentor(request):
    response_text = ""
    if request.method == 'POST':
        user_query = request.POST.get('query')
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"You are Azeez Sir, a strict but caring teacher. Answer this in Hinglish: {user_query}"
        try:
            ai_response = model.generate_content(prompt)
            response_text = ai_response.text
        except:
            response_text = "Check internet connection."
    return render(request, 'webapp/ai_mentor.html', {'response': response_text})