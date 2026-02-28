"""
3psLCCA Example Execution Script
--------------------------------
This script demonstrates how to run the Life Cycle Cost Analysis (LCCA)
using the 3psLCCA core engine.

IMPORTANT:
The execution mode is controlled inside:

Input["general_parameters"]["use_global_road_user_calculations"]

If False  → traffic_and_road_data must be provided
If True   → daily_road_user_cost_with_vehicular_emissions must be provided
"""

import json
from three_ps_lcca_core import core as co
from three_ps_lcca_core.core.main import run_full_lcc_analysis, get_IRC_standard_suggestions


# Import user-defined structured inputs
from examples.from_dict.Input import Input
from examples.from_dict.Input_global import Input_global
from examples.from_dict.wpi import wpi


# ============================================================
# 1️⃣ DEFINE CONSTRUCTION COST BREAKDOWN
# ============================================================

life_cycle_construction_cost_breakdown = {
    "initial_construction_cost_rs": 12843979.44,
    "material_carbon_emissions_cost_rs": 2065434.91,
    "superstructure_construction_cost_rs": 9356038.92,
    "total_scrap_value_rs": 2164095.02,
}


# ============================================================
# 2️⃣ RUN ANALYSIS FUNCTION
# ============================================================


def execute_analysis(input_data):
    """
    Runs the LCCA analysis using provided input dictionary.
    """

    try:
        results = run_full_lcc_analysis(
            input_data, life_cycle_construction_cost_breakdown, wpi=wpi, debug=True
        )

        print("✔ LCC Analysis Completed Successfully.")
        return results

    except Exception as e:
        print("✖ Error during LCC analysis:")
        print(e)
        return None


# ============================================================
# 3️⃣ MAIN EXECUTION
# ============================================================

# python -m examples.from_dict.example
if __name__ == "__main__":
# =======================================================================
    # run file from project root with:
    # python -m three_ps_lcca_core.examples.example
# ======================================================================
    print("--------------------------------------------------")
    print("Running 3psLCCA Analysis")
    print("--------------------------------------------------")

    # ----------------------------------------------------------
    # Choose which Input to use:
    #
    # Option 1 → Input (Detailed traffic mode)
    # Option 2 → Input_global (Global RUC mode)
    #
    # NOTE:
    # The actual calculation mode is controlled INSIDE
    # general_parameters["use_global_road_user_calculations"]
    # ----------------------------------------------------------

    results = execute_analysis(Input)

    # To use global mode instead, comment above and uncomment:
    # results = execute_analysis(Input_global)

    print("\n--- FINAL RESULTS ---")

    if results:
        print(json.dumps(results, indent=2))
    else:
        print("No results generated due to error.")

    print("\n--- IRC STANDARD SUGGESTIONS ---")
    suggestions = get_IRC_standard_suggestions()
    print(json.dumps(suggestions, indent=2))
