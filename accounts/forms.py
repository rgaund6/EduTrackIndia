from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    AdmissionPrediction,
    CareerRoadmap,
    CollegeReview,
    CostCalculation,
    CustomUser,
)

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'mobile',
            'password1',
            'password2'
        ]


class CollegeRecommendationForm(forms.Form):
    rank = forms.IntegerField(
        label="Your Rank"
    )

    state = forms.CharField(
        max_length=100,
        label="State"
    )

    course = forms.CharField(
        max_length=100,
        label="Course"
    )
class CounsellingLeadForm(forms.Form):
    name = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=15)
    email = forms.EmailField()
    interested_course = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea, required=False)


class BootstrapModelForm(forms.ModelForm):
    """Apply Bootstrap classes without repeating widget definitions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = field.widget.attrs.get('class', css_class)


class AdmissionPredictionForm(BootstrapModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].required = True

    class Meta:
        model = AdmissionPrediction
        fields = [
            'student_name',
            'percentage_12th',
            'entrance_exam',
            'exam_rank',
            'exam_score',
            'category',
            'state',
            'preferred_course',
            'budget',
            'college',
        ]
        labels = {
            'percentage_12th': '12th percentage',
            'exam_rank': 'Rank',
            'exam_score': 'Score',
        }


class CareerRoadmapForm(BootstrapModelForm):
    duration_months = forms.IntegerField(min_value=1, max_value=24, initial=6, label='Duration in months')

    class Meta:
        model = CareerRoadmap
        fields = ['course', 'interest', 'skills', 'career_goal', 'duration_months']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
            'career_goal': forms.Textarea(attrs={'rows': 3}),
        }


class CollegeReviewForm(BootstrapModelForm):
    class Meta:
        model = CollegeReview
        fields = [
            'teaching_rating',
            'placement_rating',
            'hostel_rating',
            'campus_rating',
            'fees_rating',
            'overall_rating',
            'review_text',
        ]
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Share specific details about academics, placements, campus, and fees.'}),
        }


class CostCalculationForm(BootstrapModelForm):
    duration = forms.IntegerField(min_value=1, max_value=10, initial=4, label='Course duration in years')
    scholarship = forms.IntegerField(min_value=0, initial=0, label='Estimated scholarship')

    class Meta:
        model = CostCalculation
        fields = [
            'college',
            'course_name',
            'annual_fees',
            'hostel_fees',
            'travel_costs',
            'books_materials',
            'miscellaneous',
        ]
