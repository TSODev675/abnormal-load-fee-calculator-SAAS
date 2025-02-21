import math
from django.conf import settings

# Constants
LEGAL_MASS_LIMIT = 56000  # kg
UNIT_COST = 0.59  # cents per km
ESCORT_RATE = 18.00  # R per km for escort
MIN_FEE_PER_AXLE = 12.7  # cents per km
K = 5.5  # Fee constant
WIDTH_THRESHOLD = {"RSA": 3000, "Namibia": 2600}  # mm
LENGTH_THRESHOLD = {"RSA": 25000, "Namibia": 22000}  # mm
STABILITY_CHECK_THRESHOLD = 3.5  # Stability check triggers if wheel track < 3.5m
ENGINEER_FEE_THRESHOLD = 125000  # GCM threshold for engineer's fee in kg
HEIGHT_TO_WHEELTRACK_RATIO = 2.2  # Engineer required if exceeded
WIDTH_TO_WHEELTRACK_RATIO = 2.0  # Engineer required if exceeded
DETERRENT_FACTORS = {"RSA": 1.0, "Namibia": 8.0}
ALLOWABLE_ESWM = {"Single Axle": 3850, "Other Axle Types": 2250}  # kg


def requires_engineer_approval(total_mass, laden_width, laden_height, wheel_track):
    """
    Determines if Engineer's approval is required based on height, width, and stability checks.
    """
    stability_check_required = wheel_track < STABILITY_CHECK_THRESHOLD
    height_ratio = laden_height / (wheel_track * 1000)  # Convert mm to meters
    width_ratio = laden_width / (wheel_track * 1000)

    if (
        total_mass > ENGINEER_FEE_THRESHOLD
        or laden_width > 6000
        or stability_check_required
        or height_ratio > HEIGHT_TO_WHEELTRACK_RATIO
        or width_ratio > WIDTH_TO_WHEELTRACK_RATIO
    ):
        return True  # Engineer's approval required
    return False


def calculate_mass_fee(total_mass, no_of_axles, w_spc_a, type_pressure, province, axle_type, total_distance):
    """
    Calculate the mass fee based on TRH11.
    """
    if total_mass <= LEGAL_MASS_LIMIT:
        return 0  # No mass fee if within legal limits

    # Step 1: Convert W-Spc A from mm to meters
    F = w_spc_a / 1000

    # Step 2: Load on Each Wheel (B)
    B = total_mass / no_of_axles

    # Step 3: Wheel Spacing Influence (E)
    E = -2.13 * F - 643.34 * (F ** 2) + 909.8 * (F ** 3) - 361.87 * (F ** 4) + 100

    # Step 4: Tyre Pressure Influence (C)
    D = type_pressure
    C = 0.003427 * D - (3.1e-6 * D ** 2) + (1.16e-9 * D ** 3) - 0.12587
    C = min(C, 1.35)  # Max limit

    # Step 5: Effective Single Wheel Mass (ESWM)
    if "Single" in axle_type:
        ESWM = B * C
    else:
        ESWM = B * C + (B * C * E / 100)

    # Step 6: Damage Calculation
    damage = (ESWM / 3250) ** 4

    # Step 7: Allowable Damage
    legal_eswm = ALLOWABLE_ESWM.get(axle_type, 2250) * C
    allowable_damage = (legal_eswm / 3250) ** 4

    # Step 8: Accountable Damage
    accountable_damage = max(damage - allowable_damage, 0)
    total_accountable_damage = accountable_damage * no_of_axles

    # Step 9: Mass Fee Calculation
    mass_fee = total_accountable_damage * UNIT_COST

    # Step 10: Apply minimum fee per axle
    min_mass_fee = no_of_axles * MIN_FEE_PER_AXLE
    mass_fee = max(mass_fee, min_mass_fee)

    # Step 11: Apply Deterrent Factor
    country = "RSA" if province in ["GP", "FS", "MP", "KN", "NW", "NC", "EC", "LP"] else "Namibia"
    deterrent_factor = DETERRENT_FACTORS.get(country, 1.0)
    mass_fee *= deterrent_factor

    # Step 12: Compute total fee based on distance
    total_mass_fee = mass_fee * total_distance

    return round(total_mass_fee, 2)


def calculate_road_usage_fee(laden_width, laden_length, total_distance, country="RSA"):
    """
    Road Usage Fee = (Width Fee + Length Fee) * distance
    """
    W = WIDTH_THRESHOLD[country]
    L = LENGTH_THRESHOLD[country]

    width_fee = K * ((laden_width / W) ** 4.7 - 1) if laden_width > W else 0
    length_fee = K * ((laden_length / L) ** 4.0 - 1) if laden_length > L else 0

    total_road_usage_fee = (width_fee + length_fee) * total_distance
    return max(0, round(total_road_usage_fee, 2))


def calculate_escort_fee(num_escorts, total_distance, weekend=False):
    """
    Escort Fee = Escort Rate * num_escorts * distance
    """
    weekend_rate = 21.00  # Weekend fee
    applicable_rate = weekend_rate if weekend else ESCORT_RATE

    escort_fee = num_escorts * applicable_rate * total_distance
    return round(escort_fee, 2)


def calculate_administrative_fee(total_mass, laden_width, laden_height, wheel_track, engineer_input=False):
    """
    Administrative Fee: Higher if engineer's input is required.
    Engineer Fee applies if:
    - GCM > 125,000 kg
    - Width > 6,000 mm
    - Stability check triggered (wheel track below threshold)
    - Height/Wheeltrack ratio > 2.2
    - Width/Wheeltrack ratio > 2.0
    """
    BASIC_ADMIN_FEE = 300
    ENGINEER_ADMIN_FEE = 810

    if requires_engineer_approval(total_mass, laden_width, laden_height, wheel_track) or engineer_input:
        return ENGINEER_ADMIN_FEE
    return BASIC_ADMIN_FEE


def calculate_total_permit_fee(
    total_mass, no_of_axles, w_spc_a, type_pressure, province, axle_type, total_distance,
    laden_width, laden_length, laden_height, num_escorts, wheel_track, weekend=False, engineer_input=False
):
    """
    Computes the final permit fee by summing all individual fees.
    """
    admin_fee = calculate_administrative_fee(total_mass, laden_width, laden_height, wheel_track, engineer_input)
    mass_fee = calculate_mass_fee(total_mass, no_of_axles, w_spc_a, type_pressure, province, axle_type, total_distance)
    road_usage_fee = calculate_road_usage_fee(laden_width, laden_length, total_distance)
    escort_fee = calculate_escort_fee(num_escorts, total_distance, weekend)

    total_fee = admin_fee + mass_fee + road_usage_fee + escort_fee
    return round(total_fee, 2)


# Test Example
if __name__ == "__main__":
    permit_fee = calculate_total_permit_fee(
        total_mass=23000,
        no_of_axles=1,
        w_spc_a=1200,
        type_pressure=750,
        province="GP",
        axle_type="4 Dual",
        total_distance=150,
        laden_width=2500,
        laden_length=26000,
        laden_height=4800,
        num_escorts=2,
        wheel_track=3.3,  # Stability check triggers if below threshold
        weekend=False,
        engineer_input=False  # Engineer’s fee should trigger automatically if ratio conditions met
    )
    print(f"Total Permit Fee: R{permit_fee:.2f}")
