from dataclasses import dataclass, asdict
from typing import Dict

VEHICLES = [
    "small_cars", "big_cars", "two_wheelers", "o_buses",
    "d_buses", "lcv", "hcv", "mcv",
]


@dataclass(frozen=True)
class VehicleWPI:
    petrol: float
    diesel: float
    engine_oil: float
    other_oil: float
    grease: float
    property_damage: float
    tyre_cost: float
    spare_parts: float
    fixed_depreciation: float
    commodity_holding_cost: float
    passenger_cost: float
    crew_cost: float
    fatal: float
    major: float
    minor: float
    vot_cost: float

    def __post_init__(self):
        for field_name, value in self.__dict__.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"{field_name} must be numeric")
            if value <= 0:
                raise ValueError(f"{field_name} must be > 0")


@dataclass(frozen=True)
class WPIBlock:
    small_cars: VehicleWPI
    big_cars: VehicleWPI
    two_wheelers: VehicleWPI
    o_buses: VehicleWPI
    d_buses: VehicleWPI
    lcv: VehicleWPI
    hcv: VehicleWPI
    mcv: VehicleWPI


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
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):
        if "year" not in data:
            raise KeyError("WPI data missing 'year'")
        if "WPI" not in data:
            raise KeyError("WPI data missing 'WPI' block")
        wpi_raw = data["WPI"]
        vehicles = {}
        for v in VEHICLES:
            if v not in wpi_raw:
                raise KeyError(f"WPI block missing vehicle: '{v}'")
            try:
                vehicles[v] = VehicleWPI(**wpi_raw[v])
            except TypeError as e:
                raise TypeError(f"WPI['{v}']: {e}") from None
        return cls(year=data["year"], WPI=WPIBlock(**vehicles))
