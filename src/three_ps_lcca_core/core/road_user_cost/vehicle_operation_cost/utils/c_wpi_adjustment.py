from typing import Any, Dict
from .... import standard_keys as c
from ..utils import IRCSP302019TableC1 as tableC1
from ..utils.constants import vehicle_type_list, petrolToDieselRatio


class VOCPostProcessor:
    def __init__(self, wpi_data: Dict[str, Any]):
        if "WPI" not in wpi_data:
            raise ValueError("CRITICAL: Root 'WPI' key missing from input.")
        self.wpi = wpi_data["WPI"]  # {vehicle: {cost_key: value}}

    def _wpi(self, vehicle_type: str, key: str) -> float:
        """Return WPI[vehicle][key] as a float."""
        v_key = c.O_BUSES if vehicle_type == c.BUSES else vehicle_type
        if v_key not in self.wpi:
            raise ValueError(f"CRITICAL: Vehicle '{v_key}' missing from WPI.")
        val = self.wpi[v_key].get(key)
        if val is None:
            raise ValueError(f"CRITICAL: '{key}' missing for vehicle '{v_key}' in WPI.")
        if not isinstance(val, (int, float)):
            raise ValueError(f"CRITICAL: WPI['{v_key}']['{key}'] must be numeric, got {type(val).__name__}")
        return val

    def _apply_adjustment(
        self, cost_base: Dict[str, float], mult: float, path: str
    ) -> Dict[str, Any]:
        """Strictly applies a multiplier. No defaults."""
        try:
            it_base = cost_base[c.IT] if c.IT in cost_base else cost_base[c.VALUE]
            et_base = cost_base[c.ET] if c.ET in cost_base else cost_base[c.VALUE]
        except KeyError:
            raise ValueError(
                f"CRITICAL: Base cost keys (IT/ET/VALUE) missing for {path}"
            )

        if c.VALUE in cost_base:
            debugger = {"base": it_base, "multiplier": mult, "path": path}
        else:
            debugger = {"base_it": it_base, "base_et": et_base, "multiplier": mult, "path": path}

        res = {
            "WPI_Debugger": debugger,
            c.UNIT: "Rs/km",
            c.iHTC: True,
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
                c.IT: (t_info[c.IT] * t_info[c.NUMBER_OF_WHEELS])
                / dist_s["tyre_life"][c.VALUE],
                c.ET: (t_info[c.ET] * t_info[c.NUMBER_OF_WHEELS])
                / dist_s["tyre_life"][c.VALUE],
            }
            dc["tyre_cost"] = self._apply_adjustment(
                b_tyre, self._wpi(vt, "tyre_cost"), f"WPI['{vt}']['tyre_cost']"
            )

            # --- Fuel & Lubricants ---
            f_cons = dist_s["fuel_consumption"]
            ratio = petrolToDieselRatio[vt]

            p_mult = self._wpi(vt, c.PETROL)
            d_mult = self._wpi(vt, c.DIESEL)

            p_it = (f_cons.get(c.PETROL, 0) * tableC1.petroleum_products_costs[c.PETROL][c.IT]) / 1000
            d_it = (f_cons.get(c.DIESEL, 0) * tableC1.petroleum_products_costs[c.DIESEL][c.IT]) / 1000
            p_et = (f_cons.get(c.PETROL, 0) * tableC1.petroleum_products_costs[c.PETROL][c.ET]) / 1000
            d_et = (f_cons.get(c.DIESEL, 0) * tableC1.petroleum_products_costs[c.DIESEL][c.ET]) / 1000

            dc["fuel_cost"] = {
                c.IT: (ratio[c.PETROL] * p_it * p_mult) + (ratio[c.DIESEL] * d_it * d_mult),
                c.ET: (ratio[c.PETROL] * p_et * p_mult) + (ratio[c.DIESEL] * d_et * d_mult),
                c.UNIT: "Rs/km",
                c.iHTC: True,
            }

            for oil in [c.ENGINE_OIL, c.OTHER_OIL, c.GREASE]:
                fac = 1000 if oil == c.ENGINE_OIL else 10000
                o_base = {
                    c.IT: (dist_s[oil][c.VALUE] * tableC1.petroleum_products_costs[oil][c.IT]) / fac,
                    c.ET: (dist_s[oil][c.VALUE] * tableC1.petroleum_products_costs[oil][c.ET]) / fac,
                }
                dc[oil] = self._apply_adjustment(o_base, self._wpi(vt, oil), f"WPI['{vt}']['{oil}']")

            # --- Maintenance ---
            m_mult = self._wpi(vt, "spare_parts")
            dc[c.SP] = self._apply_adjustment(
                {c.IT: dist_s[c.SP][c.IT], c.ET: dist_s[c.SP][c.ET]},
                m_mult, f"WPI['{vt}']['spare_parts']",
            )
            dc["maintenance_labour"] = self._apply_adjustment(
                {c.VALUE: dist_s["maintenance_labour"][c.VALUE]},
                m_mult, f"WPI['{vt}']['spare_parts'] (maintenance_labour)",
            )

            # --- Time Related ---
            tc["fixed_cost"] = self._apply_adjustment(
                {c.IT: time_s["fixed_cost"][c.IT], c.ET: time_s["fixed_cost"][c.ET]},
                self._wpi(vt, "fixed_depreciation"), f"WPI['{vt}']['fixed_depreciation']",
            )
            tc["crew_cost"] = self._apply_adjustment(
                {c.VALUE: time_s["crew_cost"][c.VALUE]},
                self._wpi(vt, "crew_cost"), f"WPI['{vt}']['crew_cost']",
            )
            tc["passenger_time_cost"] = self._apply_adjustment(
                {c.VALUE: time_s["passenger_time_cost"][c.VALUE]},
                self._wpi(vt, "passenger_cost"), f"WPI['{vt}']['passenger_cost']",
            )
            tc["commodity_holding_cost"] = self._apply_adjustment(
                {c.VALUE: time_s["commodity_holding_cost"][c.VALUE]},
                self._wpi(vt, "commodity_holding_cost"), f"WPI['{vt}']['commodity_holding_cost']",
            )
            tc["depreciation_cost"] = self._apply_adjustment(
                {c.IT: time_s["depreciation_cost"][c.IT], c.ET: time_s["depreciation_cost"][c.ET]},
                self._wpi(vt, "fixed_depreciation"), f"WPI['{vt}']['fixed_depreciation']",
            )

            # Totals
            tc["total_time_cost"] = {
                c.IT: sum(
                    v[c.IT] if c.IT in v else v[c.VALUE]
                    for k, v in tc.items()
                    if k not in ("WPI_Debugger", "total_time_cost")
                    and isinstance(v, dict)
                ),
                c.ET: sum(
                    v[c.ET] if c.ET in v else v[c.VALUE]
                    for k, v in tc.items()
                    if k not in ("WPI_Debugger", "total_time_cost")
                    and isinstance(v, dict)
                ),
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
                if comp_name in ("WPI_Debugger", "total_time_cost") or not isinstance(comp_values, dict):
                    continue
                total_cost[cost_type][vt][c.IT] += comp_values.get(
                    c.IT, comp_values.get(c.VALUE, 0.0)
                )
                total_cost[cost_type][vt][c.ET] += comp_values.get(
                    c.ET, comp_values.get(c.VALUE, 0.0)
                )
        total_cost[cost_type][c.UNITS] = "Rs/km/veh"
    return total_cost
