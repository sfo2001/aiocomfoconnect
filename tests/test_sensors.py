"""Unit tests for sensors module."""

import pytest
from aiocomfoconnect.sensors import (
    Sensor,
    SENSORS,
    SENSOR_DEVICE_STATE,
    SENSOR_TEMPERATURE_OUTDOOR,
    SENSOR_FAN_EXHAUST_DUTY,
    SENSOR_POWER_USAGE,
    SENSOR_UNIT_TEMPERATURE,
    SENSOR_RMOT,
    SENSOR_SEASON_HEATING_ACTIVE,
    SENSOR_AIRFLOW_CONSTRAINTS,
    UNIT_CELSIUS,
    UNIT_PERCENT,
    UNIT_WATT,
    UNIT_KWH,
    UNIT_VOLT,
    UNIT_RPM,
    UNIT_M3H,
)
from aiocomfoconnect.const import PdoType


class TestSensor:
    """Test Sensor dataclass."""
    
    def test_sensor_init_minimal(self):
        """Test Sensor initialization with minimal parameters."""
        sensor = Sensor(
            name="Test Sensor",
            unit=None,
            id=1,
            type=PdoType.TYPE_CN_UINT8
        )
        
        assert sensor.name == "Test Sensor"
        assert sensor.unit is None
        assert sensor.id == 1
        assert sensor.type == PdoType.TYPE_CN_UINT8
        assert sensor.value_fn is None
    
    def test_sensor_init_with_unit(self):
        """Test Sensor initialization with unit."""
        sensor = Sensor(
            name="Temperature",
            unit=UNIT_CELSIUS,
            id=2,
            type=PdoType.TYPE_CN_INT16
        )
        
        assert sensor.name == "Temperature"
        assert sensor.unit == UNIT_CELSIUS
        assert sensor.id == 2
        assert sensor.type == PdoType.TYPE_CN_INT16
        assert sensor.value_fn is None
    
    def test_sensor_init_with_value_fn(self):
        """Test Sensor initialization with value function."""
        value_fn = lambda x: x / 10
        sensor = Sensor(
            name="Temperature",
            unit=UNIT_CELSIUS,
            id=3,
            type=PdoType.TYPE_CN_INT16,
            value_fn=value_fn
        )
        
        assert sensor.name == "Temperature"
        assert sensor.unit == UNIT_CELSIUS
        assert sensor.id == 3
        assert sensor.type == PdoType.TYPE_CN_INT16
        assert sensor.value_fn == value_fn
    
    def test_sensor_equality(self):
        """Test Sensor equality comparison."""
        sensor1 = Sensor("Test", None, 1, PdoType.TYPE_CN_UINT8)
        sensor2 = Sensor("Test", None, 1, PdoType.TYPE_CN_UINT8)
        sensor3 = Sensor("Different", None, 1, PdoType.TYPE_CN_UINT8)
        
        assert sensor1 == sensor2
        assert sensor1 != sensor3
    
    def test_sensor_mutable(self):
        """Test that Sensor attributes can be modified."""
        sensor = Sensor("Test", None, 1, PdoType.TYPE_CN_UINT8)
        
        # Should be able to modify attributes since dataclass is not frozen
        sensor.name = "New Name"
        assert sensor.name == "New Name"


class TestSensorConstants:
    """Test sensor constants."""
    
    def test_unit_constants(self):
        """Test unit constants are defined correctly."""
        assert UNIT_WATT == "W"
        assert UNIT_KWH == "kWh"
        assert UNIT_VOLT == "V"
        assert UNIT_CELSIUS == "\u00b0C"
        assert UNIT_PERCENT == "%"
        assert UNIT_RPM == "rpm"
        assert UNIT_M3H == "m\u00b3/h"
    
    def test_sensor_id_constants(self):
        """Test sensor ID constants are integers."""
        assert isinstance(SENSOR_DEVICE_STATE, int)
        assert isinstance(SENSOR_TEMPERATURE_OUTDOOR, int)
        assert isinstance(SENSOR_FAN_EXHAUST_DUTY, int)
        assert isinstance(SENSOR_POWER_USAGE, int)
        
        # Test specific values
        assert SENSOR_DEVICE_STATE == 16
        assert SENSOR_FAN_EXHAUST_DUTY == 117
        assert SENSOR_POWER_USAGE == 128


