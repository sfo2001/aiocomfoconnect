"""Unit tests for properties module."""

import pytest
from aiocomfoconnect.properties import (
    Property,
    PROP_ID_NODE_SERIAL_NUMBER,
    PROP_ID_NODE_FW_VERSION,
    PROP_ID_NODE_MODEL,
    PROP_ID_NODE_ARTICLE,
    PROP_ID_NODE_COUNTRY,
    PROP_ID_NODE_NAME,
    PROP_ID_NODE_CFG_MAINTAINER_PASSWORD,
    PROP_ID_VENT_TEMP_PASSIVE,
    PROP_ID_VENT_HUMI_COMFORT,
    PROP_ID_VENT_HUMI_PROTECT,
    PROPERTY_SERIAL_NUMBER,
    PROPERTY_FIRMWARE_VERSION,
    PROPERTY_MODEL,
    PROPERTY_ARTICLE,
    PROPERTY_COUNTRY,
    PROPERTY_NAME,
    PROPERTY_MAINTAINER_PASSWORD,
    PROPERTY_SENSOR_VENTILATION_TEMP_PASSIVE,
    PROPERTY_SENSOR_VENTILATION_HUMIDITY_COMFORT,
    PROPERTY_SENSOR_VENTILATION_HUMIDITY_PROTECTION,
)
from aiocomfoconnect.const import (
    UNIT_NODE,
    UNIT_NODECONFIGURATION,
    UNIT_TEMPHUMCONTROL,
    PdoType,
    SUBUNIT_01,
)


class TestProperty:
    """Test Property dataclass."""
    
    def test_property_init(self):
        """Test Property initialization."""
        prop = Property(
            unit=UNIT_NODE,
            subunit=SUBUNIT_01,
            property_id=0x04,
            property_type=PdoType.TYPE_CN_STRING
        )
        
        assert prop.unit == UNIT_NODE
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == 0x04
        assert prop.property_type == PdoType.TYPE_CN_STRING
    
    def test_property_immutable(self):
        """Test that Property is immutable (frozen dataclass)."""
        prop = Property(
            unit=UNIT_NODE,
            subunit=SUBUNIT_01,
            property_id=0x04,
            property_type=PdoType.TYPE_CN_STRING
        )
        
        # Should not be able to modify attributes
        with pytest.raises(AttributeError):
            prop.unit = UNIT_NODECONFIGURATION
        
        with pytest.raises(AttributeError):
            prop.subunit = 2
        
        with pytest.raises(AttributeError):
            prop.property_id = 0x05
        
        with pytest.raises(AttributeError):
            prop.property_type = PdoType.TYPE_CN_UINT32
    
    def test_property_equality(self):
        """Test Property equality comparison."""
        prop1 = Property(UNIT_NODE, SUBUNIT_01, 0x04, PdoType.TYPE_CN_STRING)
        prop2 = Property(UNIT_NODE, SUBUNIT_01, 0x04, PdoType.TYPE_CN_STRING)
        prop3 = Property(UNIT_NODE, SUBUNIT_01, 0x05, PdoType.TYPE_CN_STRING)
        
        assert prop1 == prop2
        assert prop1 != prop3
    
    def test_property_repr(self):
        """Test Property string representation."""
        prop = Property(
            unit=UNIT_NODE,
            subunit=SUBUNIT_01,
            property_id=0x04,
            property_type=PdoType.TYPE_CN_STRING
        )
        
        repr_str = repr(prop)
        assert "Property" in repr_str
        assert str(UNIT_NODE) in repr_str
        assert str(SUBUNIT_01) in repr_str
        assert "0x4" in repr_str or "4" in repr_str


class TestPropertyIdConstants:
    """Test property ID constants."""
    
    def test_node_property_ids(self):
        """Test node property ID constants."""
        assert PROP_ID_NODE_SERIAL_NUMBER == 0x04
        assert PROP_ID_NODE_FW_VERSION == 0x06
        assert PROP_ID_NODE_MODEL == 0x08
        assert PROP_ID_NODE_ARTICLE == 0x0B
        assert PROP_ID_NODE_COUNTRY == 0x0D
        assert PROP_ID_NODE_NAME == 0x14
    
    def test_node_config_property_ids(self):
        """Test node configuration property ID constants."""
        assert PROP_ID_NODE_CFG_MAINTAINER_PASSWORD == 0x03
    
    def test_ventilation_property_ids(self):
        """Test ventilation property ID constants."""
        assert PROP_ID_VENT_TEMP_PASSIVE == 0x04
        assert PROP_ID_VENT_HUMI_COMFORT == 0x06
        assert PROP_ID_VENT_HUMI_PROTECT == 0x07
    
    def test_property_ids_are_integers(self):
        """Test all property ID constants are integers."""
        property_ids = [
            PROP_ID_NODE_SERIAL_NUMBER,
            PROP_ID_NODE_FW_VERSION,
            PROP_ID_NODE_MODEL,
            PROP_ID_NODE_ARTICLE,
            PROP_ID_NODE_COUNTRY,
            PROP_ID_NODE_NAME,
            PROP_ID_NODE_CFG_MAINTAINER_PASSWORD,
            PROP_ID_VENT_TEMP_PASSIVE,
            PROP_ID_VENT_HUMI_COMFORT,
            PROP_ID_VENT_HUMI_PROTECT,
        ]
        
        for prop_id in property_ids:
            assert isinstance(prop_id, int)


