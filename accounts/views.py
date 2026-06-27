from django.conf import settings
import random
import json
import uuid
import os
print("GROQ KEY:", os.getenv("GROQ_API_KEY"))
print("SETTINGS KEY:", settings.GROQ_API_KEY)
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from .forms import (
    AdmissionPredictionForm,
    CareerRoadmapForm,
    CollegeReviewForm,
    CostCalculationForm,
    CounsellingLeadForm,
)
from .models import (
    CounsellingLead,
    College,
    Exam,
    Notification,
    SavedCollege,
    EmailOTP,
    Institute,
    Scholarship,
    ScholarshipApplication,
    AdmissionDeadline,
    AppliedCollege,
    CollegeComparison,
    AIChat,
    DashboardTask,
    ExamRecommendation,
    StudentProfile,
    ParentProfile,
    CustomUser,
    AdmissionPrediction,
    AIChatSession,
    CareerRoadmap,
    RoadmapMilestone,
    CollegeAIScore,
    CollegeReview,
    CostCalculation,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ParentProfile, CustomUser

from .forms import StudentRegistrationForm, CollegeRecommendationForm

from groq import Groq


# ============================================================
# GROQ HELPER — single place to configure/change the model
# ============================================================

GROQ_MODEL = "llama-3.1-8b-instant"


def get_groq_client():
    """Return a configured Groq client or raise a clear configuration error."""
    api_key = getattr(settings, 'GROQ_API_KEY', '')
    if not api_key:
        raise ValueError(
            'Groq API key is not configured. '
            'Set GROQ_API_KEY in your environment or .env file.'
        )
    return Groq(api_key=api_key)


def groq_generate(prompt: str, system: str = "", max_tokens: int = 1024) -> str:
    """
    Send a prompt to Groq and return the response text.
    Replaces all genai / model.generate_content() calls.
    """
    client = get_groq_client()
    messages_payload = []
    if system:
        messages_payload.append({"role": "system", "content": system})
    messages_payload.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages_payload,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


# ============================================================
# UTILITY HELPERS
# ============================================================

def extract_json_object(text, fallback):
    """Extract first JSON object from AI response safely."""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except (TypeError, ValueError, json.JSONDecodeError):
        pass
    return fallback


def clamp_number(value, minimum=0, maximum=100):
    try:
        return max(minimum, min(maximum, float(value)))
    except (TypeError, ValueError):
        return minimum


def fallback_admission_prediction(form_data, college):
    percentage = clamp_number(form_data.get('percentage_12th'), 0, 100)
    budget = int(form_data.get('budget') or 0)
    exam_rank = int(form_data.get('exam_rank') or 0)
    affordability_bonus = 10 if budget >= college.fees else -10
    rank_score = max(0, 100 - (exam_rank / 1000))
    course_match = 10 if form_data.get('preferred_course', '').lower() in college.courses.lower() else 0
    probability = clamp_number(
        (percentage * 0.45) + (rank_score * 0.25) + affordability_bonus + course_match,
        5, 95
    )
    category = 'safe' if probability >= 70 else 'moderate' if probability >= 45 else 'dream'
    return {
        'probability': round(probability),
        'category': category,
        'reason': (
            'This estimate uses your percentage, rank, budget fit, and course availability '
            'because the AI service could not return a structured answer.'
        ),
        'backup_colleges': [],
        'better_options': [],
        'required_cutoff': 'Check the latest official counselling cutoff for this course and category.',
    }


# ============================================================
# BASIC VIEWS
# ============================================================

def home(request):
    return render(request, 'accounts/home.html')


def send_otp(user):
    otp = str(random.randint(100000, 999999))
    EmailOTP.objects.create(user=user, otp=otp)
    send_mail(
        'EduTrack OTP Verification',
        f'Your OTP is {otp}',
        'yourgmail@gmail.com',
        [user.email],
        fail_silently=False,
    )


def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['verify_email'] = user.email
            send_otp(user)
            return redirect('verify_otp')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_otp(request):
    email = request.session.get('verify_email')
    if not email:
        messages.error(request, "Please register first.")
        return redirect('register')

    if request.method == "POST":
        otp = request.POST.get("otp")
        otp_obj = EmailOTP.objects.filter(user__email=email, otp=otp).last()
        if otp_obj:
            user = otp_obj.user
            user.email_verified = True
            user.save()
            del request.session['verify_email']
            messages.success(request, "Email verified successfully. Please login.")
            return redirect('login')
        messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'accounts/verify_otp.html', {'email': email})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.email_verified:
                messages.error(request, "Please verify your email first.")
                return redirect('login')
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid Username or Password")
    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    User = get_user_model()
    context = {
        'students': User.objects.count(),
        'colleges': College.objects.count(),
        'exams': Exam.objects.count(),
        'notifications_count': Notification.objects.count(),
        'institutes_count': Institute.objects.count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def college_search(request):
    query = request.GET.get('q')
    colleges = College.objects.all()
    if query:
        colleges = colleges.filter(name__icontains=query)
    return render(request, 'accounts/college_search.html', {'colleges': colleges})


@login_required(login_url='login')
def college_detail(request, college_id):
    college = get_object_or_404(College, id=college_id)
    return render(request, 'accounts/college_detail.html', {'college': college})


@login_required(login_url='login')
def exam_list(request):
    exams = Exam.objects.all().order_by('exam_date')
    return render(request, 'accounts/exams.html', {'exams': exams})


@login_required(login_url='login')
def notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'accounts/notifications.html', {'notifications': notifications})


