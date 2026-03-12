from ...utils.dump_to_file import dump_to_file

def calculate_total_carbon_emission(vehicle_data: dict, distance_per_day_km: float, debug: bool = False) -> dict[str, float | str]:
    """
    Calculate total carbon emissions (kgCO2e) for all vehicles over a given distance per day.

    Total = sum(vehicles_per_day * carbon_emissions_kgCO2e_per_km * distance_per_day_km)

    Parameters
    ----------
    vehicle_data : dict
        traffic_input["vehicle_data"]
    distance_per_day_km : float
        Average distance traveled per day per vehicle in kilometers (default 1 km)
    debug : bool
        If True, saves a detailed emission breakdown JSON in ./debug/

    Returns
    -------
    dict
        Total carbon emissions in kgCO2e for the given distance per day

    Raises
    ------
    ValueError
        If vehicle_data is missing or not a dictionary
    """

    total_emission = 0.0
    breakdown = {}

    # Process each vehicle type
    for vehicle_type, data in vehicle_data.items():
        count = data.get("vehicles_per_day")
        emission_factor = data.get("carbon_emissions_kgCO2e_per_km")

        try:
            vehicle_total = float(count) * float(emission_factor) * float(distance_per_day_km)
        except (ValueError, TypeError):
            print(f"Warning: Skipping {vehicle_type}, invalid numeric values.")
            continue

        total_emission += vehicle_total

        breakdown[vehicle_type] = {
            "vehicles_per_day": count,
            "emission_factor_kgCO2e_per_km": emission_factor,
            "distance_traveled_km": distance_per_day_km,
            "total_emission_kgCO2e": vehicle_total
        }

    if debug:
        debug_output = {
            "unit": "kgCO2e (total per day for the given distance)",
            "distance_per_day_km": distance_per_day_km,
            "total_emission_kgCO2e": total_emission,
            "vehicle_breakdown": breakdown
        }
        dump_to_file("ruc-carbon_emission_due_to_vehicles_breakdown.json", debug_output)

    return {
        "total_emission_kgCO2e": total_emission,
        "unit": "kgCO2e/day",
        "distance_per_day_km": distance_per_day_km,
        "Note": "This value represents the total carbon emissions per day for the given distance traveled. "
        "To get total emissions over multiple days or different distances, multiply accordingly."
    }
