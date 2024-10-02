from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calculator/', views.calculator_view, name='calculator'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('route-optimization/', views.route_optimization_view, name='route-optimization'),
    path('compliance-management/', views.compliance_management_view, name='compliance-management'),
    path('real-time-tracking/', views.real_time_tracking_view, name='real-time-tracking'),
    path('permit-assistance/', views.permit_assistance_view, name='permit-assistance'),
    path('load-simulation/', views.load_simulation_view, name='load-simulation'),
    path('weather-integration/', views.weather_integration_view, name='weather-integration'),
    path('av-number/', views.av_number_view, name='av-number'),
    path('account/', views.account_view, name='account'), 
    path('constants/', views.constants_view, name='constants'),  
]