class TestSensorsDictionary:
    """Test SENSORS dictionary."""
    
    def test_sensors_dict_not_empty(self):
        """Test SENSORS dictionary is not empty."""
        assert len(SENSORS) > 0
        assert isinstance(SENSORS, dict)
    
    def test_sensors_dict_keys_are_integers(self):
        """Test all keys in SENSORS are integers."""
        for key in SENSORS.keys():
            assert isinstance(key, int)
    
    def test_sensors_dict_values_are_sensor_objects(self):
        """Test all values in SENSORS are Sensor objects."""
        for value in SENSORS.values():
            assert isinstance(value, Sensor)
    
    def test_sensor_ids_match_dict_keys(self):
        """Test sensor IDs match their dictionary keys."""
        for sensor_id, sensor in SENSORS.items():
            assert sensor.id == sensor_id
    
    def test_specific_sensors_exist(self):
        """Test specific sensors exist in SENSORS dictionary."""
        assert SENSOR_DEVICE_STATE in SENSORS
        assert SENSOR_TEMPERATURE_OUTDOOR in SENSORS
        assert SENSOR_FAN_EXHAUST_DUTY in SENSORS
        assert SENSOR_POWER_USAGE in SENSORS
    
    def test_device_state_sensor(self):
        """Test device state sensor configuration."""
        sensor = SENSORS[SENSOR_DEVICE_STATE]
        
        assert sensor.name == "Device State"
        assert sensor.unit is None
        assert sensor.id == SENSOR_DEVICE_STATE
        assert sensor.type == PdoType.TYPE_CN_UINT8
        assert sensor.value_fn is None
    
    def test_temperature_outdoor_sensor(self):
        """Test outdoor temperature sensor configuration."""
        sensor = SENSORS[SENSOR_TEMPERATURE_OUTDOOR]
        
        assert sensor.name == "Outdoor Air Temperature"
        assert sensor.unit == UNIT_CELSIUS
        assert sensor.id == SENSOR_TEMPERATURE_OUTDOOR
        assert sensor.type == PdoType.TYPE_CN_INT16
        assert sensor.value_fn is not None
    
    def test_fan_exhaust_duty_sensor(self):
        """Test exhaust fan duty sensor configuration."""
        sensor = SENSORS[SENSOR_FAN_EXHAUST_DUTY]
        
        assert sensor.name == "Exhaust Fan Duty"
        assert sensor.unit == UNIT_PERCENT
        assert sensor.id == SENSOR_FAN_EXHAUST_DUTY
        assert sensor.type == PdoType.TYPE_CN_UINT8
        assert sensor.value_fn is None
    
    def test_power_usage_sensor(self):
        """Test power usage sensor configuration."""
        sensor = SENSORS[SENSOR_POWER_USAGE]
        
        assert sensor.name == "Power Usage"
        assert sensor.unit == UNIT_WATT
        assert sensor.id == SENSOR_POWER_USAGE
        assert sensor.type == PdoType.TYPE_CN_UINT16
        assert sensor.value_fn is None


class TestSensorValueFunctions:
    """Test sensor value transformation functions."""
    
    def test_temperature_value_function(self):
        """Test temperature sensors use division by 10."""
        sensor = SENSORS[SENSOR_TEMPERATURE_OUTDOOR]
        
        # Temperature value functions should divide by 10
        assert sensor.value_fn(100) == 10.0
        assert sensor.value_fn(250) == 25.0
        assert sensor.value_fn(-50) == -5.0
    
    def test_rmot_value_function(self):
        """Test RMOT sensor value function."""
        sensor = SENSORS[SENSOR_RMOT]
        
        assert sensor.value_fn(150) == 15.0
        assert sensor.value_fn(-20) == -2.0
    
    def test_unit_temperature_value_function(self):
        """Test unit temperature sensor value function."""
        sensor = SENSORS[SENSOR_UNIT_TEMPERATURE]
        
        assert sensor.value_fn(0) == "celcius"  # Note: matches original typo
        assert sensor.value_fn(1) == "farenheit"  # Note: matches original typo
        assert sensor.value_fn(2) == "farenheit"
    
    def test_season_heating_active_value_function(self):
        """Test season heating active sensor value function."""
        sensor = SENSORS[SENSOR_SEASON_HEATING_ACTIVE]
        
        assert sensor.value_fn(1) is True
        assert sensor.value_fn(0) is False
        assert sensor.value_fn(2) is True  # Any non-zero is True
    
    def test_airflow_constraints_value_function(self):
        """Test airflow constraints sensor has value function."""
        sensor = SENSORS[SENSOR_AIRFLOW_CONSTRAINTS]
        
        # Should have the calculate_airflow_constraints function
        assert sensor.value_fn is not None
        assert callable(sensor.value_fn)
    
    def test_sensors_with_no_value_function(self):
        """Test sensors that should have no value function."""
        sensors_without_value_fn = [
            SENSOR_DEVICE_STATE,
            SENSOR_FAN_EXHAUST_DUTY,
            SENSOR_POWER_USAGE,
        ]
        
        for sensor_id in sensors_without_value_fn:
            sensor = SENSORS[sensor_id]
            assert sensor.value_fn is None


