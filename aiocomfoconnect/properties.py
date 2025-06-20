"""Property definitions for aiocomfoconnect.

Defines property IDs and Property dataclass for use with ComfoConnect units.

Attributes:
    PROP_ID_NODE_SERIAL_NUMBER (int): Property ID for node serial number.
    PROP_ID_NODE_FW_VERSION (int): Property ID for node firmware version.
    PROP_ID_NODE_MODEL (int): Property ID for node model.
    PROP_ID_NODE_ARTICLE (int): Property ID for node article.
    PROP_ID_NODE_COUNTRY (int): Property ID for node country.
    PROP_ID_NODE_NAME (int): Property ID for node name.
    PROP_ID_NODE_CFG_MAINTAINER_PASSWORD (int): Property ID for maintainer password.
    PROP_ID_VENT_TEMP_PASSIVE (int): Property ID for passive temperature sensor.
    PROP_ID_VENT_HUMI_COMFORT (int): Property ID for comfort humidity sensor.
    PROP_ID_VENT_HUMI_PROTECT (int): Property ID for protection humidity sensor.
"""

from __future__ import annotations

from dataclasses import dataclass

from .const import (
    SUBUNIT_01,
    UNIT_NODE,
    UNIT_NODECONFIGURATION,
    UNIT_TEMPHUMCONTROL,
    PdoType,
)


@dataclass(frozen=True)
class Property:
    """Dataclass representing a property for a ComfoConnect unit.

    Attributes:
        unit (int): The unit type identifier.
        subunit (int): The subunit identifier.
        property_id (int): The property ID.
        property_type (int): The PDO type for the property.
    """

    unit: int
    subunit: int
    property_id: int
    property_type: int


# Property IDs for the node
PROP_ID_NODE_SERIAL_NUMBER: int = 0x04  # Serial number property ID
PROP_ID_NODE_FW_VERSION: int = 0x06  # Firmware version property ID
PROP_ID_NODE_MODEL: int = 0x08  # Model property ID
PROP_ID_NODE_ARTICLE: int = 0x0B  # Article property ID
PROP_ID_NODE_COUNTRY: int = 0x0D  # Country property ID
PROP_ID_NODE_NAME: int = 0x14  # Name property ID

# Property IDs for the node configuration
PROP_ID_NODE_CFG_MAINTAINER_PASSWORD: int = 0x03  # Maintainer password property ID

# Property IDs for the ventilation sensor
PROP_ID_VENT_TEMP_PASSIVE: int = 0x04  # Passive temperature sensor property ID
PROP_ID_VENT_HUMI_COMFORT: int = 0x06  # Comfort humidity sensor property ID
PROP_ID_VENT_HUMI_PROTECT: int = 0x07  # Protection humidity sensor property ID

PROPERTY_SERIAL_NUMBER: Property = Property(UNIT_NODE, SUBUNIT_01, PROP_ID_NODE_SERIAL_NUMBER, PdoType.TYPE_CN_STRING)
PROPERTY_FIRMWARE_VERSION: Property = Property(UNIT_NODE, SUBUNIT_01, PROP_ID_NODE_FW_VERSION, PdoType.TYPE_CN_UINT32)
PROPERTY_MODEL: Property = Property(UNIT_NODE, SUBUNIT_01, PROP_ID_NODE_MODEL, PdoType.TYPE_CN_STRING)
PROPERTY_ARTICLE: Property = Property(UNIT_NODE, SUBUNIT_01, PROP_ID_NODE_ARTICLE, PdoType.TYPE_CN_STRING)
PROPERTY_COUNTRY: Property = Property(UNIT_NODE, SUBUNIT_01, PROP_ID_NODE_COUNTRY, PdoType.TYPE_CN_STRING)
PROPERTY_NAME: Property = Property(UNIT_NODE, SUBUNIT_01, PROP_ID_NODE_NAME, PdoType.TYPE_CN_STRING)

PROPERTY_MAINTAINER_PASSWORD: Property = Property(UNIT_NODECONFIGURATION, SUBUNIT_01, PROP_ID_NODE_CFG_MAINTAINER_PASSWORD, PdoType.TYPE_CN_STRING)

PROPERTY_SENSOR_VENTILATION_TEMP_PASSIVE: Property = Property(UNIT_TEMPHUMCONTROL, SUBUNIT_01, PROP_ID_VENT_TEMP_PASSIVE, PdoType.TYPE_CN_UINT32)
PROPERTY_SENSOR_VENTILATION_HUMIDITY_COMFORT: Property = Property(UNIT_TEMPHUMCONTROL, SUBUNIT_01, PROP_ID_VENT_HUMI_COMFORT, PdoType.TYPE_CN_UINT32)
PROPERTY_SENSOR_VENTILATION_HUMIDITY_PROTECTION: Property = Property(UNIT_TEMPHUMCONTROL, SUBUNIT_01, PROP_ID_VENT_HUMI_PROTECT, PdoType.TYPE_CN_UINT32)