@login_required(login_url='login')
def save_college(request, college_id):
    college = get_object_or_404(College, id=college_id)
    SavedCollege.objects.get_or_create(user=request.user, college=college)
    return redirect('college_detail', college_id=college.id)


@login_required(login_url='login')
def saved_colleges(request):
    colleges = SavedCollege.objects.filter(user=request.user)
    return render(request, 'accounts/saved_colleges.html', {'colleges': colleges})


@login_required(login_url='login')
def analytics(request):
    User = get_user_model()
    context = {
        'students': User.objects.count(),
        'colleges': College.objects.count(),
        'exams': Exam.objects.count(),
        'saved_colleges': SavedCollege.objects.count(),
        'institutes_count': Institute.objects.count(),
    }
    return render(request, 'accounts/analytics.html', context)


@login_required(login_url='login')
def profile(request):
    saved_count = SavedCollege.objects.filter(user=request.user).count()
    return render(request, 'accounts/profile.html', {'saved_count': saved_count})


@login_required(login_url='login')
def recommend_college(request):
    ai_result = None
    if request.method == "POST":
        form = CollegeRecommendationForm(request.POST)
        if form.is_valid():
            rank = form.cleaned_data['rank']
            state = form.cleaned_data['state']
            course = form.cleaned_data['course']

            colleges = College.objects.all()[:30]
            college_data = ""
            for c in colleges:
                college_data += f"""
Name: {c.name}
State: {c.state}
Courses: {c.courses}
Fees: {c.fees}
Placement: {c.placement_percentage}%
Website: {c.official_website}
"""
            try:
                prompt = f"""
You are an Indian education counsellor.

Student Details:
Rank: {rank}
State: {state}
Course: {course}

Available College Database:
{college_data}

Give college recommendation in simple Hinglish.

Answer format:
1. Best Colleges
2. Why suitable
3. Fees
4. Placement
5. Admission chance
6. Next steps

Do not invent colleges outside the database unless clearly saying "outside database suggestion".
"""
                ai_result = groq_generate(prompt, max_tokens=1200)
            except Exception as e:
                ai_result = f"AI error: {e}"
    else:
        form = CollegeRecommendationForm()

    return render(request, "accounts/recommend.html", {"form": form, "ai_result": ai_result})


@login_required(login_url='login')
def institute_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    institutes = Institute.objects.all().order_by('category', 'name')
    if query:
        institutes = institutes.filter(name__icontains=query)
    if category:
        institutes = institutes.filter(category=category)
    return render(request, 'accounts/institutes.html', {
        'institutes': institutes, 'query': query, 'category': category,
    })


@login_required(login_url='login')
def institute_detail(request, institute_id):
    institute = get_object_or_404(Institute, id=institute_id)
    return render(request, 'accounts/institute_detail.html', {'institute': institute})


@login_required(login_url='login')
def compare_institutes(request):
    institutes = Institute.objects.all()
    institute1 = institute2 = None
    if request.GET.get('i1') and request.GET.get('i2'):
        institute1 = Institute.objects.get(id=request.GET.get('i1'))
        institute2 = Institute.objects.get(id=request.GET.get('i2'))
    return render(request, 'accounts/compare.html', {
        'institutes': institutes, 'institute1': institute1, 'institute2': institute2,
    })


def counselling(request):
    if request.method == "POST":
        form = CounsellingLeadForm(request.POST)
        if form.is_valid():
            CounsellingLead.objects.create(
                name=form.cleaned_data['name'],
                mobile=form.cleaned_data['mobile'],
                email=form.cleaned_data['email'],
                interested_course=form.cleaned_data['interested_course'],
                message=form.cleaned_data['message'],
            )
            messages.success(request, "Your enquiry has been submitted successfully.")
            return redirect('counselling')
    else:
        form = CounsellingLeadForm()
    return render(request, 'accounts/counselling.html', {'form': form})


# ============================================================
# AI FEATURE VIEWS
# ============================================================

# ------ 1. SCHOLARSHIP FINDER ------

