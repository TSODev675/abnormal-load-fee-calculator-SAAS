from django.shortcuts import render
import requests
from django.http import JsonResponse

# Coordinates for each province in South Africa and Namibia
COUNTRY_PROVINCES_COORDINATES = {
    'South Africa': {
        'Eastern Cape': {'latitude': -32.2968, 'longitude': 26.4194},
        'Free State': {'latitude': -28.4541, 'longitude': 26.7968},
        'Gauteng': {'latitude': -26.2708, 'longitude': 28.1123},
        'KwaZulu-Natal': {'latitude': -29.8587, 'longitude': 31.0218},
        'Limpopo': {'latitude': -23.4013, 'longitude': 29.4179},
        'Mpumalanga': {'latitude': -25.5658, 'longitude': 30.5279},
        'Northern Cape': {'latitude': -29.0467, 'longitude': 21.8569},
        'North West': {'latitude': -25.3848, 'longitude': 25.6493},
        'Western Cape': {'latitude': -33.9249, 'longitude': 18.4241}
    },
    'Namibia': {
        'Erongo': {'latitude': -22.0222, 'longitude': 14.5341},
        'Hardap': {'latitude': -24.1674, 'longitude': 17.3413},
        'Karas': {'latitude': -27.3943, 'longitude': 18.7269},
        'Khomas': {'latitude': -22.5597, 'longitude': 17.0832},
        'Kunene': {'latitude': -19.2333, 'longitude': 13.5450},
        'Oshana': {'latitude': -17.6956, 'longitude': 15.4730},
        'Oshikoto': {'latitude': -18.3765, 'longitude': 16.5832},
        'Otjozondjupa': {'latitude': -20.4364, 'longitude': 17.1538},
        'Zambezi': {'latitude': -17.5034, 'longitude': 24.2698}
    }
}

# View for the main calculator page
def calculator_view(request): 
    return render(request, 'dashboard/calculator.html')

# View for the profile page
def profile_view(request):
    return render(request, 'landing/profile.html')

# View for the index (landing) page with features and pricing plans
def index(request):
    context = {
        'features': [
            {'title': 'Route Optimization', 'description': 'Efficiently plan your routes considering road restrictions and regulations.', 'icon': 'fas fa-route'},
            {'title': 'Compliance Management', 'description': 'Stay up-to-date with local and international transport regulations.', 'icon': 'fas fa-clipboard-check'},
            {'title': 'Real-time Tracking', 'description': 'Monitor your abnormal loads in real-time for better coordination.', 'icon': 'fas fa-satellite-dish'},
            {'title': 'Permit Assistance', 'description': 'Streamline the process of obtaining necessary permits for your transports.', 'icon': 'fas fa-file-alt'},
            {'title': 'Load Simulation', 'description': 'Simulate your load on various road types to ensure safe transport.', 'icon': 'fas fa-truck-loading'},
            {'title': 'Weather Integration', 'description': 'Get real-time weather updates along your planned routes.', 'icon': 'fas fa-cloud-sun-rain'},
        ],
        'pricing_plans': [
            {'name': 'Basic', 'price': 99, 'features': ['Route optimization', 'Basic compliance alerts', '5 vehicle tracking', 'Email support']},
            {'name': 'Pro', 'price': 199, 'features': ['All Basic features', 'Advanced compliance management', 'Unlimited vehicle tracking', '24/7 phone support', 'Permit assistance', 'Load simulation']},
            {'name': 'Enterprise', 'price': 399, 'features': ['All Pro features', 'Custom API integration', 'Dedicated account manager', 'Customized reporting', 'Weather integration', 'Priority support']},
        ],
    }
    return render(request, 'landing/index.html', context)

