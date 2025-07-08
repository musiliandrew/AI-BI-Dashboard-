from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChatSessionViewSet, ChatMessageViewSet, UserContextView,
    QuickChatView, DataInsightView, DiscoverInsightsView
)

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='chat-sessions')
router.register(r'messages', ChatMessageViewSet, basename='chat-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('context/', UserContextView.as_view(), name='user-context'),
    path('quick-chat/', QuickChatView.as_view(), name='quick-chat'),
    path('insights/', DataInsightView.as_view(), name='data-insights'),
    path('discover-insights/', DiscoverInsightsView.as_view(), name='discover-insights'),
]
