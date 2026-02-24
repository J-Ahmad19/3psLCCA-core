from dataclasses import dataclass, asdict
from typing import Dict

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
    DemolitionDisposal
)

@dataclass(frozen=True)
class TotalCarbonEmission:
    total_emission_kgCO2e: float

    def __post_init__(self):
        if not isinstance(self.total_emission_kgCO2e, (int, float)):
            raise TypeError("total_emission_kgCO2e must be numeric")
        if self.total_emission_kgCO2e < 0:
            raise ValueError("total_emission_kgCO2e must be >= 0")

@dataclass(frozen=True)
class DailyRoadUserCost:
    total_daily_ruc: float
    total_carbon_emission: TotalCarbonEmission

    def __post_init__(self):
        if not isinstance(self.total_daily_ruc, (int, float)):
            raise TypeError("total_daily_ruc must be numeric")
        if self.total_daily_ruc < 0:
            raise ValueError("total_daily_ruc must be >= 0")

@dataclass(frozen=True)
class InputGlobalMetaData:
    general_parameters: GeneralParameters
    daily_road_user_cost_with_vehicular_emissions: DailyRoadUserCost
    maintenance_and_stage_parameters: MaintenanceAndStageParameters

    def __post_init__(self):
        if not self.general_parameters.use_global_road_user_calculations:
            raise ValueError(
                "Global input requires use_global_road_user_calculations=True"
            )

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):

        general_parameters = GeneralParameters(
            **data["general_parameters"]
        )

        daily_ruc = DailyRoadUserCost(
            total_daily_ruc=data["daily_road_user_cost_with_vehicular_emissions"]["total_daily_ruc"],
            total_carbon_emission=TotalCarbonEmission(
                **data["daily_road_user_cost_with_vehicular_emissions"]["total_carbon_emission"]
            )
        )

        maintenance_data = MaintenanceAndStageParameters(
            use_stage_cost=UseStageCost(
                routine=Routine(
                    inspection=RoutineInspection(
                        **data["maintenance_and_stage_parameters"]["use_stage_cost"]["routine"]["inspection"]
                    ),
                    maintenance=RoutineMaintenance(
                        **data["maintenance_and_stage_parameters"]["use_stage_cost"]["routine"]["maintenance"]
                    )
                ),
                major=Major(
                    inspection=MajorInspection(
                        **data["maintenance_and_stage_parameters"]["use_stage_cost"]["major"]["inspection"]
                    ),
                    repair=MajorRepair(
                        **data["maintenance_and_stage_parameters"]["use_stage_cost"]["major"]["repair"]
                    )
                ),
                replacement_cost_for_bearing_and_expansion_joint=ReplacementCost(
                    **data["maintenance_and_stage_parameters"]["use_stage_cost"]["replacement_costs_for_bearing_and_expansion_joint"]
                )
            ),
            end_of_life_stage_costs=EndOfLifeStageCosts(
                demolition_and_disposal=DemolitionDisposal(
                    **data["maintenance_and_stage_parameters"]["end_of_life_stage_costs"]["demolition_and_disposal"]
                )
            )
        )

        return cls(
            general_parameters=general_parameters,
            daily_road_user_cost_with_vehicular_emissions=daily_ruc,
            maintenance_and_stage_parameters=maintenance_data
        )
