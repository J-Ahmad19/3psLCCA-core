import json
from three_ps_lcca_core.inputs.input_global import (
    InputGlobalMetaData,
    DailyRoadUserCost,
    TotalCarbonEmission,
)

from three_ps_lcca_core.inputs.input import (
    GeneralParameters,
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

global_input_object = InputGlobalMetaData(
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
        use_global_road_user_calculations=True,
    ),
    daily_road_user_cost_with_vehicular_emissions=DailyRoadUserCost(
        total_daily_ruc=128618.886,
        total_carbon_emission=TotalCarbonEmission(
            total_emission_kgCO2e=772.24519225
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


# python -m examples.from_metadata.Input_global
if __name__ == "__main__":
    Input_global = global_input_object.to_dict()
    print(json.dumps(Input_global, indent=4))