from . import IRCSP302019Table6_Table7 as IRC
from .input_validation import validate_traffic_input, validate_wpi
from ...utils.dump_to_file import dump_to_file
from ..carriage_width_info.carriagewayStandards import CarriagewayStandards


def calculate_additional_time_cost(traffic_input, wpi, debug=False):
    """
    Calculate additional travel time cost (Rs./day) using ADTD.

    If debug=True:
        - Saves a detailed JSON in /debug folder
        - Returns detailed breakdown

    Returns:
        float (Rs.) or dict (debug breakdown)
    """

    # Validate traffic_input
    is_valid_traffic, traffic_errors = validate_traffic_input(traffic_input)
    if not is_valid_traffic:
        raise ValueError(f"Invalid traffic_input data: {traffic_errors}")

    # Validate wpi
    is_valid_wpi, wpi_errors = validate_wpi(wpi)
    if not is_valid_wpi:
        raise ValueError(f"Invalid wpi data: {wpi_errors}")

    # Extract vehicle data
    vehicle_input = traffic_input['vehicle_data']
    # minutes
    additional_travel_time_min = traffic_input['additional_inputs']['additional_travel_time_min']
    additional_hours = additional_travel_time_min / 60  # convert minutes to hours

    # Set up travel time and occupancy values
    travel_time_values = IRC.valueofTravelTime(CarriagewayStandards.get_velocity_class(
        traffic_input["additional_inputs"]["alternate_road_carriageway"]))
    occupancy = IRC.average_occupancy()

    wpi_vot = wpi["WPI"]["vot_cost"]

    total_cost = 0
    breakdown = {}

    # Loop through each vehicle type in the input data
    for vehicle, vehicle_info in vehicle_input.items():
        if vehicle not in travel_time_values:
            raise ValueError(f"Unknown vehicle type: '{vehicle}'")

        # Extract vehicle-specific data
        count = vehicle_info["vehicles_per_day"]
        base_vot = travel_time_values[vehicle]  # Rs./hour
        persons = occupancy.get(vehicle, 1)     # persons/vehicle

        # Adjust based on WPI factor
        wpi_factor = wpi_vot.get(vehicle)
        if wpi_factor is None:
            raise ValueError(
                f"Missing WPI factor for vehicle type: '{vehicle}'")

        adjusted_vot = base_vot * wpi_factor  # Rs./hour
        cost = adjusted_vot * additional_hours * persons * count

        total_cost += cost

        # If debugging, gather detailed breakdown
        if debug:
            breakdown[vehicle] = {
                "ADT_vehicles": f"{count} vehicles/day",
                "occupancy": f"{persons} persons/vehicle",
                "base_VOT": f"{base_vot:.2f} Rs./hour",
                "WPI_vot_factor": f"{wpi_factor:.3f}",
                "adjusted_VOT": f"{adjusted_vot:.2f} Rs./hour",
                "additional_time": f"{additional_hours:.3f} hours",
                "additional_cost": f"{cost:.2f} Rs./day"
            }

    if debug:
        breakdown["TOTAL_ADDITIONAL_COST"] = f"{total_cost:.2f} Rs./day"
        dump_to_file("Value_of_time_summary.json", breakdown)
        # return breakdown

    return {"total_Cost": total_cost, "unit": "Rs./day"}
