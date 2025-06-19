"""Unit tests for const module."""

import pytest
from aiocomfoconnect.const import (
    PdoType,
    VentilationMode,
    VentilationSetting,
    VentilationBalance,
    VentilationTemperatureProfile,
    VentilationSpeed,
    ComfoCoolMode,
    BypassMode,
    AirflowSpeed,
    UNIT_NODE,
    UNIT_COMFOBUS,
    UNIT_ERROR,
    UNIT_TEMPHUMCONTROL,
    UNIT_NODECONFIGURATION,
    SUBUNIT_01,
    SUBUNIT_02,
    ERRORS_BASE,
    ERRORS,
    ERRORS_140,
    CAN_ID_OFFSET,
    PDO_SHIFT,
    UINT64_BITS,
    CONSTRAINT_BITS,
)


class TestPdoType:
    """Test PdoType enum."""
    
    def test_pdo_type_values(self):
        """Test PdoType enum values."""
        assert PdoType.TYPE_CN_BOOL == 0x00
        assert PdoType.TYPE_CN_UINT8 == 0x01
        assert PdoType.TYPE_CN_UINT16 == 0x02
        assert PdoType.TYPE_CN_UINT32 == 0x03
        assert PdoType.TYPE_CN_INT8 == 0x05
        assert PdoType.TYPE_CN_INT16 == 0x06
        assert PdoType.TYPE_CN_INT64 == 0x08
        assert PdoType.TYPE_CN_STRING == 0x09
        assert PdoType.TYPE_CN_TIME == 0x10
        assert PdoType.TYPE_CN_VERSION == 0x11
    
    def test_pdo_type_is_int_enum(self):
        """Test PdoType is an IntEnum."""
        from enum import IntEnum
        assert issubclass(PdoType, IntEnum)
        
        # Test that values can be used as integers
        assert PdoType.TYPE_CN_UINT8 + 1 == 2
        assert int(PdoType.TYPE_CN_BOOL) == 0


class TestUnitConstants:
    """Test unit constants."""
    
    def test_unit_constants_are_integers(self):
        """Test unit constants are integers."""
        units = [
            UNIT_NODE, UNIT_COMFOBUS, UNIT_ERROR, UNIT_TEMPHUMCONTROL,
            UNIT_NODECONFIGURATION
        ]
        
        for unit in units:
            assert isinstance(unit, int)
    
    def test_unit_constant_values(self):
        """Test specific unit constant values."""
        assert UNIT_NODE == 0x01
        assert UNIT_COMFOBUS == 0x02
        assert UNIT_ERROR == 0x03
        assert UNIT_TEMPHUMCONTROL == 0x1D
        assert UNIT_NODECONFIGURATION == 0x20
    
    def test_subunit_constants(self):
        """Test subunit constants."""
        assert SUBUNIT_01 == 0x01
        assert SUBUNIT_02 == 0x02
        assert isinstance(SUBUNIT_01, int)
        assert isinstance(SUBUNIT_02, int)


class TestVentilationMode:
    """Test VentilationMode enum."""
    
    def test_ventilation_mode_values(self):
        """Test VentilationMode enum values."""
        assert VentilationMode.AUTO.value == 0
        assert VentilationMode.MANUAL.value == 1
    
    def test_ventilation_mode_str(self):
        """Test VentilationMode string representation."""
        assert str(VentilationMode.AUTO) == "auto"
        assert str(VentilationMode.MANUAL) == "manual"
    
    def test_ventilation_mode_is_enum(self):
        """Test VentilationMode is an Enum."""
        from enum import Enum
        assert issubclass(VentilationMode, Enum)


class TestVentilationSetting:
    """Test VentilationSetting enum."""
    
    def test_ventilation_setting_values(self):
        """Test VentilationSetting enum values."""
        assert VentilationSetting.OFF == 0x00
        assert VentilationSetting.AUTO == 0x01
        assert VentilationSetting.ON == 0x02
    
    def test_ventilation_setting_str(self):
        """Test VentilationSetting string representation."""
        assert str(VentilationSetting.OFF) == "off"
        assert str(VentilationSetting.AUTO) == "auto"
        assert str(VentilationSetting.ON) == "on"
    
    def test_ventilation_setting_is_int_enum(self):
        """Test VentilationSetting is an IntEnum."""
        from enum import IntEnum
        assert issubclass(VentilationSetting, IntEnum)


