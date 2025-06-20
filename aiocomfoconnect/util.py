"""Utility functions for aiocomfoconnect.

Provide helper methods for bit manipulation, version decoding,
CAN/PDO conversions, airflow constraint calculations, and PDO value encoding.
All functions are type-annotated and documented according to PEP 257 and Google style.
"""

from __future__ import annotations

from aiocomfoconnect.const import (
    CAN_ID_OFFSET,
    CONSTRAINT_BITS,
    PDO_SHIFT,
    UINT64_BITS,
    PdoType,
)


def bytestring(arr: list[int | bytes]) -> bytes:
    """Join an array of bytes/integers into a bytestring. Unlike `bytes()`, this method supports a mixed array with integers and bytes.

    Args:
        arr (list[int | bytes]): List of integers or bytes.

    Returns:
        bytes: Concatenated bytes object.

    Raises:
        TypeError: If an element is not int or bytes.
    """
    result = bytearray()
    for i in arr:
        if isinstance(i, bytes):
            result.extend(i)
        elif isinstance(i, int):
            result.append(i)
        else:
            raise TypeError("Array elements must be int or bytes")
    return bytes(result)


def bytearray_to_bits(arr: bytes | bytearray) -> list[int]:
    """Convert a bytearray or bytes-like object to a list of set bit indices.

    Args:
        arr (bytes | bytearray): Input bytearray or bytes-like object.

    Returns:
        list[int]: Indices (bit positions) where bits are set to 1.

    Raises:
        TypeError: If input is not bytes or bytearray.

    Example:
        >>> bytearray_to_bits(bytearray([0b00000001, 0b00000010]))
        [0, 9]
    """
    if not isinstance(arr, (bytes, bytearray)):
        raise TypeError("Input must be a bytes or bytearray object")
    bits: list[int] = []
    j = 0
    for byte in arr:
        for i in range(8):
            if byte & (1 << i):
                bits.append(j)
            j += 1
    return bits


def uint_to_bits(value: int) -> list[int]:
    """Convert an unsigned integer to a list of set bit positions.

    Args:
        value (int): Unsigned integer to convert.

    Returns:
        list[int]: Positions of bits set to 1.
    """
    bits: list[int] = []
    for i in range(UINT64_BITS):
        if value & (1 << i):
            bits.append(i)
    return bits


def version_decode(version: int) -> str:
    """Decode the version number to a human-readable string.

    Args:
        version (int): Encoded version number as integer.

    Returns:
        str: Decoded version string in the format '<type><major>.<minor>.<patch>'.
    """
    v_1 = (version >> 30) & 3
    v_2 = (version >> 20) & 1023
    v_3 = (version >> 10) & 1023
    v_4 = version & 1023
    match v_1:
        case 0:
            v_1_str = "U"
        case 1:
            v_1_str = "D"
        case 2:
            v_1_str = "P"
        case 3:
            v_1_str = "R"
        case _:
            v_1_str = str(v_1)
    return f"{v_1_str}{v_2}.{v_3}.{v_4}"


def pdo_to_can(pdo: int, node_id: int = 1) -> str:
    """Convert a PDO-ID to a CAN-ID (hex string).

    Args:
        pdo (int): PDO-ID.
        node_id (int, optional): Node ID. Defaults to 1.

    Returns:
        str: CAN-ID as hex string.
    """
    return ((pdo << PDO_SHIFT) + CAN_ID_OFFSET + node_id).to_bytes(4, byteorder="big").hex()


def can_to_pdo(can: str | bytes | bytearray, node_id: int = 1) -> int:
    """Convert a CAN-ID to a PDO-ID.

    Args:
        can (str | bytes | bytearray): CAN-ID as hex string or bytes.
        node_id (int, optional): Node ID. Defaults to 1.

    Returns:
        int: Computed PDO-ID.

    Raises:
        ValueError: If input cannot be converted to integer.
    """
    if isinstance(can, str):
        can_int = int(can, 16)
    elif isinstance(can, (bytes, bytearray)):
        can_int = int.from_bytes(can, byteorder="big")
    else:
        raise ValueError("CAN-ID must be a hex string, bytes, or bytearray.")
    return (can_int - CAN_ID_OFFSET - node_id) >> PDO_SHIFT


def calculate_airflow_constraints(value: int) -> list[str] | None:
    """Calculate airflow constraints based on the bitmask value.

    Args:
        value (int): Bitmask integer representing airflow constraints.

    Returns:
        list[str] | None: List of constraint names if present, else None.
    """
    bits = uint_to_bits(value)
    if 45 not in bits:
        return None
    constraints: list[str] = []
    for bit, name in CONSTRAINT_BITS.items():
        if bit in bits and name not in constraints:
            constraints.append(name)
    return constraints


def encode_pdo_value(value: int, pdo_type: PdoType) -> bytes:
    """Encode a PDO value to its raw byte representation based on PDO type.

    Args:
        value (int): Integer value to encode.
        pdo_type (PdoType): PDO type determining encoding format.

    Returns:
        bytes: Encoded value as bytes (little-endian).

    Raises:
        ValueError: If PDO type is not supported.
    """
    match pdo_type:
        case PdoType.TYPE_CN_BOOL:
            # Encode as 1 byte: 0x01 for True, 0x00 for False
            return bytes([1 if value else 0])
        case PdoType.TYPE_CN_UINT8 | PdoType.TYPE_CN_UINT16 | PdoType.TYPE_CN_UINT32:
            signed = False
        case PdoType.TYPE_CN_INT8 | PdoType.TYPE_CN_INT16 | PdoType.TYPE_CN_INT64:
            signed = True
        case _:
            raise ValueError(f"Type is not supported at this time: {pdo_type}")
    match pdo_type:
        case PdoType.TYPE_CN_INT8 | PdoType.TYPE_CN_UINT8:
            length = 1
        case PdoType.TYPE_CN_INT16 | PdoType.TYPE_CN_UINT16:
            length = 2
        case PdoType.TYPE_CN_UINT32:
            length = 4
        case PdoType.TYPE_CN_INT64:
            length = 8
        case _:
            raise ValueError(f"Type is not supported at this time: {pdo_type}")
    return value.to_bytes(length, "little", signed=signed)
