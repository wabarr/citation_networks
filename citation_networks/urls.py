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
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', login_required(PaperListView.as_view())),
    path('admin/', admin.site.urls),
    path('papers/', login_required(PaperListView.as_view())),
    path('papers/<pk>', login_required(ImportCitationsFormViewFromPaperDetail.as_view()) , name="paper-detail"),
    path('authors/<pk>', login_required(AuthorDetailView.as_view()), name="author-detail"),
    path('import-citations/', login_required(ImportCitationsFormView.as_view())),
    path('network/', login_required(NetworkView.as_view())),
    path('network-json/', login_required(NetworkJSON.as_view())),
    path('network-json/<pk>', login_required(NetworkJSONDetail.as_view())),
    path('accounts/login/', auth_views.LoginView.as_view())]
