from django.urls import path
from .views import SubmitFeedbackView, MyFeedbackListView

urlpatterns = [
    path('submit/', SubmitFeedbackView.as_view(), name='feedback-submit'),
    path('my/', MyFeedbackListView.as_view(), name='feedback-list'),
]
