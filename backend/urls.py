from django.contrib import admin
from django.urls import path, include

# for images
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html")),
    path("api/products/", include("base.urls.product_url")),
    path("api/users/", include("base.urls.user_url")),
    path("api/orders/", include("base.urls.order_url")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
