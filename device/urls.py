from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.checkOnline, name='user-info-api'),
    path('getusers/', views.getUsers, name='user-online-check-api'),
    path('getCount/', views.getCount, name='user-face-count'),
    path('addUserTemplate/', views.addUserTemplate, name="add-user-template-to-device"),
    path('blockUsers/', views.blockUser, name='block-users')
    # path('photoUpload/', views.uploadPhoto, name='upload-user-photo')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)