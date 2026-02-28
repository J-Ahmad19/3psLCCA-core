import json
from three_ps_lcca_core.inputs.input import (
    InputMetaData,
    ProjectMetaData,
    GeneralParameters,
    TrafficAndRoadData,
    VehicleData,
    VehicleMetaData,
    AccidentSeverityDistribution,
    AdditionalInputs,
    MaintenanceAndStageParameters,
    UseStageCost,
    Routine,
    RoutineInspection,
    RoutineMaintenance,
    Major,
    MajorInspection,
    MajorRepair,
    ReplacementCost,
    EndOfLifeStageCosts,
    DemolitionDisposal,
)

Input_instance = InputMetaData(
    project_metadata=ProjectMetaData(
        description="Common input for OSDAG LCC Analysis",
        standard="IRC 106:1990 / IRC SP 30-2019",
        country="India",
    ),
    general_parameters=GeneralParameters(
        service_life_years=75,
        analysis_period_years=150,
        discount_rate_percent=6.7,
        inflation_rate_percent=5.15,
        interest_rate_percent=7.75,
        investment_ratio=0.5,
        social_cost_of_carbon_per_mtco2e=86.40,
        currency_conversion=88.73,
        construction_period_months=5.2,
        working_days_per_month=26,
        days_per_month=30,
        use_global_road_user_calculations=False,
    ),
    traffic_and_road_data=TrafficAndRoadData(
        vehicle_data=VehicleData(
            small_cars=VehicleMetaData(1405, 0.103, 12.18),
            big_cars=VehicleMetaData(5502, 0.269, 11.75),
            two_wheelers=VehicleMetaData(10359, 0.0351, 74.61),
            o_buses=VehicleMetaData(387, 0.45483, 0.88),
            d_buses=VehicleMetaData(394, 0.60644, 0),
            lcv=VehicleMetaData(3068, 0.307, 0),
            hcv=VehicleMetaData(1352, 0.7375, 0.59, pwr=8),
            mcv=VehicleMetaData(119, 0.5928, 0, pwr=7.22),
        ),
        accident_severity_distribution=AccidentSeverityDistribution(
            minor=25.7,
            major=61.42,
            fatal=12.88,
        ),
        additional_inputs=AdditionalInputs(
            alternate_road_carriageway="2L",
            carriage_width_in_m=8,
            road_roughness_mm_per_km=3000,
            road_rise_m_per_km=2,
            road_fall_m_per_km=2,
            additional_reroute_distance_km=0.2,
            additional_travel_time_min=0.525,
            crash_rate_accidents_per_million_km=3385.23,
            work_zone_multiplier=1.0,
            peak_hour_traffic_percent_per_hour=[0.10, 0.10, 0.10],
            hourly_capacity=1900,
            force_free_flow_off_peak=True,
        ),
    ),
    maintenance_and_stage_parameters=MaintenanceAndStageParameters(
        use_stage_cost=UseStageCost(
            routine=Routine(
                inspection=RoutineInspection(
                    percentage_of_initial_construction_cost_per_year=0.1,
                    interval_in_years=1,
                ),
                maintenance=RoutineMaintenance(
                    percentage_of_initial_construction_cost_per_year=0.55,
                    percentage_of_initial_carbon_emission_cost=0.55,
                    interval_in_years=5,
                ),
            ),
            major=Major(
                inspection=MajorInspection(
                    percentage_of_initial_construction_cost=0.5,
                    interval_for_repair_and_rehabitation_in_years=5,
                ),
                repair=MajorRepair(
                    percentage_of_initial_construction_cost=10,
                    percentage_of_initial_carbon_emission_cost=0.55,
                    interval_for_repair_and_rehabitation_in_years=20,
                    repairs_duration_months=3,
                ),
            ),
            replacement_costs_for_bearing_and_expansion_joint=ReplacementCost(
                percentage_of_super_structure_cost=12.5,
                interval_of_replacement_in_years=25,
                duration_of_replacement_in_days=2,
            ),
        ),
        end_of_life_stage_costs=EndOfLifeStageCosts(
            demolition_and_disposal=DemolitionDisposal(
                percentage_of_initial_construction_cost=10,
                percentage_of_initial_carbon_emission_cost=10,
                duration_for_demolition_and_disposal_in_months=1,
            )
        ),
    ),
)



# python -m examples.from_metadata.Input
if __name__ == "__main__":
    # Convert to dictionary
    Input = Input_instance.to_dict()
    print(json.dumps(Input, indent=4))
