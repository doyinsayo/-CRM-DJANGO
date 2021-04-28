from django.urls import path
import leads
from leads import views
from .views import lead_list


app_name = 'leads'

urlpatterns = [
    path('',views.lead_list,name='lead_list'),
]