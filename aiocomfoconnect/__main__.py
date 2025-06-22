"""aiocomfoconnect CLI application

A command-line interface for interacting with Zehnder ComfoConnect LAN C devices.

Features:
- Discover bridges on the network
- Register and deregister applications
- Set and get fan speed, operation mode, and ComfoCool mode
- Trigger or cancel boost mode
- Show all or individual sensor values
- Get and set property values
- Get and set airflow for specific speeds
- Get and set bypass and away modes
- Advanced controls for balance mode, temperature profile, and error management

Usage:
    python -m aiocomfoconnect --help

Examples:
    python -m aiocomfoconnect discover
    python -m aiocomfoconnect register --pin 1234 --name "My App"
    python -m aiocomfoconnect set-speed high
    python -m aiocomfoconnect get-balance-mode

For a full list of commands and options, use the -h flag with any group or command.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from aiocomfoconnect import DEFAULT_NAME, DEFAULT_PIN, DEFAULT_UUID
from aiocomfoconnect.comfoconnect import ComfoConnect
from aiocomfoconnect.discovery import discover_bridges
from aiocomfoconnect.exceptions import (
    AioComfoConnectNotConnected,
    AioComfoConnectTimeout,
    BridgeNotFoundException,
    ComfoConnectNotAllowed,
)
from aiocomfoconnect.properties import Property
from aiocomfoconnect.sensors import SENSORS

_LOGGER = logging.getLogger(__name__)

# Magic numbers/constants
DEFAULT_NODE_ID: int = 0x01
DEFAULT_PROPERTY_TYPE: int = 0x09


# Command type definitions for factory pattern
class CommandType:
    """Command type definitions for the CLI factory pattern."""

    GET_SIMPLE = "get_simple"
    SET_SIMPLE = "set_simple"
    SET_WITH_TIMEOUT = "set_with_timeout"
    CUSTOM = "custom"


def create_get_command(method_name: str):
    """Factory function to create simple getter commands."""

    async def command_func(args: argparse.Namespace) -> None:
        async def do_get(comfoconnect):
            result = await getattr(comfoconnect, method_name)()
            print(str(result))

        await with_connected_bridge(args.host, args.uuid, do_get)

    return command_func


def create_set_command(method_name: str, param_name: str = "mode"):
    """Factory function to create simple setter commands."""

    async def command_func(args: argparse.Namespace) -> None:
        async def do_set(comfoconnect, param):
            await getattr(comfoconnect, method_name)(param)

        param_value = getattr(args, param_name)
        await with_connected_bridge(args.host, args.uuid, do_set, param_value)

    return command_func


def create_set_command_with_timeout(method_name: str, param_name: str = "mode"):
    """Factory function to create setter commands with timeout support."""

    async def command_func(args: argparse.Namespace) -> None:
        async def do_set(comfoconnect, param, timeout):
            method = getattr(comfoconnect, method_name)
            if timeout is not None:
                await method(param, timeout)
            else:
                await method(param)

        param_value = getattr(args, param_name)
        timeout = getattr(args, "timeout", None)
        await with_connected_bridge(args.host, args.uuid, do_set, param_value, timeout)

    return command_func


async def run_discover(args: argparse.Namespace) -> None:
    """Discover all bridges on the network."""
    bridges = await discover_bridges(args.host)
    print("Discovered bridges:")
    for bridge in bridges:
        print(bridge)
        print()


async def with_connected_bridge(
    host: str | None,
    uuid: str,
    action: callable,
    *action_args,
    sensor_callback=None,
    alarm_callback=None,
    **action_kwargs,
) -> None:
    """Discover, connect, execute an action, and disconnect from a bridge."""
    bridges = await discover_bridges(host)
    if not bridges:
        raise BridgeNotFoundException("No bridge found")
    comfoconnect = ComfoConnect(bridges[0].host, bridges[0].uuid, sensor_callback=sensor_callback, alarm_callback=alarm_callback)
    try:
        await comfoconnect.connect(uuid)
    except ComfoConnectNotAllowed:
        print("Could not connect to bridge. Please register first.")
        sys.exit(1)
    try:
        await action(comfoconnect, *action_args, **action_kwargs)
    finally:
        await comfoconnect.disconnect()


async def run_register(args: argparse.Namespace) -> None:
    """Register an app on the bridge."""
    bridges = await discover_bridges(args.host)
    if not bridges:
        raise BridgeNotFoundException("No bridge found")

    comfoconnect = ComfoConnect(bridges[0].host, bridges[0].uuid)
    try:
        await comfoconnect.connect(args.uuid)
        print(f"UUID {args.uuid} is already registered.")
    except ComfoConnectNotAllowed:
        try:
            await comfoconnect.cmd_register_app(args.uuid, args.name, args.pin)
        except ComfoConnectNotAllowed:
            await comfoconnect.disconnect()
            print("Registration failed. Please check the PIN.")
            sys.exit(1)

        print(f"UUID {args.uuid} is now registered.")
        await comfoconnect.cmd_start_session(True)

    print()
    print("Registered applications:")
    reply = await comfoconnect.cmd_list_registered_apps()
    for app in reply.apps:
        print(f"* {app.uuid.hex()}: {app.devicename}")
    await comfoconnect.disconnect()


async def run_deregister(args: argparse.Namespace) -> None:
    """Deregister an app on the bridge."""

    async def do_deregister(comfoconnect, uuid_old):
        if uuid_old:
            await comfoconnect.cmd_deregister_app(uuid_old)

        print()
        print("Registered applications:")
        reply = await comfoconnect.cmd_list_registered_apps()
        for app in reply.apps:
            print(f"* {app.uuid.hex()}: {app.devicename}")

    await with_connected_bridge(args.host, args.uuid, do_deregister, args.uuid_old)


# Simple setter commands
run_set_speed = create_set_command("set_speed", "speed")
run_set_mode = create_set_command("set_mode")
run_set_comfocool = create_set_command("set_comfocool_mode")


async def run_set_boost(args: argparse.Namespace) -> None:
    """Set boost mode."""

    async def do_set_boost(comfoconnect, mode, timeout):
        await comfoconnect.set_boost(mode == "on", timeout)

    await with_connected_bridge(args.host, args.uuid, do_set_boost, args.mode, args.timeout)


async def run_show_sensors(args: argparse.Namespace) -> None:
    """Show all sensors."""

    def alarm_callback(node_id, errors):
        print(f"Alarm received for Node {node_id}:")
        for error_id, error in errors.items():
            print(f"* {error_id}: {error}")

    def sensor_callback(sensor, value):
        print(f"{sensor.name:>40}: {value} {sensor.unit or ''}")

    async def do_show_sensors(comfoconnect):
        for sensor in SENSORS.values():
            await comfoconnect.register_sensor(sensor)
        try:
            while True:
                await asyncio.sleep(30)
                try:
                    print("Sending keepalive...")
                    await comfoconnect.cmd_time_request()
                except AioComfoConnectNotConnected:
                    print("Got AioComfoConnectNotConnected")
                except AioComfoConnectTimeout:
                    print("Got AioComfoConnectTimeout")
        except KeyboardInterrupt:
            pass
        print("Disconnecting...")

    await with_connected_bridge(args.host, args.uuid, do_show_sensors, sensor_callback=sensor_callback, alarm_callback=alarm_callback)


async def run_show_sensor(args: argparse.Namespace) -> None:
    """Show a sensor."""
    result_event = asyncio.Event()

    def sensor_callback(sensor_, value):
        print(f"{sensor_.name:>40}: {value} {sensor_.unit or ''}")
        result_event.set()

    async def do_show_sensor(comfoconnect):
        if args.sensor not in SENSORS:
            print(f"Unknown sensor with ID {args.sensor}")
            sys.exit(1)

        await comfoconnect.register_sensor(SENSORS[args.sensor])
        await asyncio.wait_for(result_event.wait(), timeout=10)

        if args.follow:
            try:
                while True:
                    await asyncio.sleep(30)
                    try:
                        print("Sending keepalive...")
                        await comfoconnect.cmd_time_request()
                    except AioComfoConnectNotConnected:
                        print("Got AioComfoConnectNotConnected")
                    except AioComfoConnectTimeout:
                        print("Got AioComfoConnectTimeout")
            except KeyboardInterrupt:
                pass

    await with_connected_bridge(args.host, args.uuid, do_show_sensor, sensor_callback=sensor_callback)


async def run_get_property(args: argparse.Namespace) -> None:
    """Get a property."""

    async def do_get_property(comfoconnect, node_id, unit, subunit, property_id, property_type):
        print(await comfoconnect.get_property(Property(unit, subunit, property_id, property_type), node_id))

    await with_connected_bridge(args.host, args.uuid, do_get_property, args.node_id, args.unit, args.subunit, args.property_id, args.property_type)


async def run_get_flow_for_speed(args: argparse.Namespace) -> None:
    """Get the configured airflow for the specified speed."""

    async def do_get_flow_for_speed(comfoconnect, speed):
        print(await comfoconnect.get_flow_for_speed(speed))

    await with_connected_bridge(args.host, args.uuid, do_get_flow_for_speed, args.speed)


async def run_set_flow_for_speed(args: argparse.Namespace) -> None:
    """Set the configured airflow for the specified speed."""

    async def do_set_flow(comfoconnect, speed, desired_flow):
        await comfoconnect.set_flow_for_speed(speed, desired_flow)

    await with_connected_bridge(args.host, args.uuid, do_set_flow, args.speed, args.flow)


async def run_list_sensors(args: argparse.Namespace) -> None:
    """List all known sensors."""
    print(f"{'ID':>6} | {'Name':<40} | {'Unit':<8}")
    print("-" * 60)
    for sensor_id, sensor in sorted(SENSORS.items()):
        print(f"{sensor_id:6} | {sensor.name:<40} | {sensor.unit or '-':<8}")


# Factory-created commands using generic patterns
run_get_temperature_profile = create_get_command("get_temperature_profile")
run_set_temperature_profile = create_set_command("set_temperature_profile", "profile")
run_get_speed = create_get_command("get_speed")
run_get_comfocool = create_get_command("get_comfocool_mode")
run_get_bypass = create_get_command("get_bypass")
run_set_bypass = create_set_command("set_bypass")
run_get_sensor_ventmode_temperature_passive = create_get_command("get_sensor_ventmode_temperature_passive")
run_set_sensor_ventmode_temperature_passive = create_set_command("set_sensor_ventmode_temperature_passive")
run_get_sensor_ventmode_humidity_comfort = create_get_command("get_sensor_ventmode_humidity_comfort")
run_set_sensor_ventmode_humidity_comfort = create_set_command("set_sensor_ventmode_humidity_comfort")
run_get_sensor_ventmode_humidity_protection = create_get_command("get_sensor_ventmode_humidity_protection")
run_set_sensor_ventmode_humidity_protection = create_set_command("set_sensor_ventmode_humidity_protection")
run_get_balance_mode = create_get_command("get_balance_mode")
run_set_balance_mode = create_set_command("set_balance_mode")
run_get_mode = create_get_command("get_mode")

# Command configuration for automated parser creation
COMMAND_CONFIG = {
    "discover": {"help": "discover ComfoConnect LAN C devices on your network", "func": run_discover, "args": [{"name": "--host", "help": "Host address of the bridge"}]},
    "register": {
        "help": "register on a ComfoConnect LAN C device",
        "func": run_register,
        "args": [
            {"name": "--pin", "help": "PIN code to register on the bridge", "default": DEFAULT_PIN},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
            {"name": "--name", "help": "Name of this app", "default": DEFAULT_NAME},
        ],
    },
    "deregister": {
        "help": "deregister on a ComfoConnect LAN C device",
        "func": run_deregister,
        "args": [
            {"name": "uuid_old", "help": "UUID of the app to deregister", "default": None},
            {"name": "--pin", "help": "PIN code to register on the bridge", "default": DEFAULT_PIN},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-speed": {
        "help": "Get the current fan speed",
        "func": run_get_speed,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-speed": {
        "help": "set the fan speed",
        "func": run_set_speed,
        "args": [
            {"name": "speed", "help": "Fan speed", "choices": ["low", "medium", "high", "away"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-mode": {
        "help": "Get the current ventilation mode",
        "func": run_get_mode,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-mode": {
        "help": "set operation mode",
        "func": run_set_mode,
        "args": [
            {"name": "mode", "help": "Operation mode", "choices": ["auto", "manual"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "set-boost": {
        "help": "set boost mode",
        "func": run_set_boost,
        "args": [
            {"name": "mode", "help": "Boost mode", "choices": ["on", "off"]},
            {"name": "--timeout", "help": "Timeout in seconds", "type": int, "default": None},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "show-sensors": {
        "help": "show all sensor values",
        "func": run_show_sensors,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "show-sensor": {
        "help": "show a specific sensor value",
        "func": run_show_sensor,
        "args": [
            {"name": "sensor", "help": "Sensor ID", "type": int},
            {"name": "--follow", "help": "Keep showing sensor values", "action": "store_true"},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "list-sensors": {"help": "list all known sensors", "func": run_list_sensors, "args": []},
    "get-property": {
        "help": "get a property value",
        "func": run_get_property,
        "args": [
            {"name": "unit", "help": "Unit ID", "type": int},
            {"name": "subunit", "help": "Subunit ID", "type": int},
            {"name": "property_id", "help": "Property ID", "type": int},
            {"name": "--node-id", "help": "Node ID", "type": int, "default": DEFAULT_NODE_ID},
            {"name": "--property-type", "help": "Property type", "type": int, "default": DEFAULT_PROPERTY_TYPE},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-flow-for-speed": {
        "help": "get configured airflow for a speed",
        "func": run_get_flow_for_speed,
        "args": [
            {"name": "speed", "help": "Fan speed", "choices": ["low", "medium", "high"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "set-flow-for-speed": {
        "help": "set configured airflow for a speed",
        "func": run_set_flow_for_speed,
        "args": [
            {"name": "speed", "help": "Fan speed", "choices": ["low", "medium", "high"]},
            {"name": "flow", "help": "Airflow value", "type": int},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-temperature-profile": {
        "help": "get the current temperature profile",
        "func": run_get_temperature_profile,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-temperature-profile": {
        "help": "set the temperature profile",
        "func": run_set_temperature_profile,
        "args": [
            {"name": "profile", "help": "Temperature profile", "choices": ["normal", "cool", "warm"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-comfocool": {
        "help": "get the current ComfoCool mode",
        "func": run_get_comfocool,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-comfocool": {
        "help": "set ComfoCool mode",
        "func": run_set_comfocool,
        "args": [
            {"name": "mode", "help": "ComfoCool mode", "choices": ["auto", "on", "off"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-bypass": {
        "help": "get the current bypass mode",
        "func": run_get_bypass,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-bypass": {
        "help": "set bypass mode",
        "func": run_set_bypass,
        "args": [
            {"name": "mode", "help": "Bypass mode", "choices": ["auto", "on", "off"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-balance-mode": {
        "help": "get the current balance mode",
        "func": run_get_balance_mode,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-balance-mode": {
        "help": "set balance mode",
        "func": run_set_balance_mode,
        "args": [
            {"name": "mode", "help": "Balance mode", "choices": ["balance", "supply_only", "extract_only"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-sensor-ventmode-temperature-passive": {
        "help": "get sensor ventmode temperature passive setting",
        "func": run_get_sensor_ventmode_temperature_passive,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-sensor-ventmode-temperature-passive": {
        "help": "set sensor ventmode temperature passive setting",
        "func": run_set_sensor_ventmode_temperature_passive,
        "args": [
            {"name": "mode", "help": "Temperature passive mode", "choices": ["auto", "on", "off"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-sensor-ventmode-humidity-comfort": {
        "help": "get sensor ventmode humidity comfort setting",
        "func": run_get_sensor_ventmode_humidity_comfort,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-sensor-ventmode-humidity-comfort": {
        "help": "set sensor ventmode humidity comfort setting",
        "func": run_set_sensor_ventmode_humidity_comfort,
        "args": [
            {"name": "mode", "help": "Humidity comfort mode", "choices": ["auto", "on", "off"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
    "get-sensor-ventmode-humidity-protection": {
        "help": "get sensor ventmode humidity protection setting",
        "func": run_get_sensor_ventmode_humidity_protection,
        "args": [{"name": "--host", "help": "Host address of the bridge"}, {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID}],
    },
    "set-sensor-ventmode-humidity-protection": {
        "help": "set sensor ventmode humidity protection setting",
        "func": run_set_sensor_ventmode_humidity_protection,
        "args": [
            {"name": "mode", "help": "Humidity protection mode", "choices": ["auto", "on", "off"]},
            {"name": "--host", "help": "Host address of the bridge"},
            {"name": "--uuid", "help": "UUID of this app", "default": DEFAULT_UUID},
        ],
    },
}


def setup_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    argument_parser = argparse.ArgumentParser(description="aiocomfoconnect CLI for ComfoConnect LAN C devices")
    argument_parser.add_argument("--debug", "-d", help="Enable debug logging", default=False, action="store_true")
    subparsers = argument_parser.add_subparsers(required=True, dest="action")

    # Create subparsers from configuration
    for cmd_name, cmd_config in COMMAND_CONFIG.items():
        subparser = subparsers.add_parser(cmd_name, help=cmd_config["help"])
        subparser.set_defaults(func=cmd_config["func"])

        for arg_config in cmd_config["args"]:
            # Create a copy to avoid modifying the original config
            arg_dict = arg_config.copy()
            arg_name = arg_dict.pop("name")
            subparser.add_argument(arg_name, **arg_dict)

    return argument_parser


async def main(args: argparse.Namespace) -> None:
    """Main entry point for the CLI."""
    await args.func(args)


if __name__ == "__main__":
    try:
        parser = setup_argument_parser()
        arguments = parser.parse_args()
        if arguments.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.WARNING)
        asyncio.run(main(arguments))
    except KeyboardInterrupt:
        pass
