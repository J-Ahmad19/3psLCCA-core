from typing import Dict, Any, TypedDict
from ..utils import IRCSP302019TableC1
from ..utils.vocOutputBuilder import build_voc_output
from ..utils.commonInputs import VehicleInput, extract_vehicle_inputs
from .... import standard_keys as c

Vehicle = c.BIG_CARS


def compute_voc(vehicle_input: VehicleInput) -> Dict[str, Any]:
    vt, W, RG, FL, RS, i_lane, lane, RF = extract_vehicle_inputs(vehicle_input)
    NP: Dict[str, int] = IRCSP302019TableC1.vehicle_costs[Vehicle]

    if vt == Vehicle:
        # -----------------------------
        # SPEED FORMULA
        # -----------------------------
        speed_map: Dict[str, float] = {
            c.SL: 67.04 - 0.6984 * RF - 0.002956 * (RG - 2000),
            c.IL: 73.82 - 0.7364 * RF - 0.002251 * (RG - 2000),
            c.L2: 81.92 - 0.7963 * RF - 0.001915 * (RG - 2000),
            c.L4: 100.625 - 0.394 * RF - 0.00330 * RG,
            c.L6: 104.159 - 0.398 * RF - 0.00333 * RG,
            c.L8: 107.743 - 0.402 * RF - 0.00337 * RG,
            c.EW: 97.53 - 0.402 * RF - 0.00337 * RG + 0.729 * W
        }

        V: float = speed_map.get(lane, 0.0)

        # -----------------------------
        # DISTANCE RELATED
        # -----------------------------

        # Fuel consumption
        petrol: float = 30 + (844.085 / V) + 0.003*(V**2) + \
            0.001*RG + 0.3414*RS - 0.2225*FL
        diesel: float = 35 + (983.503 / V) + 0.003*(V**2) + \
            0.002*RG + 0.339*RS - 0.4785*FL

        # Spare parts
        SP_ET: float = (0.0045 * (RG - 2000) * 1e-5) * NP[c.ET]
        SP_IT: float = (0.0045 * (RG - 2000) * 1e-5) * NP[c.IT]

        # Maintenance labour
        ML: float = 1.79934 * SP_ET

        # Tyre life
        TL: float = 68771 - 147.9*RF - 26.72*(RG/W)

        # Engine oil
        EOL: float = 1.8807 + 0.036615*RF + 0.000578*(RG/W)

        # Other oil
        OL: float = 1.631 + 0.05167*RF + 0.001867*(RG/W)

        # Grease
        G: float = 2.816 + 0.2007*RF

        # -----------------------------
        # TIME RELATED
        # -----------------------------

        # Utilisation
        UPD: float = 6.7378 * V

        # Fixed costs
        FXC_ET: float = 395.65 / UPD
        FXC_IT: float = 400.61 / UPD

        # Depreciation costs
        DC_ET: float = 42.83 / UPD
        DC_IT: float = 76.68 / UPD

        # Passenger time cost
        if lane in [c.SL, c.IL]:
            PT: float = 244.07 / V
        elif lane == c.L2:
            PT = 328.06 / V
        else:
            PT = 721.73 / V

        # crew_cost
        crew: float = 0.0

        # Commodity holding cost
        CHC: float = 0.0

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
