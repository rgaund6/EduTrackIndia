from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True)
    email_verified = models.BooleanField(default=False)
    mobile_verified = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=20,
        choices=[('student', 'Student'), ('parent', 'Parent')],
        default='student'
    )

    def __str__(self):
        return self.username


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    course_interest = models.CharField(max_length=100, blank=True)
    career_goal = models.CharField(max_length=255, blank=True)
    academic_percentage = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    entrance_exam_score = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    budget = models.IntegerField(default=0, blank=True)
    stream = models.CharField(
        max_length=50,
        choices=[('science', 'Science'), ('commerce', 'Commerce'), ('arts', 'Arts')],
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Profile"


class ParentProfile(models.Model):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_parents',
        limit_choices_to={'user_type':'student'}
    )

    relationship = models.CharField(
        max_length=20,
        choices=[
            ('father','Father'),
            ('mother','Mother'),
            ('guardian','Guardian')
        ]
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    approved = models.BooleanField(
        default=False
    )

    created_at=models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return f"{self.user.username} - {self.student.username}"

    def __str__(self):
        return f"{self.user.username} - Parent of {self.student.username}"


class College(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    fees = models.IntegerField()
    placement_percentage = models.IntegerField()
    average_package = models.IntegerField(default=0)
    highest_package = models.IntegerField(default=0)
    official_website = models.URLField()
    courses = models.TextField()
    hostel_available = models.BooleanField(default=False)
    hostel_fees = models.IntegerField(default=0, blank=True)
    facilities = models.TextField(default="")
    student_reviews = models.TextField(default="")
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    distance_km = models.FloatField(default=0, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    established_year = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class Exam(models.Model):
    name = models.CharField(max_length=100)
    exam_date = models.DateField()
    registration_last_date = models.DateField()
    official_website = models.URLField()
    description = models.TextField()

    def __str__(self):
        return self.name
    def __str__(self):
        return self.name
class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title    
class SavedCollege(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE
    )

    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.college.name}" 
class EmailOTP(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username   
class Institute(models.Model):
    CATEGORY_CHOICES = [
        ('Pre-Primary Schools', 'Pre-Primary Schools'),
        ('Primary to Higher Secondary', 'Primary to Higher Secondary'),
        ('Colleges', 'Colleges'),
    ]

    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name
    
class CounsellingLead(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    interested_course = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# AI-Powered Feature Models

class Scholarship(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('sc_st', 'SC/ST'),
        ('obc', 'OBC'),
        ('minority', 'Minority'),
        ('girl_child', 'Girl Child'),
        ('disability', 'Disability'),
        ('merit_based', 'Merit-Based'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    state = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    amount = models.IntegerField()
    min_income = models.IntegerField()
    max_income = models.IntegerField()
    min_percentage = models.FloatField(default=0)
    application_deadline = models.DateField()
    required_documents = models.TextField()
    application_steps = models.TextField()
    eligibility_criteria = models.TextField()
    website_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.state}"


class ScholarshipApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='scholarship_applications')
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    application_date = models.DateTimeField(auto_now_add=True)
    documents_submitted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.scholarship.name}"


class AdmissionDeadline(models.Model):
    DEADLINE_TYPE_CHOICES = [
        ('exam', 'Exam Registration'),
        ('application', 'Application Deadline'),
        ('admission', 'Admission Registration'),
        ('counselling', 'Counselling Date'),
    ]

    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='admission_deadlines', null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='admission_deadlines', null=True, blank=True)
    deadline_type = models.CharField(max_length=50, choices=DEADLINE_TYPE_CHOICES)
    deadline_date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deadline_type} - {self.deadline_date}"


class AppliedCollege(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('admission_confirmed', 'Admission Confirmed'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applied_colleges')
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    application_date = models.DateTimeField(auto_now_add=True)
    application_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.college.name}"


class CollegeComparison(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='college_comparisons')
    colleges = models.ManyToManyField(College)
    ai_analysis = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comparison by {self.user.username}"


class AIChat(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ai_chats')
    chat_session_id = models.CharField(max_length=100, unique=True)
    messages = models.JSONField(default=list)
    career_context = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat - {self.user.username}"


class DashboardTask(models.Model):
    TASK_TYPES = [
        ('profile', 'Complete Profile'),
        ('scholarship', 'Apply for Scholarship'),
        ('exam_prep', 'Prepare for Entrance Exam'),
        ('college_compare', 'Compare Colleges'),
        ('counsellor', 'Contact Counsellor'),
        ('application', 'Submit Application'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='dashboard_tasks')
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class ExamRecommendation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='exam_recommendations')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('recommended', 'Recommended'), ('registered', 'Registered'), ('completed', 'Completed')],
        default='recommended'
    )
    ai_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam.name} - {self.user.username}"