@login_required(login_url='login')
def scholarship_finder(request):
    """AI-powered scholarship recommendation system"""

    ai_recommendations = None
    eligible_scholarships = []

    if request.method == "POST":

        try:

            category = request.POST.get('category')
            state = request.POST.get('state')
            family_income = int(request.POST.get('family_income', 0))
            course = request.POST.get('course')
            academic_percentage = float(request.POST.get('academic_percentage', 0))


            student_profile, _ = StudentProfile.objects.get_or_create(
                user=request.user
            )

            student_profile.course_interest = course
            student_profile.academic_percentage = academic_percentage
            student_profile.save()



            eligible_scholarships = Scholarship.objects.filter(

                state=state,
                course=course,
                min_percentage__lte=academic_percentage,
                min_income__lte=family_income,
                max_income__gte=family_income,
                category__in=[category, 'merit_based']

            )



            scholarship_data = ""

            for scholarship in eligible_scholarships:

                scholarship_data += f"""

🎓 Scholarship Name:
{scholarship.name}

💰 Amount:
₹{scholarship.amount}

📅 Deadline:
{scholarship.application_deadline}

📄 Documents:
{scholarship.required_documents}

✅ Eligibility:
{scholarship.eligibility_criteria}

-------------------------

"""



            try:

                prompt = f"""

You are an AI Scholarship Advisor.

Your task is to recommend scholarships in a beautiful UI friendly format.

Student Details:

Category:
{category}

State:
{state}

Family Income:
₹{family_income}

Course:
{course}

Academic Percentage:
{academic_percentage}%


Available Scholarships:

{scholarship_data}



IMPORTANT RULES:

- Do NOT write long paragraphs.
- Do NOT use markdown tables.
- Make response look like modern application cards.
- Use emojis.
- Use bullet points.
- Keep spacing clean.


For every scholarship use this exact format:


🎓 Scholarship Name

⭐ Match Score:
(Example: 95% Suitable)


✨ Why This Scholarship Is Suitable:

Write 2-3 simple lines.


✅ Eligibility Requirements:

• Requirement 1
• Requirement 2
• Requirement 3


📄 Required Documents:

• Document 1
• Document 2


💡 Application Tips:

• Tip 1
• Tip 2


🚀 Next Steps:

Tell student what to do next.



Give maximum 3 best recommendations only.

"""



                ai_recommendations = groq_generate(
                    prompt,
                    max_tokens=1500
                )


            except Exception as e:

                messages.error(
                    request,
                    f"AI Analysis Error: {str(e)}"
                )



        except Exception as e:

            messages.error(
                request,
                f"Error processing scholarship finder: {str(e)}"
            )



    return render(
        request,
        'accounts/scholarship_finder.html',
        {

            'eligible_scholarships': eligible_scholarships,

            'ai_recommendations': ai_recommendations,

        }
    )


@login_required(login_url='login')
def apply_scholarship(request, scholarship_id):
    scholarship = get_object_or_404(Scholarship, id=scholarship_id)
    existing = ScholarshipApplication.objects.filter(user=request.user, scholarship=scholarship).first()
    if existing:
        messages.warning(request, f"You have already applied for {scholarship.name}")
        return redirect('scholarship_finder')

    ScholarshipApplication.objects.create(user=request.user, scholarship=scholarship, status='applied')
    messages.success(request, f"Applied for {scholarship.name} successfully!")
    try:
        send_mail(
            f"Scholarship Application - {scholarship.name}",
            f"You have successfully applied for {scholarship.name}.\n\nDeadline: {scholarship.application_deadline}\n\nRequired Documents: {scholarship.required_documents}",
            'edutrack@gmail.com',
            [request.user.email],
            fail_silently=True,
        )
    except Exception:
        pass
    return redirect('scholarship_finder')


@login_required(login_url='login')
def my_scholarships(request):
    applications = ScholarshipApplication.objects.filter(user=request.user).select_related('scholarship')
    return render(request, 'accounts/my_scholarships.html', {'applications': applications})


# ------ 2. COLLEGE COMPARISON ------

@login_required(login_url='login')
def college_comparison(request):
    colleges = College.objects.all()
    ai_analysis = None
    selected_colleges = []

    if request.method == "POST":
        college_ids = request.POST.getlist('colleges')
        if len(college_ids) < 2:
            messages.error(request, "Please select at least 2 colleges to compare")
            return redirect('college_comparison')

        selected_colleges = College.objects.filter(id__in=college_ids)
        comparison = CollegeComparison.objects.create(user=request.user)
        comparison.colleges.set(selected_colleges)

        college_data = ""
        for college in selected_colleges:
            college_data += f"""
College: {college.name}
City: {college.city}, State: {college.state}
Fees: ₹{college.fees}
Placement %: {college.placement_percentage}%
Average Package: ₹{college.average_package}
Highest Package: ₹{college.highest_package}
Rating: {college.rating}/5
Hostel: {'Available' if college.hostel_available else 'Not Available'}
Courses: {college.courses}
Facilities: {college.facilities}
Student Reviews: {college.student_reviews}
Distance: {college.distance_km} km
---
"""
        try:
            prompt = f"""
You are an expert education advisor.

Compare the following colleges:
{college_data}

Provide analysis:
1. Best choice overall and why
2. Pros and cons of each college
3. Best for placements
4. Best for academics
5. Best for affordability
6. Suitable student types for each
7. Final recommendation with reasoning
8. Questions to ask each college

Be comprehensive and help the student make an informed decision.
"""
            ai_analysis = groq_generate(prompt, max_tokens=1500)
            if ai_analysis:
                ai_analysis = ai_analysis.replace("•\n", "• ")
                ai_analysis = ai_analysis.replace("\n\n\n", "\n\n")  # Preserve line breaks for HTML display
            comparison.ai_analysis = ai_analysis
            comparison.save()
        except Exception as e:
            messages.error(request, f"AI Analysis Error: {str(e)}")

    return render(request, 'accounts/college_comparison.html', {
        'colleges': colleges,
        'selected_colleges': selected_colleges,
        'ai_analysis': ai_analysis,
    })


# ------ 3. ADMISSION DEADLINES ------

@login_required(login_url='login')
def admission_deadlines(request):
    today = timezone.now().date()
    upcoming_deadlines = AdmissionDeadline.objects.filter(deadline_date__gte=today).order_by('deadline_date')
    exams = Exam.objects.filter(registration_last_date__gte=today).order_by('exam_date')
    return render(request, 'accounts/admission_deadlines.html', {
        'upcoming_deadlines': upcoming_deadlines, 'exams': exams,
    })


