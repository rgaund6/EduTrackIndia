from django.urls import path
from .views import (
    home, register, user_login, dashboard, user_logout, college_search, college_detail,
    exam_list, notifications, save_college, saved_colleges, analytics, profile, verify_otp,
    recommend_college, institute_list, institute_detail, compare_institutes, counselling,
    # AI feature views (original)
    scholarship_finder, apply_scholarship, my_scholarships,
    college_comparison,
    admission_deadlines, add_deadline,
    smart_dashboard, student_profile_view,
    parent_register, parent_dashboard, parent_pending,
    career_guidance, exam_recommendations, recommend_exams,
    # New Advanced AI Features
    admission_predictor, predict_admission, prediction_history,
    education_chatbot, send_chat_message, clear_chat,
    career_roadmap, generate_roadmap, view_roadmap,
    college_scores,
    college_reviews, add_review,
    cost_calculator, calculate_cost,
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', user_logout, name='logout'),

    path('colleges/', college_search, name='college_search'),
    path('college/<int:college_id>/', college_detail, name='college_detail'),
    path('exams/', exam_list, name='exams'),
    path('notifications/', notifications, name='notifications'),
    path('save-college/<int:college_id>/', save_college, name='save_college'),
    path('saved-colleges/', saved_colleges, name='saved_colleges'),
    path('analytics/', analytics, name='analytics'),
    path('profile/', profile, name='profile'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('recommend/', recommend_college, name='recommend'),

    # Institutes — dono naam chahiye kyunki templates dono use karte hain
    path('institutes/', institute_list, name='institutes'),
    path('institutes/list/', institute_list, name='institute_list'),
    path('institute/<int:institute_id>/', institute_detail, name='institute_detail'),

    path('compare/', compare_institutes, name='compare_institutes'),
    path('counselling/', counselling, name='counselling'),

    # ===== AI FEATURE URLS =====

    # Scholarship Finder
    path('scholarships/', scholarship_finder, name='scholarship_finder'),
    path('scholarship/<int:scholarship_id>/apply/', apply_scholarship, name='apply_scholarship'),
    path('my-scholarships/', my_scholarships, name='my_scholarships'),

    # College Comparison
    path('college-comparison/', college_comparison, name='college_comparison'),

    # Admission Deadlines
    path('deadlines/', admission_deadlines, name='admission_deadlines'),
    path('deadlines/add/', add_deadline, name='add_deadline'),

    # Smart Dashboard
    path('dashboard/ai/', smart_dashboard, name='smart_dashboard'),
    path('profile/student/', student_profile_view, name='student_profile'),

    # Parent Mode
    path('parent/register/', parent_register, name='parent_register'),
    path('parent/dashboard/', parent_dashboard, name='parent_dashboard'),
    path('parent/pending/', parent_pending, name='parent_pending'),

    # Career Guidance
    path('career/', career_guidance, name='career_guidance'),
    path('exams/recommendations/', exam_recommendations, name='exam_recommendations'),
    path('exams/recommend/', recommend_exams, name='recommend_exams'),

    # ===== ADVANCED AI FEATURES =====

    # 1. AI Admission Predictor
    path('admission-predictor/', admission_predictor, name='admission_predictor'),
    path('admission-predictor/predict/', predict_admission, name='predict_admission'),
    path('my-predictions/', prediction_history, name='prediction_history'),

    # 2. AI Education Chatbot
    path('chatbot/', education_chatbot, name='education_chatbot'),
    path('chatbot/send/', send_chat_message, name='send_chat_message'),
    path('chatbot/clear/', clear_chat, name='clear_chat'),

    # 3. Career Roadmap Generator
    path('career-roadmap/', career_roadmap, name='career_roadmap'),
    path('career-roadmap/generate/', generate_roadmap, name='generate_roadmap'),
    path('roadmap/<int:roadmap_id>/', view_roadmap, name='view_roadmap'),

    # 4. College AI Score System
    path('college-scores/', college_scores, name='college_scores'),

    # 5. Student Review System
    path('college/<int:college_id>/reviews/', college_reviews, name='college_reviews'),
    path('college/<int:college_id>/review/add/', add_review, name='add_review'),

    # 6. Education Cost Calculator
    path('cost-calculator/', cost_calculator, name='cost_calculator'),
    path('cost-calculator/calculate/', calculate_cost, name='calculate_cost'),
]
