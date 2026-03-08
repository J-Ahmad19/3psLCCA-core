from ..road_user_cost.carriage_width_info.carriagewayStandards import CarriagewayStandards

# def ironclad_validator(data, suggestions, wpi):
#     """
#     Complete Ironclad validator for OSDAG LCC inputs.

#     Ensures:
#     - Structural integrity (Mandatory keys and numeric types).
#     - Logic integrity (Percentages sum to 100, ADT > 0).
#     - Economic integrity (Every vehicle and severity maps to a WPI index).
#     - Suggestion Sync (alternate_road_carriageway must be in approved list).
#     - Domain rules (PWR for heavy vehicles, d_buses -> o_buses mapping).
#     """
#     report = {"errors": [], "warnings": [], "info": []}

#     # --- 1. CONFIGURATION MANIFESTS ---
#     GEN_MANIFEST = [
#         "service_life_years",
#         "analysis_period_years",
#         "discount_rate_percent",
#         "inflation_rate_percent",
#         "interest_rate_percent",
#         "investment_ratio",
#         "social_cost_of_carbon_per_mtco2e",
#         "currency_conversion",
#         "construction_period_months",
#         "working_days_per_month",
#         "days_per_month",
#         "use_global_road_user_calculations",
#     ]

#     ADDITIONAL_FIELDS = [
#         "road_roughness_mm_per_km",
#         "road_rise_m_per_km",
#         "road_fall_m_per_km",
#         "additional_reroute_distance_km",
#         "additional_travel_time_min",
#         "crash_rate_accidents_per_million_km",
#         "work_zone_multiplier",
#         "hourly_capacity",
#         "force_free_flow_off_peak",
#         "carriage_width_in_m",
#     ]

#     MAINT_REQUIRED_PATHS = [
#         "use_stage_cost -> routine -> inspection -> percentage_of_initial_construction_cost_per_year",
#         "use_stage_cost -> routine -> inspection -> interval_in_years",
#         "use_stage_cost -> routine -> maintenance -> percentage_of_initial_construction_cost_per_year",
#         "use_stage_cost -> routine -> maintenance -> percentage_of_initial_carbon_emission_cost",
#         "use_stage_cost -> routine -> maintenance -> interval_in_years",
#         "use_stage_cost -> major -> inspection -> percentage_of_initial_construction_cost",
#         "use_stage_cost -> major -> inspection -> interval_for_repair_and_rehabitation_in_years",
#         "use_stage_cost -> major -> repair -> percentage_of_initial_construction_cost",
#         "use_stage_cost -> major -> repair -> percentage_of_initial_carbon_emission_cost",
#         "use_stage_cost -> major -> repair -> interval_for_repair_and_rehabitation_in_years",
#         "use_stage_cost -> major -> repair -> repairs_duration_months",
#         "use_stage_cost -> replacement_costs_for_bearing_and_expansion_joint -> percentage_of_super_structure_cost",
#         "use_stage_cost -> replacement_costs_for_bearing_and_expansion_joint -> interval_of_replacement_in_years",
#         "use_stage_cost -> replacement_costs_for_bearing_and_expansion_joint -> duration_of_replacement_in_days",
#         "end_of_life_stage_costs -> demolition_and_disposal -> percentage_of_initial_construction_cost",
#         "end_of_life_stage_costs -> demolition_and_disposal -> percentage_of_initial_carbon_emission_cost",
#         "end_of_life_stage_costs -> demolition_and_disposal -> duration_for_demolition_and_disposal_in_months",
#     ]

#     # --- 2. HELPER: NUMERIC VALIDATION ---
#     def check_num(val, path):
#         if val is None:
#             report["errors"].append(f"Missing Value: {path} is null/missing.")
#             return False
#         if not isinstance(val, (int, float)):
#             report["errors"].append(
#                 f"Type Error: {path} must be numeric (got {type(val).__name__})."
#             )
#             return False
#         if val < 0:
#             report["errors"].append(f"Range Error: {path} is {val}, must be >= 0.")
#             return False
#         return True

#     # --- 3. PASS 1: GENERAL PARAMETERS ---
#     if "general_parameters" not in data:
#         return {
#             "errors": ["CRITICAL: 'general_parameters' block missing."],
#             "warnings": [],
#         }

#     gp = data["general_parameters"]
#     for f in GEN_MANIFEST:
#         if f not in gp:
#             report["errors"].append(f"Missing Key: general_parameters -> {f}")
#         elif f == "investment_ratio":
#             if not (0 <= gp[f] <= 1):
#                 report["errors"].append(
#                     "Logic Error: investment_ratio must be between 0 and 1."
#                 )
#         elif f != "use_global_road_user_calculations":
#             check_num(gp[f], f"general_parameters -> {f}")

