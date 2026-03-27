def validate_traffic_input(traffic_input):
    """
    Validate the structure, required fields, and positivity of values in the traffic_input dictionary.
    Returns a tuple (is_valid: bool, errors: list) where:
        - is_valid: True if the input is valid, False otherwise.
        - errors: List of error messages (if any).
    """
    errors = []

    # Validate 'vehicle_data' structure
    if not isinstance(traffic_input.get('vehicle_data'), dict):
        errors.append("'vehicle_data' must be a dictionary.")
    else:
        for vehicle, vehicle_info in traffic_input['vehicle_data'].items():
            if not isinstance(vehicle_info, dict):
                errors.append(
                    f"Vehicle '{vehicle}' data must be a dictionary.")
            if 'vehicles_per_day' not in vehicle_info or not isinstance(vehicle_info['vehicles_per_day'], (int, float)):
                errors.append(
                    f"Vehicle '{vehicle}' must have a valid 'vehicles_per_day' field.")
            elif vehicle_info['vehicles_per_day'] <= 0:
                errors.append(
                    f"Vehicle '{vehicle}' must have a positive 'vehicles_per_day' value.")

    # Validate 'additional_inputs' structure
    if not isinstance(traffic_input.get('additional_inputs'), dict):
        errors.append("'additional_inputs' must be a dictionary.")
    else:
        additional_inputs = traffic_input['additional_inputs']

        # Check for 'additional_travel_time_min' and validate type and positivity
        if 'additional_travel_time_min' not in additional_inputs:
            errors.append("'additional_travel_time_min' is missing.")
        elif not isinstance(additional_inputs['additional_travel_time_min'], (int, float)):
            errors.append("'additional_travel_time_min' must be a number.")
        elif additional_inputs['additional_travel_time_min'] <= 0:
            errors.append(
                "'additional_travel_time_min' must be a positive number.")

        # Check for 'alternate_road_carriageway' and validate type
        if 'alternate_road_carriageway' not in additional_inputs:
            errors.append("'alternate_road_carriageway' is missing.")
        elif not isinstance(additional_inputs['alternate_road_carriageway'], str):
            errors.append("'alternate_road_carriageway' must be a string.")

    # Return the validation result
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_wpi(wpi):
    """
    Validate the structure and positivity of values in the WPI dictionary.
    Returns a tuple (is_valid: bool, errors: list) where:
        - is_valid: True if the WPI is valid, False otherwise.
        - errors: List of error messages (if any).
    """
    errors = []

    # Check if 'wpi' is a dictionary
    if not isinstance(wpi, dict):
        errors.append("'wpi' must be a dictionary.")

    # Check if 'WPI' is present and is a dictionary
    elif 'WPI' not in wpi or not isinstance(wpi['WPI'], dict):
        errors.append("'wpi' must contain a valid 'WPI' dictionary.")
    else:
        wpi_data = wpi['WPI']

        # Each vehicle entry must have a positive 'vot_cost'
        for vehicle, vehicle_wpi in wpi_data.items():
            if not isinstance(vehicle_wpi, dict):
                errors.append(f"WPI entry for '{vehicle}' must be a dictionary.")
                continue
            if 'vot_cost' not in vehicle_wpi:
                errors.append(f"Missing 'vot_cost' for vehicle '{vehicle}' in WPI.")
            elif not isinstance(vehicle_wpi['vot_cost'], (int, float)) or vehicle_wpi['vot_cost'] <= 0:
                errors.append(f"'{vehicle}' VOT cost must be a positive number.")

    # Return the validation result
    is_valid = len(errors) == 0
    return is_valid, errors