class TestSensorUnits:
    """Test sensor units are assigned correctly."""
    
    def test_temperature_sensors_have_celsius_unit(self):
        """Test temperature sensors use Celsius unit."""
        temp_sensors = [
            SENSOR_TEMPERATURE_OUTDOOR,
            274,  # SENSOR_TEMPERATURE_EXTRACT
            275,  # SENSOR_TEMPERATURE_EXHAUST
            276,  # SENSOR_TEMPERATURE_SUPPLY
        ]
        
        for sensor_id in temp_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.unit == UNIT_CELSIUS
    
    def test_power_sensors_have_watt_unit(self):
        """Test power sensors use Watt unit."""
        power_sensors = [
            SENSOR_POWER_USAGE,
            213,  # SENSOR_AVOIDED_HEATING
            216,  # SENSOR_AVOIDED_COOLING
        ]
        
        for sensor_id in power_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.unit == UNIT_WATT
    
    def test_percentage_sensors_have_percent_unit(self):
        """Test percentage sensors use percent unit."""
        percent_sensors = [
            SENSOR_FAN_EXHAUST_DUTY,
            118,  # SENSOR_FAN_SUPPLY_DUTY
            227,  # SENSOR_BYPASS_STATE
        ]
        
        for sensor_id in percent_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.unit == UNIT_PERCENT
    
    def test_flow_sensors_have_m3h_unit(self):
        """Test flow sensors use m³/h unit."""
        flow_sensors = [
            119,  # SENSOR_FAN_EXHAUST_FLOW
            120,  # SENSOR_FAN_SUPPLY_FLOW
        ]
        
        for sensor_id in flow_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.unit == UNIT_M3H
    
    def test_speed_sensors_have_rpm_unit(self):
        """Test speed sensors use RPM unit."""
        speed_sensors = [
            121,  # SENSOR_FAN_EXHAUST_SPEED
            122,  # SENSOR_FAN_SUPPLY_SPEED
        ]
        
        for sensor_id in speed_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.unit == UNIT_RPM
    
    def test_unitless_sensors(self):
        """Test sensors that should have no unit."""
        unitless_sensors = [
            SENSOR_DEVICE_STATE,
            18,   # SENSOR_CHANGING_FILTERS
            192,  # SENSOR_DAYS_TO_REPLACE_FILTER
        ]
        
        for sensor_id in unitless_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.unit is None


class TestSensorTypes:
    """Test sensor PDO types are correct."""
    
    def test_uint8_sensors(self):
        """Test sensors with UINT8 type."""
        uint8_sensors = [
            SENSOR_DEVICE_STATE,
            SENSOR_FAN_EXHAUST_DUTY,
        ]
        
        for sensor_id in uint8_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.type == PdoType.TYPE_CN_UINT8
    
    def test_uint16_sensors(self):
        """Test sensors with UINT16 type."""
        uint16_sensors = [
            SENSOR_POWER_USAGE,
            119,  # SENSOR_FAN_EXHAUST_FLOW
            121,  # SENSOR_FAN_EXHAUST_SPEED
        ]
        
        for sensor_id in uint16_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.type == PdoType.TYPE_CN_UINT16
    
    def test_int16_sensors(self):
        """Test sensors with INT16 type."""
        int16_sensors = [
            SENSOR_TEMPERATURE_OUTDOOR,
            SENSOR_RMOT,
        ]
        
        for sensor_id in int16_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.type == PdoType.TYPE_CN_INT16
    
    def test_bool_sensors(self):
        """Test sensors with BOOL type."""
        bool_sensors = [
            SENSOR_SEASON_HEATING_ACTIVE,
        ]
        
        for sensor_id in bool_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.type == PdoType.TYPE_CN_BOOL
    
    def test_int64_sensors(self):
        """Test sensors with INT64 type."""
        int64_sensors = [
            SENSOR_AIRFLOW_CONSTRAINTS,
        ]
        
        for sensor_id in int64_sensors:
            if sensor_id in SENSORS:
                sensor = SENSORS[sensor_id]
                assert sensor.type == PdoType.TYPE_CN_INT64