class TestPropertyConstants:
    """Test predefined Property constants."""
    
    def test_property_constants_are_property_objects(self):
        """Test all property constants are Property objects."""
        properties = [
            PROPERTY_SERIAL_NUMBER,
            PROPERTY_FIRMWARE_VERSION,
            PROPERTY_MODEL,
            PROPERTY_ARTICLE,
            PROPERTY_COUNTRY,
            PROPERTY_NAME,
            PROPERTY_MAINTAINER_PASSWORD,
            PROPERTY_SENSOR_VENTILATION_TEMP_PASSIVE,
            PROPERTY_SENSOR_VENTILATION_HUMIDITY_COMFORT,
            PROPERTY_SENSOR_VENTILATION_HUMIDITY_PROTECTION,
        ]
        
        for prop in properties:
            assert isinstance(prop, Property)
    
    def test_serial_number_property(self):
        """Test serial number property configuration."""
        prop = PROPERTY_SERIAL_NUMBER
        
        assert prop.unit == UNIT_NODE
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_NODE_SERIAL_NUMBER
        assert prop.property_type == PdoType.TYPE_CN_STRING
    
    def test_firmware_version_property(self):
        """Test firmware version property configuration."""
        prop = PROPERTY_FIRMWARE_VERSION
        
        assert prop.unit == UNIT_NODE
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_NODE_FW_VERSION
        assert prop.property_type == PdoType.TYPE_CN_UINT32
    
    def test_model_property(self):
        """Test model property configuration."""
        prop = PROPERTY_MODEL
        
        assert prop.unit == UNIT_NODE
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_NODE_MODEL
        assert prop.property_type == PdoType.TYPE_CN_STRING
    
    def test_article_property(self):
        """Test article property configuration."""
        prop = PROPERTY_ARTICLE
        
        assert prop.unit == UNIT_NODE
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_NODE_ARTICLE
        assert prop.property_type == PdoType.TYPE_CN_STRING
    
    def test_country_property(self):
        """Test country property configuration."""
        prop = PROPERTY_COUNTRY
        
        assert prop.unit == UNIT_NODE
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_NODE_COUNTRY
        assert prop.property_type == PdoType.TYPE_CN_STRING
    
    def test_name_property(self):
        """Test name property configuration."""
        prop = PROPERTY_NAME
        
        assert prop.unit == UNIT_NODE
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_NODE_NAME
        assert prop.property_type == PdoType.TYPE_CN_STRING
    
    def test_maintainer_password_property(self):
        """Test maintainer password property configuration."""
        prop = PROPERTY_MAINTAINER_PASSWORD
        
        assert prop.unit == UNIT_NODECONFIGURATION
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_NODE_CFG_MAINTAINER_PASSWORD
        assert prop.property_type == PdoType.TYPE_CN_STRING
    
    def test_temp_passive_property(self):
        """Test temperature passive property configuration."""
        prop = PROPERTY_SENSOR_VENTILATION_TEMP_PASSIVE
        
        assert prop.unit == UNIT_TEMPHUMCONTROL
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_VENT_TEMP_PASSIVE
        assert prop.property_type == PdoType.TYPE_CN_UINT32
    
    def test_humidity_comfort_property(self):
        """Test humidity comfort property configuration."""
        prop = PROPERTY_SENSOR_VENTILATION_HUMIDITY_COMFORT
        
        assert prop.unit == UNIT_TEMPHUMCONTROL
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_VENT_HUMI_COMFORT
        assert prop.property_type == PdoType.TYPE_CN_UINT32
    
    def test_humidity_protection_property(self):
        """Test humidity protection property configuration."""
        prop = PROPERTY_SENSOR_VENTILATION_HUMIDITY_PROTECTION
        
        assert prop.unit == UNIT_TEMPHUMCONTROL
        assert prop.subunit == SUBUNIT_01
        assert prop.property_id == PROP_ID_VENT_HUMI_PROTECT
        assert prop.property_type == PdoType.TYPE_CN_UINT32