#     # --- 4. PASS 2: MAINTENANCE STRUCTURE ---
#     maint = data.get("maintenance_and_stage_parameters", {})
#     for path in MAINT_REQUIRED_PATHS:
#         parts = path.split(" -> ")
#         temp = maint
#         for p in parts:
#             temp = temp.get(p) if isinstance(temp, dict) else None

#         if temp is None:
#             report["errors"].append(
#                 f"Maintenance Error: Missing mandatory path '{path}'"
#             )
#         else:
#             check_num(temp, f"Maintenance -> {path}")

#     # --- 5. PASS 3: TRAFFIC & ACCIDENT LOGIC ---
#     is_global = gp.get("use_global_road_user_calculations")

#     if is_global is False:
#         trd = data.get("traffic_and_road_data", {})
#         add_in = trd.get("additional_inputs", {})
#         veh_data = trd.get("vehicle_data", {})
#         sev_dist = trd.get("accident_severity_distribution", {})

#         # WPI Mapping References
#         medical_wpi = wpi.get("WPI", {}).get("medical_cost", {})
#         prop_damage_wpi = (
#             wpi.get("WPI", {}).get("vehicle_cost", {}).get("property_damage", {})
#         )

#         # A. Road Geometry / Carriageway Validation
#         valid_lane_codes = [
#             l["code"]
#             for l in suggestions.get("road_geometry", {}).get("lane_types", [])
#         ]
#         input_lane_code = add_in.get("alternate_road_carriageway")
#         if input_lane_code not in valid_lane_codes:
#             report["errors"].append(
#                 f"Geometry Error: '{input_lane_code}' is not a valid alternate_road_carriageway. Expected one of {valid_lane_codes}."
#             )


#         # B. Additional Numeric Field Validation
#         for f in ADDITIONAL_FIELDS:
#             check_num(add_in.get(f), f"additional_inputs -> {f}")

#         hourly_capacity = add_in.get("hourly_capacity")
#         std_capacity = CarriagewayStandards.get_capacity(input_lane_code)

#         if not isinstance(hourly_capacity, (int, float)) or hourly_capacity <= 0:
#             report["errors"].append("Provided 'hourly_capacity' must be a positive number.")
#         else:
#             # Compare with standard and add info if different
#             if hourly_capacity != std_capacity:
#                 report["info"].append(f"User-provided hourly_capacity ({hourly_capacity}) differs from standard ({std_capacity}).")

#         # C. Severity Distribution Logic
#         sev_total = sum(sev_dist.values()) if isinstance(sev_dist, dict) else 0
#         if not (99.8 <= round(sev_total, 2) <= 100.2):
#             report["errors"].append(
#                 f"Severity Error: Distribution sums to {round(sev_total, 2)}%, must be 100%."
#             )

#         for sev in ["fatal", "major", "minor"]:
#             if sev not in sev_dist:
#                 report["errors"].append(
#                     f"Missing Severity: '{sev}' required in distribution."
#                 )
#             if sev not in medical_wpi:
#                 report["errors"].append(
#                     f"WPI Error: No medical cost index for severity '{sev}'."
#                 )

#         # D. Vehicle Integrity & WPI Mapping
#         required_codes = [
#             v["code"] for v in suggestions.get("traffic", {}).get("vehicle_options", [])
#         ]
#         acc_total = 0
#         total_adt = 0

#         for code in required_codes:
#             if code not in veh_data:
#                 report["errors"].append(f"Missing Vehicle: '{code}' is required.")
#                 continue

#             v_vals = veh_data[code]
#             total_adt += v_vals.get("vehicles_per_day", 0)
#             acc_total += v_vals.get("accident_percentage", 0)

#             for attr in [
#                 "vehicles_per_day",
#                 "carbon_emissions_kgCO2e_per_km",
#                 "accident_percentage",
#             ]:
#                 check_num(v_vals.get(attr), f"vehicle_data -> {code} -> {attr}")

#             if code.lower() in ["mcv", "hcv"]:
#                 if "pwr" not in v_vals:
#                     report["errors"].append(
#                         f"Missing PWR: '{code}' requires 'pwr' field."
#                     )
#                 else:
#                     check_num(v_vals.get("pwr"), f"vehicle_data -> {code} -> pwr")

#             lookup_key = "o_buses" if code == "d_buses" else code
#             if lookup_key not in prop_damage_wpi:
#                 report["errors"].append(
#                     f"WPI Error: Missing property damage index for '{lookup_key}'."
#                 )

