from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NewsArticleViewSet,
    FetchNewsAPIView,
    CategoryListView,
    ClearNewsAPIView
)

router = DefaultRouter()
router.register('articles', NewsArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('fetch-news/', FetchNewsAPIView.as_view(), name='fetch-news'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('clear-news/', ClearNewsAPIView.as_view(), name='clear-news'),
]