class TestVentilationBalance:
    """Test VentilationBalance enum."""
    
    def test_ventilation_balance_values(self):
        """Test VentilationBalance enum values."""
        assert VentilationBalance.BALANCE.value == (0, 0)
        assert VentilationBalance.SUPPLY_ONLY.value == (1, 0)
        assert VentilationBalance.EXHAUST_ONLY.value == (0, 1)
    
    def test_ventilation_balance_str(self):
        """Test VentilationBalance string representation."""
        assert str(VentilationBalance.BALANCE) == "balance"
        assert str(VentilationBalance.SUPPLY_ONLY) == "supply_only"
        assert str(VentilationBalance.EXHAUST_ONLY) == "exhaust_only"
    
    def test_from_subunits_valid_combinations(self):
        """Test from_subunits with valid combinations."""
        assert VentilationBalance.from_subunits(0, 0) == VentilationBalance.BALANCE
        assert VentilationBalance.from_subunits(1, 0) == VentilationBalance.SUPPLY_ONLY
        assert VentilationBalance.from_subunits(0, 1) == VentilationBalance.EXHAUST_ONLY
    
    def test_from_subunits_invalid_combination(self):
        """Test from_subunits with invalid combination."""
        with pytest.raises(ValueError) as exc_info:
            VentilationBalance.from_subunits(1, 1)
        
        assert "Invalid mode combination: 6=1, 7=1" in str(exc_info.value)
    
    def test_from_subunits_other_invalid_combinations(self):
        """Test from_subunits with other invalid combinations."""
        invalid_combinations = [(2, 0), (0, 2), (-1, 0), (0, -1)]
        
        for mode_06, mode_07 in invalid_combinations:
            with pytest.raises(ValueError):
                VentilationBalance.from_subunits(mode_06, mode_07)


class TestVentilationTemperatureProfile:
    """Test VentilationTemperatureProfile enum."""
    
    def test_temperature_profile_values(self):
        """Test VentilationTemperatureProfile enum values."""
        assert VentilationTemperatureProfile.NORMAL == 0
        assert VentilationTemperatureProfile.COOL == 1
        assert VentilationTemperatureProfile.WARM == 2
    
    def test_temperature_profile_str(self):
        """Test VentilationTemperatureProfile string representation."""
        assert str(VentilationTemperatureProfile.NORMAL) == "normal"
        assert str(VentilationTemperatureProfile.COOL) == "cool"
        assert str(VentilationTemperatureProfile.WARM) == "warm"
    
    def test_temperature_profile_is_int_enum(self):
        """Test VentilationTemperatureProfile is an IntEnum."""
        from enum import IntEnum
        assert issubclass(VentilationTemperatureProfile, IntEnum)


class TestVentilationSpeed:
    """Test VentilationSpeed enum."""
    
    def test_ventilation_speed_values(self):
        """Test VentilationSpeed enum values."""
        assert VentilationSpeed.AWAY == 0
        assert VentilationSpeed.LOW == 1
        assert VentilationSpeed.MEDIUM == 2
        assert VentilationSpeed.HIGH == 3
    
    def test_ventilation_speed_str(self):
        """Test VentilationSpeed string representation."""
        assert str(VentilationSpeed.AWAY) == "away"
        assert str(VentilationSpeed.LOW) == "low"
        assert str(VentilationSpeed.MEDIUM) == "medium"
        assert str(VentilationSpeed.HIGH) == "high"
    
    def test_ventilation_speed_is_int_enum(self):
        """Test VentilationSpeed is an IntEnum."""
        from enum import IntEnum
        assert issubclass(VentilationSpeed, IntEnum)


class TestComfoCoolMode:
    """Test ComfoCoolMode enum."""
    
    def test_comfocool_mode_values(self):
        """Test ComfoCoolMode enum values."""
        assert ComfoCoolMode.AUTO == 0x00
        assert ComfoCoolMode.OFF == 0x01
    
    def test_comfocool_mode_str(self):
        """Test ComfoCoolMode string representation."""
        assert str(ComfoCoolMode.AUTO) == "auto"
        assert str(ComfoCoolMode.OFF) == "off"
    
    def test_comfocool_mode_is_int_enum(self):
        """Test ComfoCoolMode is an IntEnum."""
        from enum import IntEnum
        assert issubclass(ComfoCoolMode, IntEnum)


