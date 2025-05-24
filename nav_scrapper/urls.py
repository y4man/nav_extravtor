from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('results/<int:website_id>/', views.results, name='results'),
    path('stop', views.stop_extraction, name='stop_extraction'),

]
