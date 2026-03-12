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
        input_data (dict | InputMetaData | InputGlobalMetaData): Project input.
        construction_costs (dict): Initial construction costs.
        wpi (dict | WPIMetaData, optional): Wholesale price index. Required when
            use_global_road_user_calculations is False.
        debug (bool, optional): If True, dumps intermediate inputs to JSON.

    Returns:
        dict: Stage-wise LCC results (initial, use, reconstruction, end-of-life).

    Raises:
        TypeError: If input_data or wpi are of unexpected types.
        ValueError: If input fails validation or required fields are missing.
    """

    # --- 1. Load standard suggestions for validation ---
    suggestions = get_IRC_standard_suggestions()

    # --- 2. Normalise input_data to dict and resolve is_global ---
    if isinstance(input_data, dict):
        gp = input_data.get("general_parameters")
        if gp is None:
            raise ValueError("Missing 'general_parameters' block.")

        is_global = gp.get("use_global_road_user_calculations")

        if is_global is True:
            InputGlobalMetaData.from_dict(input_data)  # validate structure early
        elif is_global is False:
            InputMetaData.from_dict(input_data)  # validate structure early
        else:
            raise ValueError(
                "'use_global_road_user_calculations' must be True or False."
            )

    elif isinstance(input_data, (InputMetaData, InputGlobalMetaData)):
        is_global = isinstance(input_data, InputGlobalMetaData)
        input_data = input_data.to_dict()

    else:
        raise TypeError(
            "input_data must be a dict, InputMetaData, or InputGlobalMetaData."
        )

    # --- 3. Normalise wpi to dict ---
    if isinstance(wpi, dict):
        WPIMetaData.from_dict(wpi)  # validate structure early; dict form is retained downstream
    elif isinstance(wpi, WPIMetaData):
        wpi = wpi.to_dict()
    elif wpi is not None:
        raise TypeError("wpi must be a dict or WPIMetaData instance.")
    # wpi=None is valid: when is_global=True, eval_wpi=False so wpi is never inspected;
    # when is_global=False, eval_wpi=True and the validator will raise if wpi is required but absent.

    # --- 4. Validate Input ---
    # eval_wpi=False when is_global is True — WPI is not needed and may not be provided
    validation_report = ironclad_validator(
        input_data, suggestions, wpi, eval_wpi=not is_global
    )

    if validation_report["errors"]:
        raise ValueError(
            f"Input validation failed with errors:\n{validation_report['errors']}"
        )

    # --- 5. Calculate or fetch RUC ---
    if is_global:
        # Use provided RUC from input_data
        ruc_results = input_data.get(
            "daily_road_user_cost_with_vehicular_emissions", {}
        )

    else:
        # Calculate RUC normally
        traffic_data = input_data.get("traffic_and_road_data", {})
        ruc_results = calculate_road_user_costs(traffic_data, wpi, debug)

    # --- 6. Prepare Stage Cost Parameters ---
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

    # --- 7. Initialize and Run LCC Calculations ---
    stage_calc = StageCostCalculator(stage_params, construction_costs, debug)

    return {
        "initial_stage": stage_calc.initial_cost_calculator(),
        "use_stage": stage_calc.use_stage_cost_calculator(),
        "reconstruction": stage_calc.reconstruction(),
        "end_of_life": stage_calc.end_of_life_stage_costs(),
        "warnings": validation_report["warnings"],
        "notes": validation_report["info"],
    }
