from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


# -----------------------------
# Project Metadata
# -----------------------------

@dataclass(frozen=True)
class ProjectMetaData:
    description: str
    standard: str
    country: str

@dataclass(frozen=True)
class GeneralParameters:
    service_life_years: int
    analysis_period_years: int
    discount_rate_percent: float
    inflation_rate_percent: float
    interest_rate_percent: float
    investment_ratio: float
    social_cost_of_carbon_per_mtco2e: float
    currency_conversion: float
    construction_period_months: float
    working_days_per_month: int
    days_per_month: int
    use_global_road_user_calculations: bool

    def __post_init__(self):
        if self.service_life_years <= 0:
            raise ValueError("service_life_years must be > 0")

        if not (0 <= self.investment_ratio <= 1):
            raise ValueError("investment_ratio must be between 0 and 1")

        for field in [
            self.discount_rate_percent,
            self.inflation_rate_percent,
            self.interest_rate_percent,
        ]:
            if field < 0:
                raise ValueError("Rates cannot be negative")

@dataclass(frozen=True)
class VehicleMetaData:
    vehicles_per_day: int
    carbon_emissions_kgCO2e_per_km: float
    accident_percentage: float
    pwr: Optional[float] = None

    def __post_init__(self):
        if self.vehicles_per_day < 0:
            raise ValueError("vehicles_per_day must be >= 0")

        if self.accident_percentage < 0:
            raise ValueError("accident_percentage must be >= 0")


@dataclass(frozen=True)
class VehicleData:
    small_cars: VehicleMetaData
    big_cars: VehicleMetaData
    two_wheelers: VehicleMetaData
    o_buses: VehicleMetaData
    d_buses: VehicleMetaData
    lcv: VehicleMetaData
    hcv: VehicleMetaData
    mcv: VehicleMetaData

    def __post_init__(self):
        for heavy in ["hcv", "mcv"]:
            vehicle = getattr(self, heavy)
            if vehicle.pwr is None:
                raise ValueError(f"{heavy} requires pwr value")

        total_acc = sum([
            self.small_cars.accident_percentage,
            self.big_cars.accident_percentage,
            self.two_wheelers.accident_percentage,
            self.o_buses.accident_percentage,
            self.d_buses.accident_percentage,
            self.lcv.accident_percentage,
            self.hcv.accident_percentage,
            self.mcv.accident_percentage,
        ])

        if abs(total_acc - 100) > 0.1:
            raise ValueError("Vehicle accident percentages must sum to 100")


@dataclass(frozen=True)
class AccidentSeverityDistribution:
    minor: float
    major: float
    fatal: float

    def __post_init__(self):
        total = self.minor + self.major + self.fatal
        if abs(total - 100) > 1e-6:
            raise ValueError(f"Accident severity must sum to 100. Got {total}")

@dataclass(frozen=True)
class AdditionalInputs:
    alternate_road_carriageway: str
    carriage_width_in_m: float
    road_roughness_mm_per_km: float
    road_rise_m_per_km: float
    road_fall_m_per_km: float
    additional_reroute_distance_km: float
    additional_travel_time_min: float
    crash_rate_accidents_per_million_km: float
    work_zone_multiplier: float
    peak_hour_traffic_percent_per_hour: List[float]
    hourly_capacity: int
    force_free_flow_off_peak: bool

    def __post_init__(self):
        numeric_fields = [
            self.road_roughness_mm_per_km,
            self.road_rise_m_per_km,
            self.road_fall_m_per_km,
            self.additional_reroute_distance_km,
            self.additional_travel_time_min,
            self.crash_rate_accidents_per_million_km,
            self.work_zone_multiplier,
            self.carriage_width_in_m,
        ]

        for val in numeric_fields:
            if val < 0:
                raise ValueError("Numeric additional_inputs values must be >= 0")

        if self.hourly_capacity <= 0:
            raise ValueError("hourly_capacity must be positive")


@dataclass(frozen=True)
class TrafficAndRoadData:
    vehicle_data: VehicleData
    accident_severity_distribution: AccidentSeverityDistribution
    additional_inputs: AdditionalInputs

@dataclass(frozen=True)
class RoutineInspection:
    percentage_of_initial_construction_cost_per_year: float
    interval_in_years: int

    def __post_init__(self):
        for key, val in asdict(self).items():
            if val < 0:
                raise ValueError(f"{key} must be >= 0")


@dataclass(frozen=True)
class RoutineMaintenance:
    percentage_of_initial_construction_cost_per_year: float
    percentage_of_initial_carbon_emission_cost: float
    interval_in_years: int

    def __post_init__(self):
        for key, val in asdict(self).items():
            if val < 0:
                raise ValueError(f"{key} must be >= 0")

