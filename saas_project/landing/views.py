from django.shortcuts import render

def index(request):
    context = {
        'features': [
            {
                'title': 'Route Optimization',
                'description': 'Efficiently plan your routes considering road restrictions and regulations.',
                'icon': 'fas fa-route',
            },
            {
                'title': 'Compliance Management',
                'description': 'Stay up-to-date with local and international transport regulations.',
                'icon': 'fas fa-clipboard-check',
            },
            {
                'title': 'Real-time Tracking',
                'description': 'Monitor your abnormal loads in real-time for better coordination.',
                'icon': 'fas fa-satellite-dish',
            },
            {
                'title': 'Permit Assistance',
                'description': 'Streamline the process of obtaining necessary permits for your transports.',
                'icon': 'fas fa-file-alt',
            },
            {
                'title': 'Load Simulation',
                'description': 'Simulate your load on various road types to ensure safe transport.',
                'icon': 'fas fa-truck-loading',
            },
            {
                'title': 'Weather Integration',
                'description': 'Get real-time weather updates along your planned routes.',
                'icon': 'fas fa-cloud-sun-rain',
            },
        ],
        'pricing_plans': [
            {
                'name': 'Basic',
                'price': 99,
                'features': [
                    'Route optimization',
                    'Basic compliance alerts',
                    '5 vehicle tracking',
                    'Email support',
                ],
            },
            {
                'name': 'Pro',
                'price': 199,
                'features': [
                    'All Basic features',
                    'Advanced compliance management',
                    'Unlimited vehicle tracking',
                    '24/7 phone support',
                    'Permit assistance',
                    'Load simulation',
                ],
            },
            {
                'name': 'Enterprise',
                'price': 399,
                'features': [
                    'All Pro features',
                    'Custom API integration',
                    'Dedicated account manager',
                    'Customized reporting',
                    'Weather integration',
                    'Priority support',
                ],
            },
        ],
    }
    return render(request, 'landing/index.html', context)
