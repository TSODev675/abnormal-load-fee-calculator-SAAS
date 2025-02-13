from django.shortcuts import render, get_object_or_404
import requests
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import AxleLoadData
from .models import Constant  
from .calculations import calculate_fees
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import os
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

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


def subscription_view(request):
    selected_plan = request.GET.get('plan', 'Basic')  # Default to 'Basic' if no plan is selected
    payment_methods = ['Visa/Mastercard', 'EFT', 'Apple Pay', 'Google Pay']

    context = {
        'selected_plan': selected_plan,
        'payment_methods': payment_methods
    }
    return render(request, 'services/subscription.html', context)



def safe_float_conversion(value, default=0.0):
    """
    Safely convert a value to float, handling empty strings and None values.
    :param value: Value to convert to float
    :param default: Default value if conversion fails or value is empty
    :return: Converted float or default value
    """
    try:
        return float(value) if value not in [None, '', 'None'] else default
    except ValueError:
        return default



def constants_view(request):
    constants_list = Constant.objects.all().order_by('id')
    paginator = Paginator(constants_list, 25)  # Show 25 rows per page
    page_number = request.GET.get('page')
    constants = paginator.get_page(page_number)
    return render(request, 'services/constants.html', {'constants': constants})


@csrf_exempt
def update_constant_value(request):
    if request.method == "POST":
        constant_id = request.POST.get("constant_id")
        new_value = request.POST.get("new_value")

        try:
            constant = Constant.objects.get(id=constant_id)
            constant.value = new_value
            constant.save()
            return JsonResponse({"success": True})
        except Constant.DoesNotExist:
            return JsonResponse({"success": False, "message": "Constant not found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method."})


def fee_calculator(request):
    calculated_fees = {'mass_tariff': 0, 'damage': 0, 'total_fee': 0}  # Initialize default values

    if request.method == "POST":
        form_data = {
            'axle_unit': request.POST.get('axle_unit', '')[:5].strip(),  # Truncate to 5 chars
            'allowable_mass': float(request.POST.get('allowable_mass', 0)),
            'actual_mass': float(request.POST.get('actual_mass', 0)),
            'no_of_axles': int(request.POST.get('no_of_axles', 0)),
            'axle_type': request.POST.get('axle_type', '')[:20].strip(),  # Truncate to 20 chars
            'w_spc_a': float(request.POST.get('w_spc_a', 0)),
            'w_spc_b': float(request.POST.get('w_spc_b', 0)),
            'type_pressure': float(request.POST.get('type_pressure', 0)),
            'total_mass': float(request.POST.get('total_mass', 0)),
            'wheel_track': float(request.POST.get('wheel_track', 0)),
            'av_no': request.POST.get('av_no', '')[:10].strip(),  # Truncate to 10 chars
            'laden_length': float(request.POST.get('laden_length', 0)),
            'laden_width': float(request.POST.get('laden_width', 0)),
            'laden_height': float(request.POST.get('laden_height', 0)),
            'total_distance': float(request.POST.get('total_distance', 0)),
            'distance_escorted': float(request.POST.get('distance_escorted', 0)),
            'no_of_escorts': int(request.POST.get('no_of_escorts', 0)),
            'rural_speed': float(request.POST.get('rural_speed', 0)),
            'engineer_fee': request.POST.get('engineer_fee') == 'on',
            'weekend_travel': request.POST.get('weekend_travel') == 'on',
            'mobile_crane': request.POST.get('mobile_crane') == 'on',
            'province': request.POST.get('province', '')[:2].strip(),  # Truncate to 2 chars
        }

         # Save the data and calculated fee in the database
        calculated_fees = calculate_fees(form_data)

        AxleLoadData.objects.create(**form_data, calculated_fee=calculated_fees['total_fee'])

    return render(request, 'dashboard/calculator.html', {
        'mass_tariff': calculated_fees['mass_tariff'],
        'damage': calculated_fees['damage'],
        'total_fee': calculated_fees['total_fee']
    })


def generate_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="axle_permit.pdf"'
    
    # Create the PDF object
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Axle Load Permit")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Axle Unit: {request.POST.get('axle_unit', '')}")
    c.drawString(50, height - 120, f"Allowable Mass (kg): {request.POST.get('allowable_mass', '')}")
    c.drawString(50, height - 140, f"Actual Mass (kg): {request.POST.get('actual_mass', '')}")
    c.drawString(50, height - 160, f"No. of Axles: {request.POST.get('no_of_axles', '')}")
    c.drawString(50, height - 180, f"Axle Type: {request.POST.get('axle_type', '')}")
    c.drawString(50, height - 200, f"Total Laden Length (mm): {request.POST.get('laden_length', '')}")
    c.drawString(50, height - 220, f"Total Laden Width (mm): {request.POST.get('laden_width', '')}")
    c.drawString(50, height - 240, f"Total Laden Height (mm): {request.POST.get('laden_height', '')}")
    c.drawString(50, height - 260, f"Total Distance (km): {request.POST.get('total_distance', '')}")
    c.drawString(50, height - 280, f"Distance Escorted (km): {request.POST.get('distance_escorted', '')}")
    c.drawString(50, height - 300, f"No. of Traffic Officer Escorts: {request.POST.get('no_of_escorts', '')}")
    c.drawString(50, height - 320, f"Rural Speed (km/h): {request.POST.get('rural_speed', '')}")
    c.drawString(50, height - 340, f"Province: {request.POST.get('province', '')}")
    
    # Fees Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 380, "Calculated Fee")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 400, f"Mass Tariff: R{request.POST.get('mass_tariff', '0.00')}")
    c.drawString(50, height - 420, f"Damage: R{request.POST.get('damage', '0.00')}")
    c.drawString(50, height - 440, f"Total Fee: R{request.POST.get('total_fee', '0.00')}")
    
    # Finalizing PDF
    c.showPage()
    c.save()
    
    return response
