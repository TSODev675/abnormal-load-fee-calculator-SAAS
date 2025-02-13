def calculate_fees(data):
    mass_tariff = data['actual_mass'] * 0.05  # Example calculation
    damage = (data['total_distance'] * 0.02) + (data['distance_escorted'] * 0.05)
    total_fee = mass_tariff + damage + (500 if data['engineer_fee'] else 0)

    return {
        'mass_tariff': round(mass_tariff, 2),
        'damage': round(damage, 2),
        'total_fee': round(total_fee, 2),
    }
