"""Unit tests for util module."""

import pytest
from aiocomfoconnect.util import (
    bytestring,
    bytearray_to_bits,
    uint_to_bits,
    version_decode,
    pdo_to_can,
    can_to_pdo,
    calculate_airflow_constraints,
    encode_pdo_value,
)
from aiocomfoconnect.const import PdoType


class TestBytestring:
    """Test bytestring function."""
    
    def test_bytestring_with_integers(self):
        """Test bytestring with array of integers."""
        result = bytestring([1, 2, 3, 4])
        expected = b'\x01\x02\x03\x04'
        assert result == expected
    
    def test_bytestring_with_bytes(self):
        """Test bytestring with array of bytes."""
        result = bytestring([b'\x01', b'\x02', b'\x03'])
        expected = b'\x01\x02\x03'
        assert result == expected
    
    def test_bytestring_with_mixed_array(self):
        """Test bytestring with mixed array of integers and bytes."""
        result = bytestring([1, b'\x02', 3, b'\x04'])
        expected = b'\x01\x02\x03\x04'
        assert result == expected
    
    def test_bytestring_empty_array(self):
        """Test bytestring with empty array."""
        result = bytestring([])
        expected = b''
        assert result == expected
    
    def test_bytestring_single_integer(self):
        """Test bytestring with single integer."""
        result = bytestring([255])
        expected = b'\xff'
        assert result == expected
    
    def test_bytestring_single_byte(self):
        """Test bytestring with single byte."""
        result = bytestring([b'\xff'])
        expected = b'\xff'
        assert result == expected
    
    def test_bytestring_zero_values(self):
        """Test bytestring with zero values."""
        result = bytestring([0, b'\x00', 0])
        expected = b'\x00\x00\x00'
        assert result == expected


class TestBytearrayToBits:
    """Test bytearray_to_bits function."""
    
    def test_bytearray_to_bits_single_byte(self):
        """Test bytearray_to_bits with single byte."""
        # 0b00000001 = 1, should set bit 0
        result = bytearray_to_bits(bytearray([1]))
        assert result == [0]
    
    def test_bytearray_to_bits_multiple_bits_single_byte(self):
        """Test bytearray_to_bits with multiple bits in single byte."""
        # 0b00000101 = 5, should set bits 0 and 2
        result = bytearray_to_bits(bytearray([5]))
        assert result == [0, 2]
    
    def test_bytearray_to_bits_multiple_bytes(self):
        """Test bytearray_to_bits with multiple bytes."""
        # First byte: 0b00000001 = 1 (bit 0)
        # Second byte: 0b00000010 = 2 (bit 9, since it's the second byte)
        result = bytearray_to_bits(bytearray([1, 2]))
        assert result == [0, 9]
    
    def test_bytearray_to_bits_all_bits_set(self):
        """Test bytearray_to_bits with all bits set in single byte."""
        # 0b11111111 = 255
        result = bytearray_to_bits(bytearray([255]))
        expected = list(range(8))  # bits 0-7
        assert result == expected
    
    def test_bytearray_to_bits_no_bits_set(self):
        """Test bytearray_to_bits with no bits set."""
        result = bytearray_to_bits(bytearray([0]))
        assert result == []
    
    def test_bytearray_to_bits_empty_bytearray(self):
        """Test bytearray_to_bits with empty bytearray."""
        result = bytearray_to_bits(bytearray([]))
        assert result == []
    
    def test_bytearray_to_bits_complex_pattern(self):
        """Test bytearray_to_bits with complex bit pattern."""
        # 0b10101010 = 170 (bits 1, 3, 5, 7)
        result = bytearray_to_bits(bytearray([170]))
        assert result == [1, 3, 5, 7]


class TestUintToBits:
    """Test uint_to_bits function."""
    
    def test_uint_to_bits_single_bit(self):
        """Test uint_to_bits with single bit set."""
        result = uint_to_bits(1)
        assert result == [0]
    
    def test_uint_to_bits_multiple_bits(self):
        """Test uint_to_bits with multiple bits set."""
        # 5 = 0b101, bits 0 and 2
        result = uint_to_bits(5)
        assert result == [0, 2]
    
    def test_uint_to_bits_large_number(self):
        """Test uint_to_bits with large number."""
        # 2^45 should set bit 45
        result = uint_to_bits(2**45)
        assert 45 in result
        assert len(result) == 1
    
    def test_uint_to_bits_zero(self):
        """Test uint_to_bits with zero."""
        result = uint_to_bits(0)
        assert result == []
    
    def test_uint_to_bits_max_64bit(self):
        """Test uint_to_bits with maximum value that fits in 64 bits."""
        # Set bit 63 (highest bit in 64-bit range tested)
        result = uint_to_bits(2**63)
        assert 63 in result
    
    def test_uint_to_bits_pattern(self):
        """Test uint_to_bits with specific pattern."""
        # 0b1010 = 10 (bits 1 and 3)
        result = uint_to_bits(10)
        assert result == [1, 3]


