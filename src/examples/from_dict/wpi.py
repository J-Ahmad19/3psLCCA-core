import json
from three_ps_lcca_core.inputs.wpi import WPIMetaData
wpi = {
    "year": 2024,
    "WPI": {
        "fuel_cost": {
            "petrol": 1.8067915690866512,
            "diesel": 1.7733050847457628,
            "engine_oil": 1.4496951219512195,
            "other_oil": 1.6951351351351354,
            "grease": 1.6951351351351354,
        },
        "vehicle_cost": {
            "property_damage": {
                "small_cars": 1.1395759717314486,
                "big_cars": 1.1395759717314486,
                "two_wheelers": 1.1395759717314486,
                "o_buses": 1.1395759717314486,
                "d_buses": 1.1395759717314486,
                "lcv": 1.1395759717314486,
                "hcv": 1.1395759717314486,
                "mcv": 1.1395759717314486,
            },
            "tyre_cost": {
                "small_cars": 1.123991935483871,
                "big_cars": 1.123991935483871,
                "two_wheelers": 1.1336538461538461,
                "o_buses": 1.1702564102564101,
                "d_buses": 1.1702564102564101,
                "lcv": 1.1702564102564101,
                "hcv": 1.1702564102564101,
                "mcv": 1.1702564102564101,
            },
            "spare_parts": {
                "small_cars": 1.1395759717314486,
                "big_cars": 1.1395759717314486,
                "two_wheelers": 1.1395759717314486,
                "o_buses": 1.1395759717314486,
                "d_buses": 1.1395759717314486,
                "lcv": 1.1395759717314486,
                "hcv": 1.1395759717314486,
                "mcv": 1.1395759717314486,
            },
            "fixed_depreciation": {
                "small_cars": 1.1388400702987698,
                "big_cars": 1.1388400702987698,
                "two_wheelers": 1.1388400702987698,
                "o_buses": 1.1388400702987698,
                "d_buses": 1.1388400702987698,
                "lcv": 1.1388400702987698,
                "hcv": 1.1388400702987698,
                "mcv": 1.1388400702987698,
            },
        },
        "commodity_holding_cost": {
            "small_cars": 1.4788593903638152,
            "big_cars": 1.4788593903638152,
            "two_wheelers": 1.4788593903638152,
            "o_buses": 1.4788593903638152,
            "d_buses": 1.4788593903638152,
            "lcv": 1.4788593903638152,
            "hcv": 1.4788593903638152,
            "mcv": 1.4788593903638152,
        },
        "passenger_crew_cost": {
            "passenger_cost": 1.2706270627062706,
            "crew_cost": 1.2706270627062706,
        },
        "medical_cost": {
            "fatal": 1.0867924528301887,
            "major": 1.0867924528301887,
            "minor": 1.0867924528301887,
        },
        "vot_cost": {
            "small_cars": 1.2706270627062706,
            "big_cars": 1.2706270627062706,
            "two_wheelers": 1.2706270627062706,
            "o_buses": 1.2706270627062706,
            "d_buses": 1.2706270627062706,
            "lcv": 1.2706270627062706,
            "hcv": 1.2706270627062706,
            "mcv": 1.2706270627062706,
        },
    },
}

# python -m three_ps_lcca_core.Example.wpi
if __name__ == "__main__":
    wpi_metadata = WPIMetaData.from_dict(wpi)
    print(json.dumps(wpi_metadata.to_dict(), indent=4))
