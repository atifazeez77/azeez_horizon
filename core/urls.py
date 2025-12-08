from django.contrib import admin
from django.urls import path
from webapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Root URL now points to Landing Page
    path('', views.landing_page, name='landing'), 
    
    # 2. Dashboard gets its own URL
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Tools
    path('predictor/', views.predictor, name='predictor'),
    path('planner/', views.planner, name='planner'),
    path('timer/', views.study_timer, name='study_timer'),
    path('save-session/', views.save_session, name='save_session'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    
    # Library
    path('library-action/', views.library_action, name='library_action'),
    
    # Auth & Parent
    path('signup/', views.signup, name='signup'),
    path('link-child/', views.link_child, name='link_child'),
    path('login/', auth_views.LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]