class TestVersionDecode:
    """Test version_decode function."""
    
    def test_version_decode_u_prefix(self):
        """Test version_decode with U prefix (v_1 = 0)."""
        # Create version with v_1=0, v_2=1, v_3=2, v_4=3
        version = (0 << 30) | (1 << 20) | (2 << 10) | 3
        result = version_decode(version)
        assert result == "U1.2.3"
    
    def test_version_decode_d_prefix(self):
        """Test version_decode with D prefix (v_1 = 1)."""
        version = (1 << 30) | (10 << 20) | (20 << 10) | 30
        result = version_decode(version)
        assert result == "D10.20.30"
    
    def test_version_decode_p_prefix(self):
        """Test version_decode with P prefix (v_1 = 2)."""
        version = (2 << 30) | (5 << 20) | (6 << 10) | 7
        result = version_decode(version)
        assert result == "P5.6.7"
    
    def test_version_decode_r_prefix(self):
        """Test version_decode with R prefix (v_1 = 3)."""
        version = (3 << 30) | (100 << 20) | (200 << 10) | 300
        result = version_decode(version)
        assert result == "R100.200.300"
    
    def test_version_decode_zero_version(self):
        """Test version_decode with zero version."""
        result = version_decode(0)
        assert result == "U0.0.0"
    
    def test_version_decode_max_values(self):
        """Test version_decode with maximum values in each field."""
        # Max values: v_2=1023, v_3=1023, v_4=1023
        version = (0 << 30) | (1023 << 20) | (1023 << 10) | 1023
        result = version_decode(version)
        assert result == "U1023.1023.1023"


class TestPdoToCan:
    """Test pdo_to_can function."""
    
    def test_pdo_to_can_default_node(self):
        """Test pdo_to_can with default node ID."""
        result = pdo_to_can(1)
        # ((1 << 14) + 0x40 + 1) = 16384 + 64 + 1 = 16449 = 0x4041
        expected = "00004041"
        assert result == expected
    
    def test_pdo_to_can_custom_node(self):
        """Test pdo_to_can with custom node ID."""
        result = pdo_to_can(1, node_id=5)
        # ((1 << 14) + 0x40 + 5) = 16384 + 64 + 5 = 16453 = 0x4045
        expected = "00004045"
        assert result == expected
    
    def test_pdo_to_can_large_pdo(self):
        """Test pdo_to_can with large PDO value."""
        result = pdo_to_can(255)
        # ((255 << 14) + 0x40 + 1) = 4177920 + 64 + 1 = 4177985 = 0x3fc041
        expected = "003fc041"
        assert result == expected
    
    def test_pdo_to_can_zero_pdo(self):
        """Test pdo_to_can with zero PDO."""
        result = pdo_to_can(0)
        # ((0 << 14) + 0x40 + 1) = 0 + 64 + 1 = 65 = 0x41
        expected = "00000041"
        assert result == expected


class TestCanToPdo:
    """Test can_to_pdo function."""
    
    def test_can_to_pdo_default_node(self):
        """Test can_to_pdo with default node ID."""
        result = can_to_pdo("00004041")
        # (0x4041 - 0x40 - 1) >> 14 = (16449 - 64 - 1) >> 14 = 16384 >> 14 = 1
        assert result == 1
    
    def test_can_to_pdo_custom_node(self):
        """Test can_to_pdo with custom node ID."""
        result = can_to_pdo("00004045", node_id=5)
        # (0x4045 - 0x40 - 5) >> 14 = (16453 - 64 - 5) >> 14 = 16384 >> 14 = 1
        assert result == 1
    
    def test_can_to_pdo_large_can(self):
        """Test can_to_pdo with large CAN value."""
        result = can_to_pdo("003fc041")
        # (0x3fc041 - 0x40 - 1) >> 14 = (4177985 - 64 - 1) >> 14 = 4177920 >> 14 = 255
        assert result == 255
    
    def test_can_to_pdo_roundtrip(self):
        """Test can_to_pdo and pdo_to_can roundtrip."""
        original_pdo = 123
        can_id = pdo_to_can(original_pdo)
        recovered_pdo = can_to_pdo(can_id)
        assert recovered_pdo == original_pdo


