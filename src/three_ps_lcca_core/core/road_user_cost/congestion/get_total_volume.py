from ... import standard_keys as c
from ...utils.dump_to_file import dump_to_file

def calculate_total_pcu(vehicle_data, debug=True):
    """
    Calculate PCU factors, total daily PCU, and PCU per hour
    based on IRC 106:1990 using vehicle counts per day.

    Parameters
    ----------
    vehicle_data : dict
        Vehicle type -> {"vehicles_per_day": count}
    debug : bool
        If True, prints debug info in JSON format.

    Returns
    -------
    dict
        {
            "pcu_values": {vehicle_type: PCU factor},
            "total_daily_pcu": float,
            "total_pcu_per_hour": float
        }
    """
    
    # PCU values for 5% and >=10% composition as per IRC 106:1990
    pcu_table = {
        c.TWO_WHEELERS:      (0.5, 0.75),
        c.SMALL_CARS:        (1.0, 1.0),
        c.BIG_CARS:          (1.0, 1.0),
        "auto_rickshaw":     (1.2, 2.0),
        c.LCV:               (1.4, 2.0),
        c.MCV:               (2.2, 3.7),
        c.HCV:               (2.2, 3.7),
        c.O_BUSES:           (2.2, 3.7),
        c.D_BUSES:           (2.2, 3.7),
        "cycle":             (0.4, 0.5),
        "cycle_rickshaw":    (1.5, 2.0),
        "tonga":             (1.5, 2.0),
        "hand_cart":         (2.0, 3.0)
    }
    
    debug_data = {}  # Collect debug info

    # 1️⃣ Calculate total vehicles to compute composition
    total_vehicles = sum(v.get("vehicles_per_day", 0) for v in vehicle_data.values())
    debug_data["total_vehicles"] = total_vehicles

    if total_vehicles == 0:
        return {
            "pcu_values": {},
            "total_daily_pcu": 0.0,
            "total_pcu_per_hour": 0.0
        }
    
    # 2️⃣ Compute traffic composition (%) per vehicle type
    traffic_composition = {}
    for vt, v in vehicle_data.items():
        traffic_composition[vt] = (v.get("vehicles_per_day", 0) / total_vehicles) * 100
    debug_data["traffic_composition"] = traffic_composition

    # 3️⃣ Calculate PCU factors based on composition
    pcu_values = {}
    pcu_calc_steps = {}  # detailed calculation steps
    for vt, percent in traffic_composition.items():
        percent = float(percent)
        if vt not in pcu_table:
            raise ValueError(f"PCU data not available for vehicle type: {vt}")
        pcu_5, pcu_10 = pcu_table[vt]
        if percent < 5:
            pcu = pcu_5
        elif 5 <= percent < 10:
            pcu = pcu_5 + (pcu_10 - pcu_5) * (percent - 5) / (10 - 5)
        else:  # >=10%
            pcu = pcu_10
        pcu = round(pcu, 2)
        pcu_values[vt] = pcu
        pcu_calc_steps[vt] = {
            "percent": percent,
            "pcu_5": pcu_5,
            "pcu_10": pcu_10,
            "calculated_pcu": pcu
        }
    debug_data["pcu_calculation"] = pcu_calc_steps

    # 4️⃣ Compute total daily PCU
    total_daily_pcu = sum(
        v.get("vehicles_per_day", 0) * pcu_values.get(vt, 0)
        for vt, v in vehicle_data.items()
    )
    debug_data["total_daily_pcu_raw"] = total_daily_pcu

    # 5️⃣ Compute PCU per hour (assuming uniform distribution over 24 hours)
    total_pcu_per_hour = total_daily_pcu / 24
    debug_data["total_pcu_per_hour_raw"] = total_pcu_per_hour

    # Round results
    total_daily_pcu = round(total_daily_pcu, 2)
    total_pcu_per_hour = round(total_pcu_per_hour, 2)

    result = {
        "pcu_values": pcu_values,
        "total_daily_pcu": total_daily_pcu,
        "total_pcu_per_hour": total_pcu_per_hour
    }

    if debug:
 
        dump_to_file("ruc-congestion-volume-capacity-summary.json", debug_data)
        
    return result