#         if total_adt <= 0:
#             report["errors"].append(
#                 "Traffic Error: Total ADT must be greater than zero."
#             )
#         if abs(acc_total - 100) > 0.1:
#             report["errors"].append(
#                 f"Accident Sum: Vehicle percentages sum to {round(acc_total, 2)}%, must be 100%."
#             )

#     elif is_global is True:
#         ruc_block = data.get("daily_road_user_cost_with_vehicular_emissions", {})
#         if ruc_block.get("total_daily_ruc") is None:
#             report["errors"].append("Global Error: Missing 'total_daily_ruc'")
#         if (
#             ruc_block.get("total_carbon_emission", {}).get("total_emission_kgCO2e")
#             is None
#         ):
#             report["errors"].append("Global Error: Missing 'total_emission_kgCO2e'")

#     return report


def ironclad_validator(input, suggestions, wpi):
    """
    Ironclad validator for OSDAG LCC inputs.
    Assumes:
    - All domain validation is enforced inside dataclasses.
    - This layer validates ecosystem consistency only.
    """

    report = {"errors": [], "warnings": [], "info": []}

    gp = input["general_parameters"]
    is_global = gp["use_global_road_user_calculations"]

    # --------------------------------------------------
    # GLOBAL MODE CHECK
    # --------------------------------------------------

    if is_global:
        # Ensure traffic block is not mistakenly used
        if "traffic_and_road_data" in input:
            report["warnings"].append(
                "Global mode enabled. traffic_and_road_data will be ignored."
            )

        # Ensure WPI still structurally usable
        if "WPI".lower() not in [k.lower() for k in wpi.keys()]:
            report["errors"].append(
                "WPI Error: Missing top-level 'WPI' block.")

        return report

    # --------------------------------------------------
    # NON-GLOBAL MODE VALIDATION
    # --------------------------------------------------

     # Ensure traffic data exists in non-global mode
    if "traffic_and_road_data" not in input:
        report["errors"].append(
            "Non-global mode requires traffic_and_road_data block."
        )
        return report

    trd = input["traffic_and_road_data"]
    add_in = trd["additional_inputs"]
    veh_data = trd["vehicle_data"]

    # --------------------------------------------------
    # 1. Suggestion Sync – Carriageway Code
    # --------------------------------------------------

    valid_lane_codes = [
        l["code"]
        for l in suggestions.get("road_geometry", {}).get("lane_types", [])
    ]

    if add_in["alternate_road_carriageway"] not in valid_lane_codes:
        report["errors"].append(
            f"Geometry Error: '{add_in['alternate_road_carriageway']}' "
            f"is not valid. Expected one of {valid_lane_codes}."
        )

    # --------------------------------------------------
    # 2. Capacity Comparison (Informational)
    # --------------------------------------------------

    try:
        std_capacity = CarriagewayStandards.get_capacity(
            add_in['alternate_road_carriageway']
        )

        if add_in['hourly_capacity'] != std_capacity:
            report["info"].append(
                f"User-provided hourly_capacity ({add_in['hourly_capacity']}) "
                f"differs from standard ({std_capacity})."
            )
    except Exception:
        report["warnings"].append(
            "Unable to fetch standard capacity for carriageway."
        )
    # ==========================================================
    # 3. Suggestion Sync – Required Vehicles
    # ==========================================================

    required_vehicle_codes = [
        v["code"]
        for v in suggestions.get("traffic", {}).get("vehicle_options", [])
    ]

    model_vehicle_codes = list(veh_data.keys())

    # Ensure all required suggestion vehicles exist in model
    for code in required_vehicle_codes:
        if code not in model_vehicle_codes:
            report["errors"].append(
                f"Traffic Sync Error: Required vehicle '{code}' missing in input."
            )

    # Ensure no unknown vehicle types appear
    for code in model_vehicle_codes:
        if code not in required_vehicle_codes:
            report["warnings"].append(
                f"Traffic Sync Warning: Unexpected vehicle '{code}' not defined in suggestions."
            )
    # --------------------------------------------------
    # 4. WPI Mapping Integrity
    # --------------------------------------------------

    medical_wpi = wpi.get("WPI", {}).get("medical_cost", {})
    prop_damage_wpi = (
        wpi.get("WPI", {}).get("vehicle_cost", {}).get("property_damage", {})
    )

    # Severity mapping
    for sev in ["fatal", "major", "minor"]:
        if sev not in medical_wpi:
            report["errors"].append(
                f"WPI Error: Missing medical cost index for severity '{sev}'."
            )

    # Vehicle mapping
    for code in veh_data.keys():

        lookup_key = "o_buses" if code == "d_buses" else code

        if lookup_key not in prop_damage_wpi:
            report["errors"].append(
                f"WPI Error: Missing property damage index for '{lookup_key}'."
            )

    return report