class TestCalculateAirflowConstraints:
    """Test calculate_airflow_constraints function."""
    
    def test_calculate_airflow_constraints_no_bit_45(self):
        """Test calculate_airflow_constraints when bit 45 is not set."""
        # Value without bit 45 set
        value = 0b1111  # bits 0-3
        result = calculate_airflow_constraints(value)
        assert result is None
    
    def test_calculate_airflow_constraints_bit_45_only(self):
        """Test calculate_airflow_constraints with only bit 45 set."""
        value = 2**45  # Only bit 45
        result = calculate_airflow_constraints(value)
        assert result == []
    
    def test_calculate_airflow_constraints_resistance(self):
        """Test calculate_airflow_constraints with resistance bits."""
        value = (2**45) | (2**2)  # bit 45 + bit 2
        result = calculate_airflow_constraints(value)
        assert "Resistance" in result
        
        value = (2**45) | (2**3)  # bit 45 + bit 3
        result = calculate_airflow_constraints(value)
        assert "Resistance" in result
    
    def test_calculate_airflow_constraints_preheater_negative(self):
        """Test calculate_airflow_constraints with preheater negative bit."""
        value = (2**45) | (2**4)  # bit 45 + bit 4
        result = calculate_airflow_constraints(value)
        assert "PreheaterNegative" in result
    
    def test_calculate_airflow_constraints_noise_guard(self):
        """Test calculate_airflow_constraints with noise guard bits."""
        value = (2**45) | (2**5)  # bit 45 + bit 5
        result = calculate_airflow_constraints(value)
        assert "NoiseGuard" in result
        
        value = (2**45) | (2**7)  # bit 45 + bit 7
        result = calculate_airflow_constraints(value)
        assert "NoiseGuard" in result
    
    def test_calculate_airflow_constraints_frost_protection(self):
        """Test calculate_airflow_constraints with frost protection bit."""
        value = (2**45) | (2**9)  # bit 45 + bit 9
        result = calculate_airflow_constraints(value)
        assert "FrostProtection" in result
    
    def test_calculate_airflow_constraints_bypass(self):
        """Test calculate_airflow_constraints with bypass bit."""
        value = (2**45) | (2**10)  # bit 45 + bit 10
        result = calculate_airflow_constraints(value)
        assert "Bypass" in result
    
    def test_calculate_airflow_constraints_analog_inputs(self):
        """Test calculate_airflow_constraints with analog input bits."""
        analog_inputs = [
            (12, "AnalogInput1"),
            (13, "AnalogInput2"),
            (14, "AnalogInput3"),
            (15, "AnalogInput4"),
        ]
        
        for bit, expected_constraint in analog_inputs:
            value = (2**45) | (2**bit)
            result = calculate_airflow_constraints(value)
            assert expected_constraint in result
    
    def test_calculate_airflow_constraints_hood(self):
        """Test calculate_airflow_constraints with hood bit."""
        value = (2**45) | (2**16)  # bit 45 + bit 16
        result = calculate_airflow_constraints(value)
        assert "Hood" in result
    
    def test_calculate_airflow_constraints_comfocool(self):
        """Test calculate_airflow_constraints with ComfoCool bit."""
        value = (2**45) | (2**19)  # bit 45 + bit 19
        result = calculate_airflow_constraints(value)
        assert "ComfoCool" in result
    
    def test_calculate_airflow_constraints_co2_zones(self):
        """Test calculate_airflow_constraints with CO2 zone bits."""
        co2_zones = [
            (47, "CO2ZoneX1"),
            (48, "CO2ZoneX2"),
            (49, "CO2ZoneX3"),
            (50, "CO2ZoneX4"),
            (51, "CO2ZoneX5"),
            (52, "CO2ZoneX6"),
            (53, "CO2ZoneX7"),
            (54, "CO2ZoneX8"),
        ]
        
        for bit, expected_constraint in co2_zones:
            value = (2**45) | (2**bit)
            result = calculate_airflow_constraints(value)
            assert expected_constraint in result
    
    def test_calculate_airflow_constraints_multiple_constraints(self):
        """Test calculate_airflow_constraints with multiple constraints."""
        # Set bit 45 + resistance (bit 2) + bypass (bit 10) + hood (bit 16)
        value = (2**45) | (2**2) | (2**10) | (2**16)
        result = calculate_airflow_constraints(value)
        
        assert "Resistance" in result
        assert "Bypass" in result
        assert "Hood" in result
        assert len(result) == 3


