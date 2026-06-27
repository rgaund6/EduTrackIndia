from django.contrib import admin
from .models import (
    AdmissionPrediction,
    AIChatSession,
    CareerRoadmap,
    College,
    CollegeAIScore,
    CollegeReview,
    CostCalculation,
    CounsellingLead,
    CustomUser,
    EmailOTP,
    Exam,
    Institute,
    Notification,
    RoadmapMilestone,
    SavedCollege,
)

admin.site.register(CustomUser)
admin.site.register(College)
admin.site.register(Exam)
admin.site.register(Notification)
admin.site.register(SavedCollege)
admin.site.register(EmailOTP)
admin.site.register(Institute)
admin.site.register(CounsellingLead)
admin.site.register(AdmissionPrediction)
admin.site.register(AIChatSession)
admin.site.register(CareerRoadmap)
admin.site.register(RoadmapMilestone)
admin.site.register(CollegeAIScore)
admin.site.register(CollegeReview)
admin.site.register(CostCalculation)
