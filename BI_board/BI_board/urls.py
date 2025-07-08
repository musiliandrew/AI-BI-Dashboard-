from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # app-specific URLs
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/data-ingestion/", include("apps.data_ingestion.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/", include("apps.organizations.urls")),  # SaaS organization endpoints
    path("api/ai-chat/", include("apps.ai_chat.urls")),  # AI Data Scientist Chat
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)