class TestPropertyUnits:
    """Test property unit assignments."""
    
    def test_node_properties_use_node_unit(self):
        """Test node properties use UNIT_NODE."""
        node_properties = [
            PROPERTY_SERIAL_NUMBER,
            PROPERTY_FIRMWARE_VERSION,
            PROPERTY_MODEL,
            PROPERTY_ARTICLE,
            PROPERTY_COUNTRY,
            PROPERTY_NAME,
        ]
        
        for prop in node_properties:
            assert prop.unit == UNIT_NODE
    
    def test_node_config_properties_use_node_config_unit(self):
        """Test node configuration properties use UNIT_NODECONFIGURATION."""
        node_config_properties = [
            PROPERTY_MAINTAINER_PASSWORD,
        ]
        
        for prop in node_config_properties:
            assert prop.unit == UNIT_NODECONFIGURATION
    
    def test_ventilation_properties_use_temphumcontrol_unit(self):
        """Test ventilation properties use UNIT_TEMPHUMCONTROL."""
        ventilation_properties = [
            PROPERTY_SENSOR_VENTILATION_TEMP_PASSIVE,
            PROPERTY_SENSOR_VENTILATION_HUMIDITY_COMFORT,
            PROPERTY_SENSOR_VENTILATION_HUMIDITY_PROTECTION,
        ]
        
        for prop in ventilation_properties:
            assert prop.unit == UNIT_TEMPHUMCONTROL
    
    def test_all_properties_use_subunit_01(self):
        """Test all properties use SUBUNIT_01."""
        all_properties = [
            PROPERTY_SERIAL_NUMBER,
            PROPERTY_FIRMWARE_VERSION,
            PROPERTY_MODEL,
            PROPERTY_ARTICLE,
            PROPERTY_COUNTRY,
            PROPERTY_NAME,
            PROPERTY_MAINTAINER_PASSWORD,
            PROPERTY_SENSOR_VENTILATION_TEMP_PASSIVE,
            PROPERTY_SENSOR_VENTILATION_HUMIDITY_COMFORT,
            PROPERTY_SENSOR_VENTILATION_HUMIDITY_PROTECTION,
        ]
        
        for prop in all_properties:
            assert prop.subunit == SUBUNIT_01


class TestPropertyTypes:
    """Test property PDO types."""
    
    def test_string_properties(self):
        """Test properties that use string type."""
        string_properties = [
            PROPERTY_SERIAL_NUMBER,
            PROPERTY_MODEL,
            PROPERTY_ARTICLE,
            PROPERTY_COUNTRY,
            PROPERTY_NAME,
            PROPERTY_MAINTAINER_PASSWORD,
        ]
        
        for prop in string_properties:
            assert prop.property_type == PdoType.TYPE_CN_STRING
    
    def test_uint32_properties(self):
        """Test properties that use UINT32 type."""
        uint32_properties = [
            PROPERTY_FIRMWARE_VERSION,
            PROPERTY_SENSOR_VENTILATION_TEMP_PASSIVE,
            PROPERTY_SENSOR_VENTILATION_HUMIDITY_COMFORT,
            PROPERTY_SENSOR_VENTILATION_HUMIDITY_PROTECTION,
        ]
        
        for prop in uint32_properties:
            assert prop.property_type == PdoType.TYPE_CN_UINT32


class TestPropertyIdMatching:
    """Test property IDs match between constants and Property objects."""
    
    def test_property_ids_match_constants(self):
        """Test property IDs in Property objects match the constant values."""
        property_mappings = [
            (PROPERTY_SERIAL_NUMBER, PROP_ID_NODE_SERIAL_NUMBER),
            (PROPERTY_FIRMWARE_VERSION, PROP_ID_NODE_FW_VERSION),
            (PROPERTY_MODEL, PROP_ID_NODE_MODEL),
            (PROPERTY_ARTICLE, PROP_ID_NODE_ARTICLE),
            (PROPERTY_COUNTRY, PROP_ID_NODE_COUNTRY),
            (PROPERTY_NAME, PROP_ID_NODE_NAME),
            (PROPERTY_MAINTAINER_PASSWORD, PROP_ID_NODE_CFG_MAINTAINER_PASSWORD),
            (PROPERTY_SENSOR_VENTILATION_TEMP_PASSIVE, PROP_ID_VENT_TEMP_PASSIVE),
            (PROPERTY_SENSOR_VENTILATION_HUMIDITY_COMFORT, PROP_ID_VENT_HUMI_COMFORT),
            (PROPERTY_SENSOR_VENTILATION_HUMIDITY_PROTECTION, PROP_ID_VENT_HUMI_PROTECT),
        ]
        
        for prop, expected_id in property_mappings:
            assert prop.property_id == expected_id