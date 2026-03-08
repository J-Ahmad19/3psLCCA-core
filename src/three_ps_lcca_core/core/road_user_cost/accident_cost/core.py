from .IRCSP302019Table8_Table9 import (
    table8_Economic_Cost_for_Different_Type_of_Accidents,
    table9_Economic_Cost_of_Quantum_of_Vehicle_Damage_due_to_Accidents
)
from .input_validation import validate_accident_input
from ... import standard_keys as c
from ...utils.dump_to_file import dump_to_file


def accident_cost(traffic_input, wpi, debug=False):
    """
    Calculates total accident cost (INR/day)
    - Uses exposure-based accident calculation
    - Uses severity distribution for human cost
    - Uses vehicle accident % distribution for vehicle damage cost
    """

    is_valid, errors = validate_accident_input(traffic_input, wpi)
    if not is_valid:
        raise ValueError(
            f"Accident Input Validation Failed: {', '.join(errors)}"
        )

    # ------------------------------------------------------------------
    # 1. Extract Inputs
    # ------------------------------------------------------------------
    add_in = traffic_input["additional_inputs"]
    vehicle_data = traffic_input["vehicle_data"]
    severity_dist_percent = traffic_input["accident_severity_distribution"]

    # ------------------------------------------------------------------
    # 2. Exposure-Based Total Accident Calculation
    # ------------------------------------------------------------------
    total_adt = sum(v["vehicles_per_day"] for v in vehicle_data.values())
    dist_km = add_in["additional_reroute_distance_km"]
    crash_rate_annual = add_in["crash_rate_accidents_per_million_km"]
    wz_multiplier = add_in["work_zone_multiplier"]

    # Annual crash rate per million vehicle-km → daily accidents
    total_daily_accidents = (
        crash_rate_annual * wz_multiplier * dist_km
    ) / 1_000_000

    # ------------------------------------------------------------------
    # 3. Human Cost Calculation
    # ------------------------------------------------------------------
    human_cost_table = table8_Economic_Cost_for_Different_Type_of_Accidents()
    human_cost = 0
    calculated_severity_counts = {}
    human_breakdown = {}

    for severity, weight in severity_dist_percent.items():
        severity_count = total_daily_accidents * weight / 100
        calculated_severity_counts[severity] = round(severity_count, 8)

        base_cost = human_cost_table[severity]
        wpi_factor = wpi["WPI"]["medical_cost"][severity]
        adjusted_cost = base_cost * wpi_factor

        total_sev_cost = severity_count * adjusted_cost
        human_cost += total_sev_cost

        if debug:
            human_breakdown[severity] = {
                "severity_percentage": weight,
                "accident_count": round(severity_count, 8),
                "base_cost": base_cost,
                "wpi_factor": wpi_factor,
                "adjusted_cost": round(adjusted_cost, 2),
                "total_cost": round(total_sev_cost, 2)
            }

    # ------------------------------------------------------------------
    # 4. Vehicle Damage Cost (using accident % distribution)
    # ------------------------------------------------------------------
    damage_table = table9_Economic_Cost_of_Quantum_of_Vehicle_Damage_due_to_Accidents()
    vehicle_damage_cost = 0
    damage_breakdown = {}

    for v_key, v_info in vehicle_data.items():
        lookup_key = c.O_BUSES if v_key == c.D_BUSES else v_key

        if "accident_percentage" in v_info:
            accident_pct = v_info["accident_percentage"]
            note = None
        else:
            accident_pct = 0
            note = "accident_percentage missing; assumed 0"

        veh_accident_count = total_daily_accidents * accident_pct / 100

        base_dmg_cost = damage_table[lookup_key]
        wpi_factor = wpi["WPI"]["vehicle_cost"]["property_damage"][lookup_key]
        adj_dmg_cost = base_dmg_cost * wpi_factor

        total_veh_dmg_cost = veh_accident_count * adj_dmg_cost
        vehicle_damage_cost += total_veh_dmg_cost

        if debug:
            damage_breakdown[v_key] = {
                "lookup_key_used": lookup_key,
                "vehicles_per_day": v_info.get("vehicles_per_day"),
                "accident_percentage": accident_pct,
                "accident_count": round(veh_accident_count, 8),
                "base_damage_cost": base_dmg_cost,
                "wpi_factor": wpi_factor,
                "adjusted_damage_cost": round(adj_dmg_cost, 2),
                "total_cost": round(total_veh_dmg_cost, 2),
                "note": note
            }

    # ------------------------------------------------------------------
    # 5. Final Result
    # ------------------------------------------------------------------
    total_cost = human_cost + vehicle_damage_cost

    result = {
        "total_accident_cost_INR_per_day": round(total_cost, 2),
        "human_cost_INR_per_day": round(human_cost, 2),
        "vehicle_damage_cost_INR_per_day": round(vehicle_damage_cost, 2),
        "calculated_total_daily_accidents": round(total_daily_accidents, 8),
        "accident_severity_distribution_counts": calculated_severity_counts
    }

    # ------------------------------------------------------------------
    # 6. Debug Output (Full Trace)
    # ------------------------------------------------------------------
    if debug:
        debug_context = {
            "inputs": {
                "additional_inputs": add_in,
                "accident_severity_distribution_percent": severity_dist_percent
            },
            "exposure_calculation": {
                "total_adt": total_adt,
                "additional_reroute_distance_km": dist_km,
                "crash_rate_accidents_per_million_km": crash_rate_annual,
                "work_zone_multiplier": wz_multiplier,
                "total_daily_accidents": round(total_daily_accidents, 8)
            },
            "distribution_checks": {
                "severity_percentage_sum": sum(severity_dist_percent.values()),
                "vehicle_accident_percentage_sum": round(
                    sum(v.get("accident_percentage", 0)
                        for v in vehicle_data.values()), 2
                )
            },
            "assumptions": [
                "Crash rate assumed annual per million vehicle-km",
                "Total accidents scaled to daily basis",
                "Vehicle damage cost allocated using vehicle accident_percentage",
                "Missing accident_percentage values assumed as 0",
                "d_buses mapped to o_buses for damage cost lookup"
            ]
        }

        dump_to_file(
            "ruc-accident_cost_summary.json",
            {
                "summary": result,
                "debug_context": debug_context,
                "human_cost_breakdown": human_breakdown,
                "vehicle_damage_breakdown": damage_breakdown
            }
        )

    return result
