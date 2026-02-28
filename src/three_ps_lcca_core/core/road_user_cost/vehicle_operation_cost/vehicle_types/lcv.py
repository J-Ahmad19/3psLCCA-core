from typing import Dict, Any, TypedDict
from ..utils import IRCSP302019TableC1
from ..utils.vocOutputBuilder import build_voc_output
from ..utils.commonInputs import VehicleInput, extract_vehicle_inputs
import math
from .... import standard_keys as c

Vehicle = c.LCV


def compute_voc(vehicle_input: VehicleInput) -> Dict[str, Any]:
    vt, W, RG, FL, RS, i_lane, lane, RF = extract_vehicle_inputs(vehicle_input)
    NP: Dict[str, int] = IRCSP302019TableC1.vehicle_costs[Vehicle]

    if vt == Vehicle:
        # -----------------------------
        # SPEED FORMULA
        # -----------------------------
        speed_map: Dict[str, float] = {
            c.SL: 49.87 - 0.4447 * RF - 0.00088 * (RG - 2000),
            c.IL: 53.70 - 0.4788 * RF - 0.00095 * (RG - 2000),
            c.L2: 57.41 - 0.5119 * RF - 0.00102 * (RG - 2000),
            c.L4: 74.897 - 0.163 * RF - 0.0031 * RG,
            c.L6: 77.036 - 0.163 * RF - 0.0031 * RG,
            c.L8: 79.174 - 0.163 * RF - 0.0031 * RG,
            c.EW: 70.620 - 0.163 * RF - 0.0031 * RG + 0.611 * W
        }

        V: float = speed_map.get(lane, 0.0)

        # -----------------------------
        # DISTANCE RELATED
        # -----------------------------

        # Fuel consumption
        petrol: float = 0
        diesel: float = 22.504 + (1708.244 / V) + 0.02591 * \
            (V ** 2) + 0.001612 * RG + 5.6863 * RS - 0.8744 * FL

        # Spare parts
        SP_ET: float = math.exp(-10.5615 + 0.000141 *
                                RG + 3.493 / W) * NP[c.ET]
        SP_IT: float = math.exp(-10.5615 + 0.000141 *
                                RG + 3.493 / W) * NP[c.IT]

        # Maintenance labour
        ML: float = 0.85773 * SP_IT

        # Tyre life
        TL: float = 22382 + 3817 * W - 375.3 * RF - 1.037 * RG

        # Engine oil
        EOL: float = 0.80679 + 0.019496 * RF + 0.0001297 * (RG / W)

        # Other oil
        OL: float = 2.0415 + 0.0001058 * RG

        # Grease
        G: float = 0.3661 + 0.0283 * RF + 0.000251 * RG

        # -----------------------------
        # TIME RELATED
        # -----------------------------

        # Utilisation
        UPD: float = 28.807 + 2.1836 * V

        # Fixed costs
        FXC_ET: float = 723.80 / UPD
        FXC_IT: float = 829.56 / UPD

        # Depreciation costs
        DC_ET: float = 120.90 / UPD
        DC_IT: float = 173.51 / UPD

        # Passenger time cost
        PT = 0

        # crew_cost
        crew: float = 900 / UPD

        # Commodity holding cost
        CHC: float
        if lane in [c.SL, c.IL]:
            CHC = 64.71 / UPD
        elif lane == c.L2:
            CHC = 71.35 / UPD
        elif lane in [c.L4, c.L6, c.L8]:
            CHC = 149.12 / UPD
        elif lane == c.EW:
            CHC = 149.12 / UPD
        else:
            raise ValueError(f"Invalid lane type: {lane}")

        # -----------------------------
        # BUILD FINAL OUTPUT
        # -----------------------------
        return build_voc_output(
            vt=vt, i_lane=i_lane, lane=lane,
            velocity=V,
            petrol=petrol, diesel=diesel,
            SP_ET=SP_ET, SP_IT=SP_IT,
            ML=ML, TL=TL,
            EOL=EOL, OL=OL, G=G,
            FXC_ET=FXC_ET, FXC_IT=FXC_IT,
            DC_ET=DC_ET, DC_IT=DC_IT,
            PT=PT, crew=crew, CHC=CHC,
            UPD=UPD
        )

    else:
        raise NotImplementedError(
            f"VOC computation for vehicle type '{vt}' is not implemented yet."
        )
