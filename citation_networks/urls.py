"""citation_networks URL Configuration

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
from citation_networks.views import *
urlpatterns = [
    path('', PaperListView.as_view()),
    path('admin/', admin.site.urls),
    path('papers/', PaperListView.as_view()),
    path('papers/<pk>', ImportCitationsFormViewFromPaperDetail.as_view(), name="paper-detail"),
    path('authors/<pk>', AuthorDetailView.as_view(), name="author-detail"),
    path('import-citations/', ImportCitationsFormView.as_view()),
    path('network/', NetworkView.as_view()),
    path('network-json/', NetworkJSON.as_view())
]
