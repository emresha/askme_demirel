"""askme_demirel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls.static import static
from app import views
from askme_demirel import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('hot/', views.hot, name="hot"),
    path('tag/<str:tag_name>', views.tag, name="tag"),
    path('ask/', views.ask, name="ask"),
    path('login/', views.login, name="login"),
    path('signup/', views.signup, name="signup"),
    path('question/<int:id>', views.question, name="question"),
    path('settings/', views.settings, name="settings"),
    path('logout/', views.logout, name="logout"),
    path('toggle_question_like/', views.toggle_question_like, name='toggle_like'),
    path('toggle_comment_like/', views.toggle_comment_like, name='toggle_answer_like'),
    path('mark_correct/', views.mark_correct, name='mark_correct'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