class TestEncodePdoValue:
    """Test encode_pdo_value function."""
    
    def test_encode_pdo_value_bool_true(self):
        """Test encode_pdo_value with boolean True."""
        result = encode_pdo_value(1, PdoType.TYPE_CN_BOOL)
        assert result == True.to_bytes()
    
    def test_encode_pdo_value_bool_false(self):
        """Test encode_pdo_value with boolean False."""
        result = encode_pdo_value(0, PdoType.TYPE_CN_BOOL)
        assert result == False.to_bytes()
    
    def test_encode_pdo_value_uint8(self):
        """Test encode_pdo_value with UINT8."""
        result = encode_pdo_value(255, PdoType.TYPE_CN_UINT8)
        expected = (255).to_bytes(1, "little", signed=False)
        assert result == expected
    
    def test_encode_pdo_value_uint16(self):
        """Test encode_pdo_value with UINT16."""
        result = encode_pdo_value(65535, PdoType.TYPE_CN_UINT16)
        expected = (65535).to_bytes(2, "little", signed=False)
        assert result == expected
    
    def test_encode_pdo_value_uint32(self):
        """Test encode_pdo_value with UINT32."""
        result = encode_pdo_value(4294967295, PdoType.TYPE_CN_UINT32)
        expected = (4294967295).to_bytes(4, "little", signed=False)
        assert result == expected
    
    def test_encode_pdo_value_int8(self):
        """Test encode_pdo_value with INT8."""
        result = encode_pdo_value(-128, PdoType.TYPE_CN_INT8)
        expected = (-128).to_bytes(1, "little", signed=True)
        assert result == expected
    
    def test_encode_pdo_value_int16(self):
        """Test encode_pdo_value with INT16."""
        result = encode_pdo_value(-32768, PdoType.TYPE_CN_INT16)
        expected = (-32768).to_bytes(2, "little", signed=True)
        assert result == expected
    
    def test_encode_pdo_value_int64(self):
        """Test encode_pdo_value with INT64."""
        result = encode_pdo_value(-9223372036854775808, PdoType.TYPE_CN_INT64)
        expected = (-9223372036854775808).to_bytes(8, "little", signed=True)
        assert result == expected
    
    def test_encode_pdo_value_positive_int8(self):
        """Test encode_pdo_value with positive INT8."""
        result = encode_pdo_value(127, PdoType.TYPE_CN_INT8)
        expected = (127).to_bytes(1, "little", signed=True)
        assert result == expected
    
    def test_encode_pdo_value_zero_values(self):
        """Test encode_pdo_value with zero values."""
        test_cases = [
            (PdoType.TYPE_CN_UINT8, 1),
            (PdoType.TYPE_CN_UINT16, 2),
            (PdoType.TYPE_CN_UINT32, 4),
            (PdoType.TYPE_CN_INT8, 1),
            (PdoType.TYPE_CN_INT16, 2),
            (PdoType.TYPE_CN_INT64, 8),
        ]
        
        for pdo_type, expected_length in test_cases:
            result = encode_pdo_value(0, pdo_type)
            assert len(result) == expected_length
            assert all(byte == 0 for byte in result)
    
    def test_encode_pdo_value_unsupported_type(self):
        """Test encode_pdo_value with unsupported PDO type."""
        with pytest.raises(ValueError) as exc_info:
            encode_pdo_value(123, PdoType.TYPE_CN_STRING)
        
        assert "Type is not supported at this time" in str(exc_info.value)
        assert PdoType.TYPE_CN_STRING in exc_info.value.args
    
    def test_encode_pdo_value_little_endian(self):
        """Test encode_pdo_value uses little endian byte order."""
        # Test with a value that will show endianness
        value = 0x1234
        result = encode_pdo_value(value, PdoType.TYPE_CN_UINT16)
        
        # In little endian, 0x1234 should be stored as [0x34, 0x12]
        assert result == b'\x34\x12'
    
    def test_encode_pdo_value_edge_cases(self):
        """Test encode_pdo_value with edge case values."""
        # Test boundary values
        test_cases = [
            (PdoType.TYPE_CN_UINT8, 0, b'\x00'),
            (PdoType.TYPE_CN_UINT8, 255, b'\xff'),
            (PdoType.TYPE_CN_INT8, -128, b'\x80'),
            (PdoType.TYPE_CN_INT8, 127, b'\x7f'),
            (PdoType.TYPE_CN_UINT16, 0, b'\x00\x00'),
            (PdoType.TYPE_CN_UINT16, 65535, b'\xff\xff'),
        ]
        
        for pdo_type, value, expected in test_cases:
            result = encode_pdo_value(value, pdo_type)
            assert result == expected