@login_required(login_url='login')
def add_deadline(request):
    if request.method == "POST":
        try:
            deadline_type = request.POST.get('deadline_type')
            deadline_date = request.POST.get('deadline_date')
            description = request.POST.get('description')
            college_id = request.POST.get('college_id')
            college = College.objects.get(id=college_id) if college_id else None
            AdmissionDeadline.objects.create(
                college=college,
                deadline_type=deadline_type,
                deadline_date=deadline_date,
                description=description,
            )
            messages.success(request, "Deadline added successfully!")
            return redirect('admission_deadlines')
        except Exception as e:
            messages.error(request, f"Error adding deadline: {str(e)}")

    return render(request, 'accounts/add_deadline.html', {'colleges': College.objects.all()})


# ------ 4. SMART DASHBOARD ------

@login_required(login_url='login')
def smart_dashboard(request):
    user = request.user
    student_profile, _ = StudentProfile.objects.get_or_create(user=user)

    tasks = DashboardTask.objects.filter(user=user, completed=False).order_by('-priority', 'due_date')[:5]
    saved_colleges = list(SavedCollege.objects.filter(user=user).order_by('-id')[:3])
    applied_colleges = AppliedCollege.objects.filter(user=user)
    exam_recommendations = list(
        ExamRecommendation.objects.filter(user=user, status__in=['recommended', 'registered']).order_by('-id')[:3]
    )
    scholarship_apps = ScholarshipApplication.objects.filter(user=user)
    today = timezone.now().date()
    upcoming_deadlines = AdmissionDeadline.objects.filter(deadline_date__gte=today).order_by('deadline_date')[:5]

    ai_next_steps = None
    try:
        if student_profile.course_interest and student_profile.academic_percentage > 0:
            profile_data = f"""
Course Interest: {student_profile.course_interest}
Academic Percentage: {student_profile.academic_percentage}
Career Goal: {student_profile.career_goal}
Location: {student_profile.location}
Budget: ₹{student_profile.budget}
"""
            prompt = f"""
As an education advisor, based on this student profile:
{profile_data}

Suggest the next 3 important steps they should take:
1. Title
2. Why it's important
3. Timeline
4. How to do it

Keep it concise and actionable.
"""
            ai_next_steps = groq_generate(prompt, max_tokens=600)
    except Exception:
        ai_next_steps = None

    return render(request, 'accounts/smart_dashboard.html', {
        'student_profile': student_profile,
        'tasks': tasks,
        'saved_colleges': saved_colleges,
        'applied_colleges': applied_colleges,
        'exam_recommendations': exam_recommendations,
        'scholarship_apps': scholarship_apps,
        'upcoming_deadlines': upcoming_deadlines,
        'ai_next_steps': ai_next_steps,
    })


@login_required(login_url='login')
def student_profile_view(request):
    student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        try:
            student_profile.course_interest = request.POST.get('course_interest')
            student_profile.career_goal = request.POST.get('career_goal')
            student_profile.academic_percentage = float(request.POST.get('academic_percentage', 0))
            student_profile.location = request.POST.get('location')
            student_profile.budget = int(request.POST.get('budget', 0))
            student_profile.stream = request.POST.get('stream')
            student_profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('smart_dashboard')
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
    return render(request, 'accounts/student_profile.html', {'student_profile': student_profile})


# ------ 5. PARENT MODE ------

# ------ 5. PARENT MODE ------

@login_required(login_url='login')
def parent_register(request):
    if request.method == "POST":
        try:
            student_username = request.POST.get('student_username')
            relationship = request.POST.get('relationship')
            student = CustomUser.objects.get(username=student_username)
            ParentProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'student': student,
                    'relationship': relationship,
                    'phone_number': request.user.mobile,
                    'approved': True,
                }
            )
            messages.success(request, "Parent account linked successfully!")
            return redirect('parent_dashboard')
        except CustomUser.DoesNotExist:
            messages.error(request, "Student username not found")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return render(request, 'accounts/parent_register.html')


@login_required(login_url='login')
def parent_pending(request):
    return render(request, 'accounts/parent_waiting_approval.html')


@login_required(login_url='login')
def parent_dashboard(request):
    try:
        parent_profile = ParentProfile.objects.get(user=request.user)
        student = parent_profile.student
    except ParentProfile.DoesNotExist:
        messages.warning(request, "Please register as parent first")
        return redirect('parent_register')

    if not parent_profile.approved:
        return render(request, 'accounts/parent_waiting_approval.html')

    student_profile = StudentProfile.objects.filter(user=student).first()
    return render(request, 'accounts/parent_dashboard.html', {
        'student': student,
        'student_profile': student_profile,
        'saved_colleges': SavedCollege.objects.filter(user=student),
        'applied_colleges': AppliedCollege.objects.filter(user=student),
        'exam_recommendations': ExamRecommendation.objects.filter(user=student),
        'upcoming_deadlines': AdmissionDeadline.objects.filter(
            deadline_date__gte=timezone.now().date()
        ).order_by('deadline_date')[:5],
        'scholarship_apps': ScholarshipApplication.objects.filter(user=student),
    })


# ------ 6. AI CAREER GUIDANCE CHATBOT ------

