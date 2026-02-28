from dataclasses import dataclass, asdict
from typing import Dict


@dataclass(frozen=True)
class fuel_cost:
    petrol: float
    diesel: float
    engine_oil: float
    other_oil: float
    grease: float

    def __post_init__(self):
        for field_name, value in self.__dict__.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field_name} must be numeric")
            if value < 0:
                raise ValueError(f"{field_name} must be >= 0")


@dataclass(frozen=True)
class vehicle_category_cost:
    small_cars: float
    big_cars: float
    two_wheelers: float
    o_buses: float
    d_buses: float
    lcv: float
    hcv: float
    mcv: float

    def __post_init__(self):
        for field_name, value in self.__dict__.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field_name} must be numeric")
            if value < 0:
                raise ValueError(f"{field_name} cost must be >= 0")


@dataclass(frozen=True)
class VehicleCost:
    property_damage: vehicle_category_cost
    tyre_cost: vehicle_category_cost
    spare_parts: vehicle_category_cost
    fixed_depreciation: vehicle_category_cost


@dataclass(frozen=True)
class commodity_holding_cost(vehicle_category_cost):
    pass


@dataclass(frozen=True)
class vot_cost(vehicle_category_cost):
    pass


@dataclass(frozen=True)
class passenger_crew_cost:
    passenger_cost: float
    crew_cost: float

    def __post_init__(self):
        for field_name, value in self.__dict__.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field_name} must be numeric")
            if value < 0:
                raise ValueError(f"{field_name} cost must be >= 0")


@dataclass(frozen=True)
class medical_cost:
    fatal: float
    major: float
    minor: float

    def __post_init__(self):
        for k, v in self.__dict__.items():
            if not isinstance(v, (int, float)):
                raise TypeError(f"Medical cost '{k}' must be numeric")
            if v < 0:
                raise ValueError(f"Medical cost '{k}' must be >= 0")


@dataclass(frozen=True)
class WPIBlock:
    fuel_cost: fuel_cost
    vehicleCost: VehicleCost
    commodity_holding_cost: commodity_holding_cost
    passenger_crew_cost: passenger_crew_cost
    medical_cost: medical_cost
    vot_cost: vot_cost


@dataclass(frozen=True)
class WPIMetaData:
    year: int
    WPI: WPIBlock

    def __post_init__(self):
        if not isinstance(self.year, int):
            raise TypeError("year must be integer")
        if self.year <= 0:
            raise ValueError("year must be positive")

    def to_dict(self):
        if isinstance(self, WPIMetaData):
            return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            year=data["year"],
            WPI=WPIBlock(
                fuel_cost=fuel_cost(**data["WPI"]["fuel_cost"]),
                vehicleCost=VehicleCost(
                    property_damage=vehicle_category_cost(
                        **data["WPI"]["vehicleCost"]["property_damage"]),
                    tyre_cost=vehicle_category_cost(
                        **data["WPI"]["vehicleCost"]["tyre_cost"]),
                    spare_parts=vehicle_category_cost(
                        **data["WPI"]["vehicleCost"]["spare_parts"]),
                    fixed_depreciation=vehicle_category_cost(
                        **data["WPI"]["vehicleCost"]["fixed_depreciation"]),
                ),
                commodity_holding_cost=commodity_holding_cost(
                    **data["WPI"]["commodity_holding_cost"]),
                passenger_crew_cost=passenger_crew_cost(
                    passenger_cost=data["WPI"]["passenger_crew_cost"]["passenger_cost"],
                    crew_cost=data["WPI"]["passenger_crew_cost"]["crew_cost"],
                ),
                medical_cost=medical_cost(**data["WPI"]["medical_cost"]),
                vot_cost=vot_cost(**data["WPI"]["vot_cost"]),
            )
        )