@dataclass(frozen=True)
class Routine:
    inspection: RoutineInspection
    maintenance: RoutineMaintenance

@dataclass(frozen=True)
class MajorInspection:
    percentage_of_initial_construction_cost: float
    interval_for_repair_and_rehabitation_in_years: int

    def __post_init__(self):
        for key, val in asdict(self).items():
            if val < 0:
                raise ValueError(f"{key} must be >= 0")


@dataclass(frozen=True)
class MajorRepair:
    percentage_of_initial_construction_cost: float
    percentage_of_initial_carbon_emission_cost: float
    interval_for_repair_and_rehabitation_in_years: int
    repairs_duration_months: float

    def __post_init__(self):
        for key, val in asdict(self).items():
            if val < 0:
                raise ValueError(f"{key} must be >= 0")

@dataclass(frozen=True)
class Major:
    inspection: MajorInspection
    repair: MajorRepair

@dataclass(frozen=True)
class ReplacementCost:
    percentage_of_super_structure_cost: float
    interval_of_replacement_in_years: int
    duration_of_replacement_in_days: int

    def __post_init__(self):
        for key, val in asdict(self).items():
            if val < 0:
                raise ValueError(f"{key} must be >= 0")


@dataclass(frozen=True)
class UseStageCost:
    routine: Routine
    major: Major
    replacement_cost_for_bearing_and_expansion_joint: ReplacementCost

@dataclass(frozen=True)
class DemolitionDisposal:
    percentage_of_initial_construction_cost: float
    percentage_of_initial_carbon_emission_cost: float
    duration_for_demolition_and_disposal_in_months: float

    def __post_init__(self):
        for key, val in asdict(self).items():
            if val < 0:
                raise ValueError(f"{key} must be >= 0")


@dataclass(frozen=True)
class EndOfLifeStageCosts:
    demolition_and_disposal: DemolitionDisposal


@dataclass(frozen=True)
class MaintenanceAndStageParameters:
    use_stage_cost: UseStageCost
    end_of_life_stage_costs: EndOfLifeStageCosts


@dataclass(frozen=True)
class InputMetaData:
    project_metadata: ProjectMetaData
    general_parameters: GeneralParameters
    traffic_and_road_data: TrafficAndRoadData
    maintenance_and_stage_parameters: MaintenanceAndStageParameters

    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):

        project_metadata = ProjectMetaData(**data['project_metadata'])
        general_parameters = GeneralParameters(**data['general_parameters'])
        vehicle_data = VehicleData(
            **{
                k: VehicleMetaData(**v)
                for k, v in data['traffic_and_road_data']['vehicle_data'].items()
            }
        )
        traffic_data = TrafficAndRoadData(
            vehicle_data = vehicle_data,
            accident_severity_distribution=AccidentSeverityDistribution(
                **data['traffic_and_road_data']['accident_severity_distribution']
            ),
            additional_inputs=AdditionalInputs(
                **data['traffic_and_road_data']['additional_inputs']
            )
        )

        maintenance_data = MaintenanceAndStageParameters(
            use_stage_cost=UseStageCost(
                routine=Routine(
                    inspection=RoutineInspection(
                        **data['maintenance_and_stage_parameters']['use_stage_cost']['routine']['inspection']
                    ),
                    maintenance=RoutineMaintenance(
                        **data['maintenance_and_stage_parameters']['use_stage_cost']['routine']['maintenance']
                    )
                ),
                major=Major(
                    inspection=MajorInspection(
                        **data['maintenance_and_stage_parameters']['use_stage_cost']['major']['inspection']
                    ),
                    repair=MajorRepair(
                        **data['maintenance_and_stage_parameters']['use_stage_cost']['major']['repair']
                    )
                ),
                replacement_cost_for_bearing_and_expansion_joint=ReplacementCost(
                    **data['maintenance_and_stage_parameters']['use_stage_cost']['replacement_costs_for_bearing_and_expansion_joint']
                )
            ),
            end_of_life_stage_costs=EndOfLifeStageCosts(
                demolition_and_disposal=DemolitionDisposal(
                    **data['maintenance_and_stage_parameters']['end_of_life_stage_costs']['demolition_and_disposal']
                )
            )
        )

        return cls(
            project_metadata=project_metadata,
            general_parameters=general_parameters,
            traffic_and_road_data=traffic_data,
            maintenance_and_stage_parameters=maintenance_data
        )
