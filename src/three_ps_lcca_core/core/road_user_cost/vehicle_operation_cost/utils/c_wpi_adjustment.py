from typing import Any, Dict
from .... import standard_keys as c
from ..utils import IRCSP302019TableC1 as tableC1
from ..utils.constants import vehicle_type_list, petrolToDieselRatio


class VOCPostProcessor:
    def __init__(self, wpi_data: Dict[str, Any]):
        if "WPI" not in wpi_data:
            raise ValueError("CRITICAL: Root 'WPI' key missing from input.")
        self.wpi = wpi_data["WPI"]
        self.v_cost_wpi = self.wpi.get("vehicleCost", {})

    def _get_strict_multiplier(self, category: str, vehicle_type: str, sub_key: str = None) -> float:  # type: ignore
        """
        Navigates the WPI JSON and extracts a FLOAT. 
        If sub_key is provided, it looks inside the resulting dict.
        """
        v_key = c.O_BUSES if vehicle_type == c.BUSES else vehicle_type
        val = None
        path = ""

        # 1. Try Top Level
        if category in self.wpi:
            block = self.wpi[category]
            path = f"WPI -> {category}"
            if isinstance(block, dict):
                if v_key in block:
                    val = block[v_key]
                    path += f" -> {v_key}"
                elif sub_key and sub_key in block:
                    val = block[sub_key]
                    path += f" -> {sub_key}"
                else:
                    raise ValueError(
                        f"CRITICAL: Key '{v_key}' or '{sub_key}' missing in {path}")
            else:
                val = block

        # 2. Try vehicleCost Level
        elif category in self.v_cost_wpi:
            block = self.v_cost_wpi[category]
            path = f"WPI -> vehicleCost -> {category}"
            if isinstance(block, dict):
                if v_key in block:
                    val = block[v_key]
                    path += f" -> {v_key}"
                else:
                    raise ValueError(
                        f"CRITICAL: Vehicle '{v_key}' missing in {path}")
            else:
                val = block
        else:
            raise ValueError(
                f"CRITICAL: Category '{category}' missing from WPI.")

        if not isinstance(val, (int, float)):
            raise ValueError(
                f"CRITICAL: Expected number at {path}, but got {type(val).__name__}")

        return val

    def _apply_adjustment(self, cost_base: Dict[str, float], mult: float, path: str) -> Dict[str, Any]:
        """Strictly applies a multiplier. No defaults."""
        try:
            it_base = cost_base[c.IT] if c.IT in cost_base else cost_base[c.VALUE]
            et_base = cost_base[c.ET] if c.ET in cost_base else cost_base[c.VALUE]
        except KeyError:
            raise ValueError(
                f"CRITICAL: Base cost keys (IT/ET/VALUE) missing for {path}")

        res = {
            "WPI_Debugger": {"base_it": it_base, "multiplier": mult, "path": path},
            c.UNIT: "Rs/km",
            c.iHTC: True
        }

        if c.VALUE in cost_base:
            res[c.VALUE] = it_base * mult
            res[c.iHTC] = False
        else:
            res[c.IT] = it_base * mult
            res[c.ET] = et_base * mult
        return res

    def process(self, voc_data: Dict[str, Any]) -> Dict[str, Any]:
        adjusted = {"distanceCost": {}, "timeCost": {}}

        for vt in vehicle_type_list:
            if vt not in voc_data:
                continue

            raw = voc_data[vt]["VOC_summary"]
            dist_s, time_s = raw["distance_related"], raw["time_related"]
            dc = adjusted["distanceCost"].setdefault(vt, {})
            tc = adjusted["timeCost"].setdefault(vt, {})

            # --- Tyres ---
            t_info = tableC1.new_tyres_costs[vt]
            b_tyre = {
                c.IT: (t_info[c.IT] * t_info[c.NUMBER_OF_WHEELS]) / dist_s["tyre_life"][c.VALUE],
                c.ET: (t_info[c.ET] * t_info[c.NUMBER_OF_WHEELS]
                       ) / dist_s["tyre_life"][c.VALUE]
            }
            dc["tyre_cost"] = self._apply_adjustment(
                b_tyre, self._get_strict_multiplier("tyre_cost", vt), f"tyre_cost for {vt}")

            # --- Fuel & Lubricants ---
            f_cons = dist_s["fuel_consumption"]
            ratio = petrolToDieselRatio[vt]

            p_mult = self._get_strict_multiplier(
                "fuel_cost", vt, sub_key=c.PETROL)
            d_mult = self._get_strict_multiplier(
                "fuel_cost", vt, sub_key=c.DIESEL)

            p_it = (f_cons.get(c.PETROL, 0) *
                    tableC1.petroleum_products_costs[c.PETROL][c.IT]) / 1000
            d_it = (f_cons.get(c.DIESEL, 0) *
                    tableC1.petroleum_products_costs[c.DIESEL][c.IT]) / 1000

            dc["fuel_cost"] = {
                c.IT: (ratio[c.PETROL] * p_it * p_mult) + (ratio[c.DIESEL] * d_it * d_mult),
                c.UNIT: "Rs/km", c.iHTC: True
            }

            for oil in [c.ENGINE_OIL, c.OTHER_OIL, c.GREASE]:
                o_mult = self._get_strict_multiplier(
                    "fuel_cost", vt, sub_key=oil)
                fac = 1000 if oil == c.ENGINE_OIL else 10000
                o_base = {c.VALUE: (
                    dist_s[oil][c.VALUE] * tableC1.petroleum_products_costs[oil][c.IT]) / fac}
                dc[oil] = self._apply_adjustment(
                    o_base, o_mult, f"fuel_cost -> {oil}")

            # --- Maintenance ---
            m_mult = self._get_strict_multiplier("spare_parts", vt)
            dc[c.SP] = self._apply_adjustment(
                {c.IT: dist_s[c.SP][c.IT], c.ET: dist_s[c.SP][c.ET]}, m_mult, "spare_parts")
            dc["maintenance_labour"] = self._apply_adjustment(
                {c.VALUE: dist_s["maintenance_labour"][c.VALUE]}, m_mult, "labour")

            # --- Time Related ---
            fd_mult = self._get_strict_multiplier("fixed_depreciation", vt)
            tc["fixed_cost"] = self._apply_adjustment(
                {c.IT: time_s["fixed_cost"][c.IT], c.ET: time_s["fixed_cost"][c.ET]}, fd_mult, "fixed_depreciation")

            pc_mult_crew = self._get_strict_multiplier(
                "passenger_crew_cost", vt, sub_key="crew_cost")
            pc_mult_pass = self._get_strict_multiplier(
                "passenger_crew_cost", vt, sub_key="passenger_cost")

            tc["crew_cost"] = self._apply_adjustment(
                {c.VALUE: time_s["crew_cost"][c.VALUE]}, pc_mult_crew, "crew_cost")
            tc["passenger_time_cost"] = self._apply_adjustment(
                {c.VALUE: time_s["passenger_time_cost"][c.VALUE]}, pc_mult_pass, "passCost")

            ch_mult = self._get_strict_multiplier("commodity_holding_cost", vt)
            tc["commodity_holding_cost"] = self._apply_adjustment(
                {c.VALUE: time_s["commodity_holding_cost"][c.VALUE]}, ch_mult, "commodityHolding")

            # Totals
            tc["total_time_cost"] = {
                c.IT: sum(v[c.IT] if c.IT in v else v[c.VALUE] for k, v in tc.items() if k != "WPI_Debugger" and isinstance(v, dict)),
                c.ET: sum(v[c.ET] if c.ET in v else v[c.VALUE] for k, v in tc.items() if k != "WPI_Debugger" and isinstance(v, dict)),
            }

        return adjusted


def calculate_total_cost(data: Dict[str, Any]) -> Dict[str, Any]:
    total_cost: Dict[str, Any] = {}
    for cost_type in ["distanceCost", "timeCost"]:
        if cost_type not in data:
            continue
        total_cost[cost_type] = {}
        for vt, components in data[cost_type].items():
            total_cost[cost_type][vt] = {c.IT: 0.0, c.ET: 0.0}
            for comp_name, comp_values in components.items():
                if comp_name == "WPI_Debugger" or not isinstance(comp_values, dict):
                    continue
                total_cost[cost_type][vt][c.IT] += comp_values.get(
                    c.IT, comp_values.get(c.VALUE, 0.0))
                total_cost[cost_type][vt][c.ET] += comp_values.get(
                    c.ET, comp_values.get(c.VALUE, 0.0))
        total_cost[cost_type][c.UNITS] = "Rs/km/veh"
    return total_cost
