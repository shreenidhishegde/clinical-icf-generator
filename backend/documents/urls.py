from django.urls import path
from .views import GenerateICFView, DownloadICF

urlpatterns = [
    path("generate_icf/", GenerateICFView.as_view(), name="generate-icf"),
    path("download_icf/", DownloadICF.as_view(), name="download-icf"),
]