class TestBypassMode:
    """Test BypassMode enum."""
    
    def test_bypass_mode_values(self):
        """Test BypassMode enum values."""
        assert BypassMode.AUTO == 0
        assert BypassMode.OPEN == 1
        assert BypassMode.CLOSED == 2
    
    def test_bypass_mode_str(self):
        """Test BypassMode string representation."""
        assert str(BypassMode.AUTO) == "auto"
        assert str(BypassMode.OPEN) == "open"
        assert str(BypassMode.CLOSED) == "closed"
    
    def test_bypass_mode_is_int_enum(self):
        """Test BypassMode is an IntEnum."""
        from enum import IntEnum
        assert issubclass(BypassMode, IntEnum)


class TestAirflowSpeed:
    """Test AirflowSpeed enum."""
    
    def test_airflow_speed_values(self):
        """Test AirflowSpeed enum values."""
        assert AirflowSpeed.AWAY == 3
        assert AirflowSpeed.LOW == 4
        assert AirflowSpeed.MEDIUM == 5
        assert AirflowSpeed.HIGH == 6
    
    def test_airflow_speed_str(self):
        """Test AirflowSpeed string representation."""
        assert str(AirflowSpeed.AWAY) == "away"
        assert str(AirflowSpeed.LOW) == "low"
        assert str(AirflowSpeed.MEDIUM) == "medium"
        assert str(AirflowSpeed.HIGH) == "high"
    
    def test_airflow_speed_is_int_enum(self):
        """Test AirflowSpeed is an IntEnum."""
        from enum import IntEnum
        assert issubclass(AirflowSpeed, IntEnum)


class TestErrorDictionaries:
    """Test error message dictionaries."""
    
    def test_errors_base_not_empty(self):
        """Test ERRORS_BASE is not empty."""
        assert len(ERRORS_BASE) > 0
        assert isinstance(ERRORS_BASE, dict)
    
    def test_errors_not_empty(self):
        """Test ERRORS is not empty."""
        assert len(ERRORS) > 0
        assert isinstance(ERRORS, dict)
    
    def test_errors_140_not_empty(self):
        """Test ERRORS_140 is not empty."""
        assert len(ERRORS_140) > 0
        assert isinstance(ERRORS_140, dict)
    
    def test_errors_keys_are_integers(self):
        """Test error dictionary keys are integers."""
        for error_dict in [ERRORS_BASE, ERRORS, ERRORS_140]:
            for key in error_dict.keys():
                assert isinstance(key, int)
    
    def test_errors_values_are_strings(self):
        """Test error dictionary values are strings."""
        for error_dict in [ERRORS_BASE, ERRORS, ERRORS_140]:
            for value in error_dict.values():
                assert isinstance(value, str)
                assert len(value) > 0
    
    def test_errors_contains_base_errors(self):
        """Test ERRORS contains all ERRORS_BASE entries."""
        for key, value in ERRORS_BASE.items():
            assert key in ERRORS
            assert ERRORS[key] == value
    
    def test_errors_140_contains_base_errors(self):
        """Test ERRORS_140 contains all ERRORS_BASE entries."""
        for key, value in ERRORS_BASE.items():
            assert key in ERRORS_140
            assert ERRORS_140[key] == value
    
    def test_specific_error_messages(self):
        """Test specific error messages."""
        assert 21 in ERRORS_BASE
        assert "OVERHEATING" in ERRORS_BASE[21].upper()
        
        assert 77 in ERRORS
        assert "filter" in ERRORS[77].lower()
        
        assert 80 in ERRORS
        assert "SERVICE MODE" in ERRORS[80]
    
    def test_errors_has_more_entries_than_base(self):
        """Test ERRORS has more entries than ERRORS_BASE."""
        assert len(ERRORS) > len(ERRORS_BASE)
    
    def test_errors_140_has_different_mappings(self):
        """Test ERRORS_140 has different mappings than ERRORS for some keys."""
        # Error 70 should be different between ERRORS and ERRORS_140
        assert 70 in ERRORS
        assert 70 in ERRORS_140
        assert ERRORS[70] != ERRORS_140[70]