@login_required(login_url='login')
def career_guidance(request):
    chat_session_id = request.session.get('career_chat_id')
    if not chat_session_id:
        chat_session_id = str(uuid.uuid4())
        request.session['career_chat_id'] = chat_session_id
        AIChat.objects.create(
            user=request.user,
            chat_session_id=chat_session_id,
            career_context=request.POST.get('career_context', ''),
        )

    try:
        ai_chat = AIChat.objects.get(chat_session_id=chat_session_id, user=request.user)
    except AIChat.DoesNotExist:
        ai_chat = AIChat.objects.create(user=request.user, chat_session_id=chat_session_id)

    if request.method == "POST" and request.POST.get('message'):
        message = request.POST.get('message')
        try:
            chat_history = ai_chat.messages if ai_chat.messages else []
            chat_history.append({'role': 'user', 'content': message, 'timestamp': timezone.now().isoformat()})

            prompt = f"""
            IMPORTANT:

Return clean readable format.

For Challenges section use:

⚠️ Challenges:

• Challenge 1
• Challenge 2
• Challenge 3

Never split words character by character.
You are an expert career guidance counselor. Help students explore career options and plan their future.

Student's previous context: {ai_chat.career_context}

Chat history:
{json.dumps(chat_history[-4:], indent=2)}

Respond helpfully to the student's question. Provide:
- Career options relevant to their question
- Required skills
- Job market insights
- Roadmap/steps
- Resources for learning

Keep responses concise but informative.
"""
            ai_response = groq_generate(prompt, max_tokens=800)
            chat_history.append({'role': 'assistant', 'content': ai_response, 'timestamp': timezone.now().isoformat()})
            ai_chat.messages = chat_history
            ai_chat.save()
        except Exception as e:
            pass  # silently skip on error

    messages_list = ai_chat.messages if ai_chat.messages else []
    return render(request, 'accounts/career_guidance.html', {'chat': ai_chat, 'messages': messages_list})


# ------ 7. EXAM RECOMMENDATIONS ------

@login_required(login_url='login')
def exam_recommendations(request):
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    if not student_profile or not student_profile.course_interest:
        messages.warning(request, "Please complete your profile first")
        return redirect('student_profile_view')

    return render(request, 'accounts/exam_recommendations.html', {
        'exams': Exam.objects.all(),
        'recommendations': ExamRecommendation.objects.filter(user=request.user),
        'student_profile': student_profile,
    })


@login_required(login_url='login')
def recommend_exams(request):
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    if not student_profile:
        return JsonResponse({'error': 'Student profile not found'}, status=404)

    try:
        prompt = f"""
Based on this student's profile:
- Course Interest: {student_profile.course_interest}
- Career Goal: {student_profile.career_goal}
- Academic Percentage: {student_profile.academic_percentage}%
- Stream: {student_profile.stream}

Recommend 3-5 entrance exams they should consider.
For each exam, provide:
1. Exam name
2. Why it's suitable
3. Preparation tips
4. Importance for their goals

Keep it concise and practical.
"""
        recommendations = groq_generate(prompt, max_tokens=800)
        return JsonResponse({'recommendations': recommendations})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================================
# FEATURE 1: AI ADMISSION PREDICTOR
# ============================================================

@login_required(login_url='login')
def admission_predictor(request):
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    form = AdmissionPredictionForm(initial={
        'student_name': request.user.get_full_name() or request.user.username,
        'percentage_12th': getattr(student_profile, 'academic_percentage', None),
        'state': getattr(student_profile, 'location', ''),
        'preferred_course': getattr(student_profile, 'course_interest', ''),
        'budget': getattr(student_profile, 'budget', None),
    })
    predictions = AdmissionPrediction.objects.filter(
        user=request.user
    ).select_related('college', 'entrance_exam')[:10]
    return render(request, 'accounts/admission_predictor.html', {'form': form, 'predictions': predictions})


@login_required(login_url='login')
@require_http_methods(['POST'])
def predict_admission(request):
    form = AdmissionPredictionForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)

    cleaned = form.cleaned_data
    college = cleaned['college']
    exam = cleaned['entrance_exam']
    ai_score = calculate_college_ai_score(college)

    try:
        prompt = f"""
Return only valid JSON for an Indian college admission prediction.
Keys: probability, category, reason, backup_colleges, better_options, required_cutoff.
Category must be one of: safe, moderate, dream.

Student:
Name: {cleaned['student_name']}
12th percentage: {cleaned['percentage_12th']}
Entrance exam: {exam.name}
Rank: {cleaned['exam_rank']}
Score: {cleaned['exam_score']}
Category: {cleaned['category']}
State: {cleaned['state']}
Preferred course: {cleaned['preferred_course']}
Budget INR: {cleaned['budget']}

College:
Name: {college.name}
Location: {college.city}, {college.state}
Fees INR: {college.fees}
Courses: {college.courses}
Placement: {college.placement_percentage}%
Average package INR: {college.average_package}
EduConnect score: {round(ai_score.overall_score, 1) if ai_score else 'not available'}
"""
        response_text = groq_generate(prompt, max_tokens=600)
        ai_data = extract_json_object(response_text, fallback_admission_prediction(cleaned, college))
    except Exception as exc:
        ai_data = fallback_admission_prediction(cleaned, college)
        ai_data['reason'] = f"{ai_data['reason']} AI service note: {exc}"

    category_type = str(ai_data.get('category', 'moderate')).lower()
    if category_type not in {'safe', 'moderate', 'dream'}:
        category_type = 'moderate'

    prediction = AdmissionPrediction.objects.create(
        user=request.user,
        student_name=cleaned['student_name'],
        percentage_12th=cleaned['percentage_12th'],
        entrance_exam=exam,
        exam_rank=cleaned['exam_rank'],
        exam_score=cleaned['exam_score'],
        category=cleaned['category'],
        state=cleaned['state'],
        preferred_course=cleaned['preferred_course'],
        budget=cleaned['budget'],
        college=college,
        admission_probability=clamp_number(ai_data.get('probability'), 0, 100),
        category_type=category_type,
        ai_analysis=ai_data.get('reason', ''),
        backup_colleges=ai_data.get('backup_colleges') or [],
        better_options=ai_data.get('better_options') or [],
        required_cutoff=ai_data.get('required_cutoff', ''),
    )

    return JsonResponse({
        'success': True,
        'prediction_id': prediction.id,
        'data': {
            'college': college.name,
            'probability': round(prediction.admission_probability),
            'category': prediction.category_type,
            'reason': prediction.ai_analysis,
            'backup_colleges': prediction.backup_colleges,
            'better_options': prediction.better_options,
            'required_cutoff': prediction.required_cutoff,
        }
    })


