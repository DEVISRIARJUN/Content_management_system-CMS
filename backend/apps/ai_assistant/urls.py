from django.urls import path
from .views import ReadabilityAnalysisView, SeoSuggestionsView, SmartTagSuggesterView, SummarizerView

urlpatterns = [
    path('readability/', ReadabilityAnalysisView.as_view(), name='ai-readability'),
    path('seo/', SeoSuggestionsView.as_view(), name='ai-seo'),
    path('suggest-tags/', SmartTagSuggesterView.as_view(), name='ai-tags'),
    path('summarize/', SummarizerView.as_view(), name='ai-summarize'),
]