class TestAirflowConstraintConstants:
    """Test airflow constraint constants."""
    
    def test_airflow_constants_are_integers(self):
        """Test airflow constraint constants are integers."""
        assert isinstance(CAN_ID_OFFSET, int)
        assert isinstance(PDO_SHIFT, int)
        assert isinstance(UINT64_BITS, int)
    
    def test_airflow_constant_values(self):
        """Test specific airflow constant values."""
        assert CAN_ID_OFFSET == 0x40
        assert PDO_SHIFT == 14
        assert UINT64_BITS == 64
    
    def test_constraint_bits_not_empty(self):
        """Test CONSTRAINT_BITS is not empty."""
        assert len(CONSTRAINT_BITS) > 0
        assert isinstance(CONSTRAINT_BITS, dict)
    
    def test_constraint_bits_keys_are_integers(self):
        """Test CONSTRAINT_BITS keys are integers."""
        for key in CONSTRAINT_BITS.keys():
            assert isinstance(key, int)
            assert key >= 0
    
    def test_constraint_bits_values_are_strings(self):
        """Test CONSTRAINT_BITS values are strings."""
        for value in CONSTRAINT_BITS.values():
            assert isinstance(value, str)
            assert len(value) > 0
    
    def test_specific_constraint_bits(self):
        """Test specific constraint bit mappings."""
        assert CONSTRAINT_BITS[2] == "Resistance"
        assert CONSTRAINT_BITS[9] == "FrostProtection"
        assert CONSTRAINT_BITS[10] == "Bypass"
        assert CONSTRAINT_BITS[16] == "Hood"
        assert CONSTRAINT_BITS[19] == "ComfoCool"
    
    def test_co2_zone_constraints(self):
        """Test CO2 zone constraint mappings."""
        co2_zones = [47, 48, 49, 50, 51, 52, 53, 54]
        
        for i, zone_bit in enumerate(co2_zones, 1):
            assert zone_bit in CONSTRAINT_BITS
            assert f"CO2ZoneX{i}" in CONSTRAINT_BITS[zone_bit]


class TestEnumStringMethods:
    """Test all enum __str__ methods return lowercase."""
    
    def test_all_enums_str_lowercase(self):
        """Test all enum string representations are lowercase."""
        enums_and_values = [
            (VentilationMode.AUTO, "auto"),
            (VentilationMode.MANUAL, "manual"),
            (VentilationSetting.OFF, "off"),
            (VentilationSetting.AUTO, "auto"),
            (VentilationSetting.ON, "on"),
            (VentilationBalance.BALANCE, "balance"),
            (VentilationBalance.SUPPLY_ONLY, "supply_only"),
            (VentilationBalance.EXHAUST_ONLY, "exhaust_only"),
            (VentilationTemperatureProfile.NORMAL, "normal"),
            (VentilationTemperatureProfile.COOL, "cool"),
            (VentilationTemperatureProfile.WARM, "warm"),
            (VentilationSpeed.AWAY, "away"),
            (VentilationSpeed.LOW, "low"),
            (VentilationSpeed.MEDIUM, "medium"),
            (VentilationSpeed.HIGH, "high"),
            (ComfoCoolMode.AUTO, "auto"),
            (ComfoCoolMode.OFF, "off"),
            (BypassMode.AUTO, "auto"),
            (BypassMode.OPEN, "open"),
            (BypassMode.CLOSED, "closed"),
            (AirflowSpeed.AWAY, "away"),
            (AirflowSpeed.LOW, "low"),
            (AirflowSpeed.MEDIUM, "medium"),
            (AirflowSpeed.HIGH, "high"),
        ]
        
        for enum_value, expected_str in enums_and_values:
            assert str(enum_value) == expected_str
            assert str(enum_value).islower()


class TestEnumInheritance:
    """Test enum inheritance is correct."""
    
    def test_int_enum_inheritance(self):
        """Test IntEnum inheritance."""
        from enum import IntEnum
        
        int_enums = [
            PdoType,
            VentilationSetting,
            VentilationTemperatureProfile,
            VentilationSpeed,
            ComfoCoolMode,
            BypassMode,
            AirflowSpeed,
        ]
        
        for enum_class in int_enums:
            assert issubclass(enum_class, IntEnum)
    
    def test_enum_inheritance(self):
        """Test Enum inheritance."""
        from enum import Enum
        
        regular_enums = [
            VentilationMode,
            VentilationBalance,
        ]
        
        for enum_class in regular_enums:
            assert issubclass(enum_class, Enum)
            # Should not be IntEnum
            from enum import IntEnum
            assert not issubclass(enum_class, IntEnum)