@login_required(login_url='login')
def prediction_history(request):
    predictions = AdmissionPrediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/prediction_history.html', {'predictions': predictions})


# ============================================================
# FEATURE 2: AI EDUCATION CHATBOT
# ============================================================

@login_required(login_url='login')
def education_chatbot(request):
    chat_session = AIChatSession.objects.filter(user=request.user).order_by('-updated_at').first()
    if not chat_session:
        chat_session = AIChatSession.objects.create(
            user=request.user, session_id=str(uuid.uuid4()), messages=[]
        )
    return render(request, 'accounts/education_chatbot.html', {'chat_session': chat_session})


@login_required(login_url='login')
@require_http_methods(['POST'])
def send_chat_message(request):
    user_message = request.POST.get('message', '').strip()
    session_id = request.POST.get('session_id', '').strip()

    if not user_message:
        return JsonResponse({'success': False, 'error': 'Please enter a message.'}, status=400)

    if session_id:
        chat_session = AIChatSession.objects.filter(user=request.user, session_id=session_id).first()
        if not chat_session:
            return JsonResponse({'success': False, 'error': 'Invalid chat session.'}, status=404)
    else:
        chat_session = AIChatSession.objects.create(
            user=request.user, session_id=str(uuid.uuid4()), messages=[]
        )

    student_profile = StudentProfile.objects.filter(user=request.user).first()
    colleges = College.objects.filter(
        city__icontains=getattr(student_profile, 'location', '')
    ).values('name', 'city', 'fees', 'courses')[:5] if student_profile else []

    history = "\n".join(
        f"{'Student' if item.get('sender') == 'user' else 'Advisor'}: {item.get('text', '')}"
        for item in chat_session.messages[-12:]
    )

    try:
        prompt = f"""
You are EduConnect AI, a practical education advisor for Indian students.
Use prior conversation context and give actionable answers with colleges, fees,
eligibility, exams, career scope, and roadmap when relevant.

Student profile:
Course interest: {getattr(student_profile, 'course_interest', '')}
Career goal: {getattr(student_profile, 'career_goal', '')}
Percentage: {getattr(student_profile, 'academic_percentage', '')}
Location: {getattr(student_profile, 'location', '')}
Budget INR: {getattr(student_profile, 'budget', '')}

Known nearby colleges from EduConnect DB: {list(colleges)}

Previous conversation:
{history}

Student question: {user_message}
"""
        ai_response = groq_generate(prompt, max_tokens=800)
    except Exception as exc:
        ai_response = (
            f"I could not reach the AI service right now. "
            f"Please check GROQ_API_KEY and try again. Details: {exc}"
        )

    messages_list = list(chat_session.messages)
    messages_list.append({'sender': 'user', 'text': user_message, 'timestamp': timezone.now().isoformat()})
    messages_list.append({'sender': 'ai', 'text': ai_response, 'timestamp': timezone.now().isoformat()})
    chat_session.messages = messages_list
    chat_session.total_messages = len(messages_list)
    chat_session.save(update_fields=['messages', 'total_messages', 'updated_at'])

    return JsonResponse({
        'success': True,
        'session_id': chat_session.session_id,
        'ai_response': ai_response,
        'total_messages': chat_session.total_messages,
    })


@login_required(login_url='login')
@require_http_methods(['POST'])
def clear_chat(request):
    session_id = request.POST.get('session_id', '').strip()
    chat_session = get_object_or_404(AIChatSession, user=request.user, session_id=session_id)
    chat_session.messages = []
    chat_session.total_messages = 0
    chat_session.save(update_fields=['messages', 'total_messages', 'updated_at'])
    return JsonResponse({'success': True})


# ============================================================
# FEATURE 3: CAREER ROADMAP GENERATOR
# ============================================================

@login_required(login_url='login')
def career_roadmap(request):
    form = CareerRoadmapForm(initial={'duration_months': 6})
    roadmaps = CareerRoadmap.objects.filter(
        user=request.user, status='active'
    ).prefetch_related('milestones')
    return render(request, 'accounts/career_roadmap.html', {'form': form, 'roadmaps': roadmaps})


