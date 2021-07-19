"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import employee

from employee.views import EmployeeImage, EmpImageDisplay

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', employee.views.login),
    path('login_submit/', employee.views.login_submit),
    path('logout', employee.views.logout),
    path('landing', employee.views.landing),
    path('works', employee.views.works),
    path('face_reco/', EmployeeImage.as_view(), name='home'),
    path('digital_makeup/',employee.views.digital_makeup),
    path('find_face/',employee.views.find_face),
    path('face_recognition/',employee.views.face_recog),
    path('find_facial_feature/',employee.views.find_facial_feature),
    path('video_detection/',employee.views.video_detection),
    
    path('emp-image/<int:pk>/', EmpImageDisplay.as_view(), name='emp_image_display'),
]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)