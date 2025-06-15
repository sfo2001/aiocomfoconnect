""" aiocomfoconnect CLI application

This module provides a command-line interface for interacting with ComfoConnect LAN C devices.
It supports discovering bridges, registering/deregistering apps, setting fan speed and mode,
showing sensor values, and more.

Usage:
    python -m aiocomfoconnect --help

Example:
    python -m aiocomfoconnect discover
    python -m aiocomfoconnect register --pin 1234 --name "My App"
    python -m aiocomfoconnect set-speed high

Available actions:
    discover, register, deregister, set-speed, set-mode, set-comfocool, set-boost,
    show-sensors, show-sensor, get-property, get-flow-for-speed, set-flow-for-speed
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
    UnknownActionException,
)
from aiocomfoconnect.properties import Property
from aiocomfoconnect.sensors import SENSORS

_LOGGER = logging.getLogger(__name__)

# Magic numbers/constants
DEFAULT_NODE_ID: int = 0x01
DEFAULT_PROPERTY_TYPE: int = 0x09

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
    comfoconnect = ComfoConnect(
        bridges[0].host, bridges[0].uuid,
        sensor_callback=sensor_callback,
        alarm_callback=alarm_callback
    )
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


async def run_set_speed(args: argparse.Namespace) -> None:
    """Set ventilation speed."""
    async def do_set_speed(comfoconnect, speed):
        await comfoconnect.set_speed(speed)
    await with_connected_bridge(args.host, args.uuid, do_set_speed, args.speed)

async def run_set_mode(args: argparse.Namespace) -> None:
    """Set ventilation mode."""
    async def do_set_mode(comfoconnect, mode):
        await comfoconnect.set_mode(mode)
    await with_connected_bridge(args.host, args.uuid, do_set_mode, args.mode)

async def run_set_comfocool(args: argparse.Namespace) -> None:
    """Set comfocool mode."""
    async def do_set_comfocool(comfoconnect, mode):
        await comfoconnect.set_comfocool_mode(mode)
    await with_connected_bridge(args.host, args.uuid, do_set_comfocool, args.mode)

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
    await with_connected_bridge(
        args.host, args.uuid, do_show_sensors,
        sensor_callback=sensor_callback,
        alarm_callback=alarm_callback
    )

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

    await with_connected_bridge(
        args.host, args.uuid, do_show_sensor,
        sensor_callback=sensor_callback
    )

async def run_get_property(args: argparse.Namespace) -> None:
    """Get a property."""
    async def do_get_property(comfoconnect, node_id, unit, subunit, property_id, property_type):
        print(
            await comfoconnect.get_property(Property(unit, subunit, property_id, property_type), node_id)
        )
    await with_connected_bridge(
        args.host, args.uuid, do_get_property, args.node_id, args.unit, args.subunit, args.property_id, args.property_type
    )

async def run_get_flow_for_speed(args: argparse.Namespace) -> None:
    """Get the configured airflow for the specified speed."""
    async def do_get_flow(comfoconnect, speed):
        print(await comfoconnect.get_flow_for_speed(speed))
    await with_connected_bridge(args.host, args.uuid, do_get_flow, args.speed)

async def run_set_flow_for_speed(args: argparse.Namespace) -> None:
    """Set the configured airflow for the specified speed."""
    async def do_set_flow_for_speed(comfoconnect, speed, flow):
        await comfoconnect.set_flow_for_speed(speed, flow)

    await with_connected_bridge(args.host, args.uuid, do_set_flow_for_speed, args.speed, args.flow)

async def main(args: argparse.Namespace) -> None:
    """Main entry point for the CLI."""
    await args.func(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", help="Enable debug logging", default=False, action="store_true")
    subparsers = parser.add_subparsers(required=True, dest="action")
    p_discover = subparsers.add_parser("discover", help="discover ComfoConnect LAN C devices on your network")
    p_discover.add_argument("--host", help="Host address of the bridge")
    p_discover.set_defaults(func=run_discover)

    p_register = subparsers.add_parser("register", help="register on a ComfoConnect LAN C device")
    p_register.add_argument("--pin", help="PIN code to register on the bridge", default=DEFAULT_PIN)
    p_register.add_argument("--host", help="Host address of the bridge")
    p_register.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_register.add_argument("--name", help="Name of this app", default=DEFAULT_NAME)
    p_register.set_defaults(func=run_register)

    p_deregister = subparsers.add_parser("deregister", help="deregister on a ComfoConnect LAN C device")
    p_deregister.add_argument("uuid_old", help="UUID of the app to deregister", default=None)
    p_deregister.add_argument("--pin", help="PIN code to register on the bridge", default=DEFAULT_PIN)
    p_deregister.add_argument("--host", help="Host address of the bridge")
    p_deregister.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_deregister.set_defaults(func=run_deregister)

    p_set_speed = subparsers.add_parser("set-speed", help="set the fan speed")
    p_set_speed.add_argument("speed", help="Fan speed", choices=["low", "medium", "high", "away"])
    p_set_speed.add_argument("--host", help="Host address of the bridge")
    p_set_speed.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_set_speed.set_defaults(func=run_set_speed)

    p_set_mode = subparsers.add_parser("set-mode", help="set operation mode")
    p_set_mode.add_argument("mode", help="Operation mode", choices=["auto", "manual"])
    p_set_mode.add_argument("--host", help="Host address of the bridge")
    p_set_mode.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_set_mode.set_defaults(func=run_set_mode)

    p_set_comfocool = subparsers.add_parser("set-comfocool", help="set comfocool mode")
    p_set_comfocool.add_argument("mode", help="Comfocool mode", choices=["auto", "off"])
    p_set_comfocool.add_argument("--host", help="Host address of the bridge")
    p_set_comfocool.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_set_comfocool.set_defaults(func=run_set_comfocool)

    p_set_boost = subparsers.add_parser("set-boost", help="trigger or cancel a boost")
    p_set_boost.add_argument("mode", help="Boost mode", choices=["on", "off"])
    p_set_boost.add_argument("--host", help="Host address of the bridge")
    p_set_boost.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_set_boost.add_argument("--timeout", "-t", help="Timeout in seconds", type=int, default=600)
    p_set_boost.set_defaults(func=run_set_boost)

    p_sensors = subparsers.add_parser("show-sensors", help="show the sensor values")
    p_sensors.add_argument("--host", help="Host address of the bridge")
    p_sensors.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_sensors.set_defaults(func=run_show_sensors)

    p_sensor = subparsers.add_parser("show-sensor", help="show a single sensor value")
    p_sensor.add_argument("sensor", help="The ID of the sensor", type=int)
    p_sensor.add_argument("--host", help="Host address of the bridge")
    p_sensor.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_sensor.add_argument("--follow", "-f", help="Follow", default=False, action="store_true")
    p_sensor.set_defaults(func=run_show_sensor)

    p_property = subparsers.add_parser("get-property", help="show a property value")
    p_property.add_argument("unit", help="The Unit of the property", type=int)
    p_property.add_argument("subunit", help="The Subunit of the property", type=int)
    p_property.add_argument("property_id", help="The id of the property", type=int)
    p_property.add_argument("property_type", help="The type of the property", type=int, default=0x09)
    p_property.add_argument("--node_id", help="The Node ID of the query", type=int, default=0x01)
    p_property.add_argument("--host", help="Host address of the bridge")
    p_property.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_property.set_defaults(func=run_get_property)

    p_get_flow_speed = subparsers.add_parser("get-flow-for-speed", help="Get m³/h for given speed")
    p_get_flow_speed.add_argument("speed", help="Fan speed", choices=["low", "medium", "high", "away"])
    p_get_flow_speed.add_argument("--host", help="Host address of the bridge")
    p_get_flow_speed.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_get_flow_speed.set_defaults(func=run_get_flow_for_speed)

    p_set_flow_speed = subparsers.add_parser("set-flow-for-speed", help="Set m³/h for given speed")
    p_set_flow_speed.add_argument("speed", help="Fan speed", choices=["low", "medium", "high", "away"])
    p_set_flow_speed.add_argument("flow", help="Desired airflow in m³/h", type=int)
    p_set_flow_speed.add_argument("--host", help="Host address of the bridge")
    p_set_flow_speed.add_argument("--uuid", help="UUID of this app", default=DEFAULT_UUID)
    p_set_flow_speed.set_defaults(func=run_set_flow_for_speed)

    arguments = parser.parse_args()
    if arguments.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    try:
        asyncio.run(main(arguments))
    except KeyboardInterrupt:
        pass
