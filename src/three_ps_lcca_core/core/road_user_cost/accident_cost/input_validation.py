from ... import standard_keys as c


def validate_accident_input(traffic_input: dict, wpi: dict) -> tuple[bool, list[str]]:
    """
    Validate the structure and contents of the accident input data.
    Ensures all keys required for explicit lookup in core.py exist.
    """
    errors = []

    # 1. Validate traffic_input core structure
    if not isinstance(traffic_input, dict):
        return False, ["traffic_input must be a dictionary."]

    # 2. Validate Severity Distribution (Percentage Check)
    sev_dist = traffic_input.get('accident_severity_distribution')
    if not isinstance(sev_dist, dict):
        errors.append("'accident_severity_distribution' must be a dictionary.")
    else:
        total_percent = sum(sev_dist.values())
        if not (99.9 <= round(total_percent, 2) <= 100):
            errors.append(
                f"Severity distribution percentages must sum to 100 (found {total_percent}).")

        # Ensure WPI has medical cost indices for these severities
        medical_wpi = wpi.get('WPI', {}).get('medical_cost', {})
        for severity, value in sev_dist.items():
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(
                    f"Invalid percentage for severity '{severity}': {value}")
            if severity not in medical_wpi:
                errors.append(
                    f"Missing WPI medical cost index for severity: '{severity}'.")

    # 3. Validate vehicle_data and WPI mapping
    vehicle_data = traffic_input.get('vehicle_data')
    property_damage_wpi = wpi.get('WPI', {}).get(
        'vehicle_cost', {}).get('property_damage', {})

    if not isinstance(vehicle_data, dict):
        errors.append("'vehicle_data' must be a dictionary.")
    else:
        total_adt = sum(v.get('vehicles_per_day', 0)
                        for v in vehicle_data.values())
        if total_adt <= 0:
            errors.append(
                "Total ADT (Average Daily Traffic) must be greater than zero.")

        for vehicle, data in vehicle_data.items():
            if not isinstance(data, dict):
                errors.append(
                    f"Vehicle data for '{vehicle}' must be a dictionary.")
            elif 'vehicles_per_day' not in data or not isinstance(data['vehicles_per_day'], (int, float)):
                errors.append(
                    f"Missing or invalid 'vehicles_per_day' for vehicle '{vehicle}'.")

            # Check if WPI has property damage keys (handling d_buses -> o_buses mapping)
            lookup_key = c.O_BUSES if vehicle == c.D_BUSES else vehicle
            if lookup_key not in property_damage_wpi:
                errors.append(
                    f"Missing WPI property damage index for vehicle key: '{lookup_key}'.")

    # 4. Validate Additional Inputs for Calculation
    add_in = traffic_input.get('additional_inputs')
    if not isinstance(add_in, dict):
        errors.append("'additional_inputs' must be a dictionary.")
    else:
        required_params = [
            "additional_reroute_distance_km",
            "crash_rate_accidents_per_million_km",
            "work_zone_multiplier"
        ]
        for param in required_params:
            if param not in add_in or not isinstance(add_in[param], (int, float)):
                errors.append(
                    f"Missing or invalid calculation parameter: '{param}'.")

    # Return validation result
    is_valid = len(errors) == 0
    return is_valid, errors