# View for the dashboard page displaying services
def dashboard_view(request):
    services = [
        {'title': 'Route Optimization', 'description': 'Efficiently plan your routes considering road restrictions and regulations.', 'icon': 'fas fa-route', 'url': 'route-optimization'},
        {'title': 'Compliance Management', 'description': 'Stay up-to-date with local and international transport regulations.', 'icon': 'fas fa-clipboard-check', 'url': 'compliance-management'},
        {'title': 'Real-time Tracking', 'description': 'Monitor your abnormal loads in real-time for better coordination.', 'icon': 'fas fa-satellite-dish', 'url': 'real-time-tracking'},
        {'title': 'Permit Assistance', 'description': 'Streamline the process of obtaining necessary permits for your transports.', 'icon': 'fas fa-file-alt', 'url': 'permit-assistance'},
        {'title': 'Load Simulation', 'description': 'Simulate your load on various road types to ensure safe transport.', 'icon': 'fas fa-truck-loading', 'url': 'load-simulation'},
        {'title': 'Weather Integration', 'description': 'Get real-time weather updates along your planned routes.', 'icon': 'fas fa-cloud-sun-rain', 'url': 'weather-integration'},
    ]
    return render(request, 'dashboard/dashboard.html', {'services': services})

# View for Weather Integration Service with Open-Meteo API Integration
def weather_integration_view(request):
    selected_country = request.GET.get('country', 'South Africa')  # Default to 'South Africa'
    selected_province = request.GET.get('province', 'Gauteng')     # Default to 'Gauteng'
    
    provinces = COUNTRY_PROVINCES_COORDINATES.get(selected_country, {}).keys()
    weather_info = None
    daily_weather_data = []

    # Fetch weather data if country and province are selected
    if selected_country and selected_province:
        coordinates = COUNTRY_PROVINCES_COORDINATES[selected_country].get(selected_province)
        if coordinates:
            latitude = coordinates['latitude']
            longitude = coordinates['longitude']
            
            # Open-Meteo API call for weather data, including daily temperature and precipitation
            url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Africa/Johannesburg'
            response = requests.get(url)
            
            # Check if the API request was successful
            if response.status_code == 200:
                weather_info = response.json()
                
                # Extract daily weather data and format it
                days = weather_info.get("daily", {}).get("time", [])
                max_temps = weather_info.get("daily", {}).get("temperature_2m_max", [])
                min_temps = weather_info.get("daily", {}).get("temperature_2m_min", [])
                precipitation = weather_info.get("daily", {}).get("precipitation_sum", [])
                
                # Create a list of tuples with day, max_temp, min_temp, and precipitation
                for day, max_temp, min_temp, precip in zip(days, max_temps, min_temps, precipitation):
                    daily_weather_data.append((day, max_temp, min_temp, precip))
            else:
                weather_info = {'error': 'Could not retrieve weather data.'}

    # If the request expects a JSON response, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'countries': list(COUNTRY_PROVINCES_COORDINATES.keys()),
            'selected_country': selected_country,
            'provinces': list(provinces),
            'selected_province': selected_province,
            'weather_info': weather_info,
            'daily_weather_data': daily_weather_data,
        })
    
    # Otherwise, render the template normally
    return render(request, 'services/weather_integration.html', {
        'countries': COUNTRY_PROVINCES_COORDINATES.keys(),
        'selected_country': selected_country,
        'provinces': provinces,
        'selected_province': selected_province,
        'weather_info': weather_info,
        'daily_weather_data': daily_weather_data,  # Pass the daily weather data to the template
    })
# View placeholders for each service
def route_optimization_view(request):
    return render(request, 'services/route_optimization.html')

def compliance_management_view(request):
    return render(request, 'services/compliance_management.html')

def real_time_tracking_view(request):
    return render(request, 'services/real_time_tracking.html')

def permit_assistance_view(request):
    return render(request, 'services/permit_assistance.html')

def load_simulation_view(request):
    return render(request, 'services/load_simulation.html')

def av_number_view(request):
    return render(request, 'services/av_number.html')

def account_view(request):
    return render(request, 'services/account.html')

def constants_view(request):
    return render(request, 'services/constants.html')