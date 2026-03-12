from .vehicle_types import bigCars, buses, hcv, lcv, mcv, smallCars, two_wheeler
from .utils import b_post_processor_for_VOC as pp
from ... import standard_keys as c
from .utils import total_of_raw_voc 

# Map vehicle_info keys to their model modules
MODEL_MAP = {
    c.BIG_CARS: bigCars,
    c.SMALL_CARS: smallCars,
    c.TWO_WHEELERS: two_wheeler,
    c.BUSES: buses,
    c.HCV: hcv,
    c.LCV: lcv,
    c.MCV: mcv,
}


def normalize_input(vehicle_input):
    """
    Converts Traffic_Input schema into the format expected by VOC models.
    """
    normalized = {}

    vehicle_data = vehicle_input.get("vehicle_data")
    vehicle_info = {}
    power_weight_ratio_pwr = {}

    # Extract vehicle counts and power-weight ratio for HCV/MCV
    for vt, data in vehicle_data.items():
        count = data.get("vehicles_per_day")
        vehicle_info[vt] = count

        if vt in [c.HCV, c.MCV] and "pwr" in data:
            power_weight_ratio_pwr[vt] = data["pwr"]

    # Combine buses and remove individual types
    vehicle_info[c.BUSES] = vehicle_info.get(c.O_BUSES) + vehicle_info.get(c.D_BUSES) # type: ignore
    vehicle_info.pop(c.O_BUSES, None)
    vehicle_info.pop(c.D_BUSES, None)

    normalized["vehicle_info"] = vehicle_info

    # Map additional_inputs to VOC fields
    additional_inputs = vehicle_input.get("additional_inputs", {})
    normalized["carriageway_width"] = additional_inputs.get("carriage_width_in_m")
    normalized["rg_roughness_factor"] = additional_inputs.get("road_roughness_mm_per_km")
    normalized["fl_fall_factor"] = additional_inputs.get("road_fall_m_per_km")
    normalized["rs_rise_factor"] = additional_inputs.get("road_rise_m_per_km")
    normalized["lane_type"] = additional_inputs.get("alternate_road_carriageway")
    normalized["additional_travel_time_min"] = additional_inputs.get("additional_travel_time_min")
    normalized["power_weight_ratio_pwr"] = power_weight_ratio_pwr

    # Keep accident severity distribution
    normalized["accident_severity_distribution"] = vehicle_input.get("accident_severity_distribution", {})

    return normalized


def main(vehicle_input_raw, wpi, debug=False):
    """
    Validates input and executes the correct vehicle models for all vehicles with count > 0.
    Supports only the new Traffic_Input format.
    """

    # --------------------
    # 0. Normalize input
    # --------------------
    vehicle_input = normalize_input(vehicle_input_raw)

    # --------------------
    # 1. Vehicle model execution
    # --------------------
    results = {}
    vehicle_info = vehicle_input.get("vehicle_info", {})
    for vt, count in vehicle_info.items():
        if count > 0:
            model_module = MODEL_MAP.get(vt)
            if model_module is None:
                results[vt] = {
                    "status": "error",
                    "message": f"No model available for '{vt}'."
                }
            else:
                input_for_model = {
                    **{k: v for k, v in vehicle_input.items() if k != "vehicle_info"},
                    "vehicle_type": vt,
                    "rf_rise_and_fall_factor": vehicle_input.get("fl_fall_factor")+ vehicle_input.get("rs_rise_factor")  # type: ignore
                }

                # Add power_weight_ratio_pwr if available
                pwr_dict = vehicle_input.get("power_weight_ratio_pwr", {})
                if isinstance(pwr_dict, dict):
                    input_for_model["power_weight_ratio_pwr"] = pwr_dict.get(vt)

                results[vt] = model_module.compute_voc(input_for_model)

    # --------------------
    # 2. Post-process results
    # --------------------
    summaryOfVOC = pp.post_process(results, wpi, debug)
    final_results = total_of_raw_voc.calculate_total_cost(summaryOfVOC, vehicle_input["vehicle_info"])
    return [summaryOfVOC, final_results]