@login_required(login_url='login')
@require_http_methods(['POST'])
def generate_roadmap(request):
    form = CareerRoadmapForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)

    cleaned = form.cleaned_data
    duration = min(max(cleaned['duration_months'], 1), 24)

    try:
        prompt = f"""
Create a {duration}-month career roadmap. Return only valid JSON with:
milestones: list of objects containing month, title, description, skills_to_learn, resources.
summary, success_tips, challenges.

Course: {cleaned['course']}
Interest: {cleaned['interest']}
Current skills: {cleaned['skills']}
Career goal: {cleaned['career_goal']}
"""
        roadmap_data = extract_json_object(groq_generate(prompt, max_tokens=1500), {})
    except Exception:
        roadmap_data = {}

    if not roadmap_data.get('milestones'):
        roadmap_data = {
            'summary': f"A focused {duration}-month path toward {cleaned['career_goal']}.",
            'success_tips': ['Build weekly projects', 'Track progress in a portfolio', 'Apply for internships early'],
            'challenges': ['Consistency', 'Interview practice', 'Project quality'],
            'milestones': [
                {
                    'month': 1, 'title': 'Foundation',
                    'description': 'Strengthen fundamentals and set up a learning plan.',
                    'skills_to_learn': ['Core concepts', 'Practice routine'],
                    'resources': ['Official docs', 'Beginner project'],
                },
                {
                    'month': 2, 'title': 'Core Skills',
                    'description': 'Learn the main tools required for the target role.',
                    'skills_to_learn': ['Python or JavaScript', 'SQL'],
                    'resources': ['Hands-on tutorials', 'Mini project'],
                },
                {
                    'month': 3, 'title': 'Project Building',
                    'description': 'Create a real project connected to your interest area.',
                    'skills_to_learn': ['Django or relevant framework', 'Git'],
                    'resources': ['GitHub portfolio', 'Deployment guide'],
                },
                {
                    'month': min(duration, 6), 'title': 'Internship Preparation',
                    'description': 'Prepare resume, portfolio, aptitude, and interviews.',
                    'skills_to_learn': ['Resume writing', 'Interview practice'],
                    'resources': ['Mock interviews', 'LinkedIn profile'],
                },
            ],
        }

    roadmap = CareerRoadmap.objects.create(
        user=request.user,
        course=cleaned['course'],
        interest=cleaned['interest'],
        skills=cleaned['skills'],
        career_goal=cleaned['career_goal'],
        duration_months=duration,
        roadmap_data=roadmap_data,
        ai_analysis=roadmap_data.get('summary', ''),
    )
    for item in roadmap_data.get('milestones', []):
        RoadmapMilestone.objects.create(
            roadmap=roadmap,
            month=int(item.get('month') or 1),
            title=item.get('title', 'Milestone'),
            description=item.get('description', ''),
            skills_to_learn=item.get('skills_to_learn') or [],
            resources=item.get('resources') or [],
        )

    return JsonResponse({'success': True, 'roadmap_id': roadmap.id, 'redirect_url': f'/roadmap/{roadmap.id}/'})


@login_required(login_url='login')
def view_roadmap(request, roadmap_id):
    roadmap = get_object_or_404(CareerRoadmap, id=roadmap_id, user=request.user)
    milestones = RoadmapMilestone.objects.filter(roadmap=roadmap).order_by('month')
    return render(request, 'accounts/view_roadmap.html', {'roadmap': roadmap, 'milestones': milestones})


# ============================================================
# FEATURE 4: COLLEGE AI SCORE SYSTEM
# ============================================================

def calculate_college_ai_score(college):
    reviews = CollegeReview.objects.filter(college=college, is_spam=False)
    avg_overall = reviews.aggregate(models.Avg('overall_rating'))['overall_rating__avg']
    avg_teaching = reviews.aggregate(models.Avg('teaching_rating'))['teaching_rating__avg']
    avg_campus = reviews.aggregate(models.Avg('campus_rating'))['campus_rating__avg']

    placement_score = min(100, max(0, college.placement_percentage or 0))
    fees_score = max(0, min(100, 100 - ((college.fees or 0) / 500000 * 100)))
    review_score = (avg_overall or college.rating or 0) * 20
    faculty_score = (avg_teaching * 20) if avg_teaching else max(40, placement_score * 0.8)
    campus_score = (avg_campus * 20) if avg_campus else max(0, min(100, (college.average_package or 0) / 800000 * 100))
    overall_score = (
        placement_score * 0.35 +
        fees_score * 0.20 +
        review_score * 0.20 +
        faculty_score * 0.15 +
        campus_score * 0.10
    )
    category = (
        'tier1' if overall_score >= 85 else
        'tier2' if overall_score >= 70 else
        'tier3' if overall_score >= 55 else
        'tier4'
    )
    score, _ = CollegeAIScore.objects.update_or_create(
        college=college,
        defaults={
            'placement_score': round(placement_score),
            'fees_score': round(fees_score),
            'review_score': round(review_score),
            'faculty_score': round(faculty_score),
            'campus_score': round(campus_score),
            'overall_score': round(overall_score, 2),
            'category': category,
            'ai_summary': 'Score uses placement 35%, fees 20%, reviews 20%, faculty 15%, and campus 10%.',
        }
    )
    return score