# ===== FEATURE 1: AI ADMISSION PREDICTOR =====
class AdmissionPrediction(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('obc', 'OBC'),
        ('sc', 'SC'),
        ('st', 'ST'),
        ('ews', 'EWS'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admission_predictions')
    student_name = models.CharField(max_length=255)
    percentage_12th = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    entrance_exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True, blank=True)
    exam_rank = models.IntegerField()
    exam_score = models.IntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    state = models.CharField(max_length=100)
    preferred_course = models.CharField(max_length=100)
    budget = models.IntegerField()
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='admission_predictions')
    
    # AI Prediction Results
    admission_probability = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    category_type = models.CharField(max_length=20, choices=[('safe', 'Safe'), ('moderate', 'Moderate'), ('dream', 'Dream')], default='moderate')
    ai_analysis = models.TextField(blank=True)
    backup_colleges = models.JSONField(default=list, blank=True)
    better_options = models.JSONField(default=list, blank=True)
    required_cutoff = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student_name} - {self.college.name}"


# ===== FEATURE 2: AI CHAT SESSION (Enhanced) =====
class AIChatSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ai_chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    messages = models.JSONField(default=list)  # Store conversation history
    context_data = models.JSONField(default=dict, blank=True)  # Store context for better responses
    total_messages = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat Session - {self.user.username}"


# ===== FEATURE 3: CAREER ROADMAP GENERATOR =====
class CareerRoadmap(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='career_roadmaps')
    course = models.CharField(max_length=100)
    interest = models.CharField(max_length=255)
    skills = models.TextField()
    career_goal = models.CharField(max_length=255)
    
    roadmap_data = models.JSONField(default=dict)  # Store the entire roadmap
    ai_analysis = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    duration_months = models.IntegerField(default=12)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Roadmap - {self.user.username} - {self.career_goal}"


class RoadmapMilestone(models.Model):
    roadmap = models.ForeignKey(CareerRoadmap, on_delete=models.CASCADE, related_name='milestones')
    month = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills_to_learn = models.JSONField(default=list)
    resources = models.JSONField(default=list)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['month']

    def __str__(self):
        return f"Month {self.month} - {self.title}"


# ===== FEATURE 4: COLLEGE AI SCORE =====
class CollegeAIScore(models.Model):
    college = models.OneToOneField(College, on_delete=models.CASCADE, related_name='ai_score')
    
    # Individual scores (0-100)
    placement_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    fees_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    review_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    faculty_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    campus_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Overall score calculation: (placement*0.35 + fees*0.2 + reviews*0.2 + faculty*0.15 + campus*0.1)
    overall_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Ranking and categorization
    rank = models.IntegerField(default=0)
    category = models.CharField(max_length=50, default='tier2', choices=[
        ('tier1', 'Tier 1 - Excellent'),
        ('tier2', 'Tier 2 - Very Good'),
        ('tier3', 'Tier 3 - Good'),
        ('tier4', 'Tier 4 - Average'),
    ])
    
    ai_summary = models.TextField(blank=True)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.college.name} - Score: {self.overall_score}"


# ===== FEATURE 5: COLLEGE REVIEWS =====
class CollegeReview(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='college_reviews')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='reviews')
    
    # Individual ratings (1-5 stars)
    teaching_rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    placement_rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    hostel_rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    campus_rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    fees_rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    
    # Overall review
    overall_rating = models.IntegerField(choices=RATING_CHOICES, default=3)
    review_text = models.TextField()
    
    # Spam detection
    is_spam = models.BooleanField(default=False)
    spam_score = models.FloatField(default=0)  # 0-1, higher = more likely spam
    
    helpful_count = models.IntegerField(default=0)
    is_verified_student = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'college']

    def __str__(self):
        return f"Review by {self.user.username} - {self.college.name}"


# ===== FEATURE 6: EDUCATION COST CALCULATOR =====
class CostCalculation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cost_calculations')
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=100)
    
    # Cost breakdown (per year)
    annual_fees = models.IntegerField()
    hostel_fees = models.IntegerField(default=0)
    travel_costs = models.IntegerField(default=0)
    books_materials = models.IntegerField(default=0)
    miscellaneous = models.IntegerField(default=0)
    
    # Durations
    course_duration_years = models.IntegerField(default=4)
    
    # Total calculations
    total_cost = models.IntegerField()  # Total for entire course
    annual_total = models.IntegerField()  # Annual total
    
    # Financial aid info
    estimated_scholarship = models.IntegerField(default=0)
    net_cost = models.IntegerField()  # Total - scholarship
    
    # Additional info
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cost Calc - {self.user.username} - {self.college.name}"
    
    