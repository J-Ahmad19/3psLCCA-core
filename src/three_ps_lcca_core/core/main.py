from .road_user_cost.main import calculate_road_user_costs
from .stage_cost.stage_cost import StageCostCalculator
from .utils.dump_to_file import dump_to_file
from .utils.list_suggestions import get_IRC_standard_suggestions
from .utils.input_validator import ironclad_validator
from three_ps_lcca_core.inputs.input import InputMetaData
from three_ps_lcca_core.inputs.input_global import InputGlobalMetaData
from three_ps_lcca_core.inputs.wpi import WPIMetaData


def run_full_lcc_analysis(input_data, construction_costs, wpi=None, debug=False):
    """
    Entry point for the OSDAG LCC module.
    Validates input, coordinates Road User Cost (RUC) calculations, and
    computes Life Cycle Stage Costs.

    Args:
        input_data (dict): Project input dictionary.
        construction_costs (dict): Initial construction costs.
        wpi (float, optional): Wholesale price index for RUC calculation.
        debug (bool, optional): If True, dumps intermediate inputs to JSON.

    Returns:
        dict: Stage-wise LCC results (initial, use, reconstruction, end-of-life).

    Raises:
        ValueError: If input fails validation or wpi is required but not provided.
    """

    # --- 1. Load standard suggestions for validation ---
    suggestions = get_IRC_standard_suggestions()
    if isinstance(input_data, dict):

        gp = input_data.get("general_parameters")
        if gp is None:
            raise ValueError("Missing 'general_parameters' block.")

        is_global = gp.get("use_global_road_user_calculations")

        if is_global is True:
            input_data_obj = InputGlobalMetaData.from_dict(input_data)
        elif is_global is False:
            input_data_obj = InputMetaData.from_dict(input_data)
        else:
            raise ValueError(
                "'use_global_road_user_calculations' must be True or False."
            )
    elif isinstance(input_data, (InputMetaData, InputGlobalMetaData)):
        input_data= input_data.to_dict()

    else:
        raise TypeError(
            "input_data must be dict, InputMetaData, or InputGlobalMetaData."
        )
    
    if wpi is not None and isinstance(wpi, dict):
        wpi_obj = WPIMetaData.from_dict(wpi)
    elif wpi is not None and isinstance(wpi, WPIMetaData):
        wpi = wpi.to_dict()
    else:
        raise TypeError("wpi must be dict or WPIMetaData.")

    # --- 2. Validate Input ---
    validation_report = ironclad_validator(input_data, suggestions, wpi)

    if validation_report["errors"]:
        # Stop execution if there are critical errors
        raise ValueError(
            f"Input validation failed with errors:\n{validation_report['errors']}"
        )
        

    # --- 3. Determine if RUC calculation is bypassed ---
    bypass_ruc = input_data.get("general_parameters", {}).get(
        "use_global_road_user_calculations", False
    )

    if bypass_ruc:
        # Use provided RUC from input_data
        ruc_results = input_data.get(
            "daily_road_user_cost_with_vehicular_emissions", {}
        )
        if debug:
            print("Bypassing RUC calculation. Using provided RUC:", ruc_results)

    else:
        if wpi is None:
            raise ValueError("wpi cannot be None when RUC calculation is required")

        # Calculate RUC normally
        traffic_data = input_data.get("traffic_and_road_data", {})
        ruc_results = calculate_road_user_costs(traffic_data, wpi, debug)

    # --- 4. Prepare Stage Cost Parameters ---
    stage_params = input_data.get("maintenance_and_stage_parameters", {}).copy()
    stage_params["general"] = input_data.get("general_parameters", {})

    # Add RUC results to construction costs
    construction_costs["daily_road_user_cost_with_vehicular_emissions"] = ruc_results

    if debug:
        dump_to_file(
            "Stage_Cost_Calculator_Inputs.json",
            {"stage_params": stage_params, "construction_costs": construction_costs},
        )
        
        dump_to_file("A0_Validation_report.json", validation_report)

    # --- 5. Initialize and Run LCC Calculations ---
    stage_calc = StageCostCalculator(stage_params, construction_costs, debug)

    return {
        "initial_stage": stage_calc.initial_cost_calculator(),
        "use_stage": stage_calc.use_stage_cost_calculator(),
        "reconstruction": stage_calc.reconstruction(),
        "end_of_life": stage_calc.end_of_life_stage_costs(),
        "warnings": validation_report["warnings"],
        "notes": validation_report["info"]
    }