@login_required(login_url='login')
def college_scores(request):
    min_score = request.GET.get('score')
    sort_by = request.GET.get('sort', '-overall_score')
    scored_colleges = [(college, calculate_college_ai_score(college)) for college in College.objects.all()]

    if min_score:
        try:
            scored_colleges = [item for item in scored_colleges if item[1].overall_score >= float(min_score)]
        except ValueError:
            pass

    if sort_by == 'fees':
        scored_colleges.sort(key=lambda item: item[0].fees)
    elif sort_by == 'placement':
        scored_colleges.sort(key=lambda item: item[0].placement_percentage, reverse=True)
    else:
        scored_colleges.sort(key=lambda item: item[1].overall_score, reverse=True)

    return render(request, 'accounts/college_scores.html', {
        'scored_colleges': scored_colleges,
        'filter_score': min_score or '',
        'sort_by': sort_by,
    })


# ============================================================
# FEATURE 5: STUDENT REVIEW SYSTEM
# ============================================================

def detect_review_spam(review_text, user, college):
    text = review_text.strip()
    lowered = text.lower()
    spam_score = 0.0
    reasons = []
    if len(text) < 40:
        spam_score += 0.35
        reasons.append('too short')
    if len(set(lowered.split())) < max(4, len(lowered.split()) / 3):
        spam_score += 0.20
        reasons.append('repetitive wording')
    if any(w in lowered for w in ['http://', 'https://', 'buy now', 'discount', 'earn money']):
        spam_score += 0.30
        reasons.append('promotional language')
    if CollegeReview.objects.filter(user=user, college=college).exists():
        spam_score += 0.25
        reasons.append('duplicate user review')
    return min(spam_score, 1.0), reasons


@login_required(login_url='login')
def college_reviews(request, college_id):
    college = get_object_or_404(College, id=college_id)
    score = calculate_college_ai_score(college)
    reviews = CollegeReview.objects.filter(college=college, is_spam=False).select_related('user')
    avg_rating = reviews.aggregate(models.Avg('overall_rating'))['overall_rating__avg'] or 0
    return render(request, 'accounts/college_reviews.html', {
        'college': college, 'score': score, 'reviews': reviews, 'avg_rating': avg_rating,
    })


@login_required(login_url='login')
def add_review(request, college_id):
    college = get_object_or_404(College, id=college_id)
    existing = CollegeReview.objects.filter(user=request.user, college=college).first()

    if request.method == 'POST':
        form = CollegeReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.college = college
            spam_score, reasons = detect_review_spam(review.review_text, request.user, college)
            review.spam_score = spam_score
            review.is_spam = spam_score >= 0.65
            review.save()
            calculate_college_ai_score(college)
            if review.is_spam:
                messages.warning(request, f'Review saved for moderation: {", ".join(reasons)}.')
            else:
                messages.success(request, 'Review submitted successfully.')
            return redirect('college_reviews', college_id=college.id)
    else:
        form = CollegeReviewForm(instance=existing)

    return render(request, 'accounts/add_review.html', {'college': college, 'form': form, 'existing': existing})


# ============================================================
# FEATURE 6: EDUCATION COST CALCULATOR
# ============================================================

@login_required(login_url='login')
def cost_calculator(request):
    form = CostCalculationForm()
    calculations = CostCalculation.objects.filter(user=request.user).select_related('college')[:10]
    return render(request, 'accounts/cost_calculator.html', {'form': form, 'calculations': calculations})


@login_required(login_url='login')
@require_http_methods(['POST'])
def calculate_cost(request):
    form = CostCalculationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)

    cleaned = form.cleaned_data
    annual_total = (
        cleaned['annual_fees'] +
        cleaned['hostel_fees'] +
        cleaned['travel_costs'] +
        cleaned['books_materials'] +
        cleaned['miscellaneous']
    )
    total_cost = annual_total * cleaned['duration']
    net_cost = max(0, total_cost - cleaned['scholarship'])

    calculation = CostCalculation.objects.create(
        user=request.user,
        college=cleaned['college'],
        course_name=cleaned['course_name'],
        annual_fees=cleaned['annual_fees'],
        hostel_fees=cleaned['hostel_fees'],
        travel_costs=cleaned['travel_costs'],
        books_materials=cleaned['books_materials'],
        miscellaneous=cleaned['miscellaneous'],
        course_duration_years=cleaned['duration'],
        total_cost=total_cost,
        annual_total=annual_total,
        estimated_scholarship=cleaned['scholarship'],
        net_cost=net_cost,
    )

    return JsonResponse({
        'success': True,
        'calculation_id': calculation.id,
        'data': {
            'annual_total': annual_total,
            'total_cost': total_cost,
            'net_cost': net_cost,
            'per_month': round(net_cost / (cleaned['duration'] * 12), 2),
        },
    })
def parent_register(request):

    if request.method == "POST":

        student_username = request.POST.get(
            "student_username"
        )

        relationship = request.POST.get(
            "relationship"
        )


        try:

            student = CustomUser.objects.get(
                username=student_username,
                user_type="student"
            )


            ParentProfile.objects.update_or_create(
    user=request.user,
    defaults={
        "student": student,
        "relationship": relationship
    }
)
            

            messages.success(
                request,
                "Parent request sent successfully"
            )


            return redirect(
                "parent_pending"
            )


        except CustomUser.DoesNotExist:


            messages.error(
                request,
                "Student username not found"
            )


    return render(
        request,
        "accounts/parent_register.html"
    )
def parent_pending(request):
    return render(request, 'accounts/parent_pending.html')