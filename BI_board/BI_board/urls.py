from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core BI Platform URLs (to be created)
    # path("api/data-pipeline/", include("apps.data_pipeline.urls")),
    # path("api/ml-engine/", include("apps.ml_engine.urls")),
    # path("api/social/", include("apps.social_intelligence.urls")),
    # path("api/payments/", include("apps.payments.urls")),
    # path("api/website/", include("apps.website_intelligence.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)