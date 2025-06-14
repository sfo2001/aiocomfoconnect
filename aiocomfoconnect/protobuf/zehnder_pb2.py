# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: zehnder.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'zehnder.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import aiocomfoconnect.protobuf.nanopb_pb2 as nanopb__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rzehnder.proto\x1a\x0cnanopb.proto\"\x80\x01\n\x12\x44iscoveryOperation\x12\x33\n\x14searchGatewayRequest\x18\x01 \x01(\x0b\x32\x15.SearchGatewayRequest\x12\x35\n\x15searchGatewayResponse\x18\x02 \x01(\x0b\x32\x16.SearchGatewayResponse\"\x16\n\x14SearchGatewayRequest\"\xb4\x01\n\x15SearchGatewayResponse\x12\x18\n\tipaddress\x18\x01 \x02(\tB\x05\x92?\x02\x08\x10\x12\x13\n\x04uuid\x18\x02 \x02(\x0c\x42\x05\x92?\x02\x08\x10\x12\x0f\n\x07version\x18\x03 \x02(\r\x12\x36\n\x04type\x18\x04 \x01(\x0e\x32\".SearchGatewayResponse.GatewayType:\x04lanc\"#\n\x0bGatewayType\x12\x08\n\x04lanc\x10\x00\x12\n\n\x06season\x10\x01\"\xd5\x12\n\x10GatewayOperation\x12:\n\x04type\x18\x01 \x01(\x0e\x32\x1f.GatewayOperation.OperationType:\x0bNoOperation\x12\x33\n\x06result\x18\x02 \x01(\x0e\x32\x1f.GatewayOperation.GatewayResult:\x02OK\x12\x19\n\x11resultDescription\x18\x03 \x01(\t\x12\x11\n\treference\x18\x04 \x01(\r\"\xfb\x0f\n\rOperationType\x12\x0f\n\x0bNoOperation\x10\x00\x12\x19\n\x15SetAddressRequestType\x10\x01\x12\x1a\n\x16RegisterAppRequestType\x10\x02\x12\x1b\n\x17StartSessionRequestType\x10\x03\x12\x1b\n\x17\x43loseSessionRequestType\x10\x04\x12!\n\x1dListRegisteredAppsRequestType\x10\x05\x12\x1c\n\x18\x44\x65registerAppRequestType\x10\x06\x12\x18\n\x14\x43hangePinRequestType\x10\x07\x12 \n\x1cGetRemoteAccessIdRequestType\x10\x08\x12 \n\x1cSetRemoteAccessIdRequestType\x10\t\x12\x1b\n\x17GetSupportIdRequestType\x10\n\x12\x1b\n\x17SetSupportIdRequestType\x10\x0b\x12\x17\n\x13GetWebIdRequestType\x10\x0c\x12\x17\n\x13SetWebIdRequestType\x10\r\x12\x18\n\x14SetPushIdRequestType\x10\x0e\x12\x14\n\x10\x44\x65\x62ugRequestType\x10\x0f\x12\x16\n\x12UpgradeRequestType\x10\x10\x12 \n\x1cSetDeviceSettingsRequestType\x10\x11\x12\x16\n\x12VersionRequestType\x10\x12\x12\x19\n\x15SetAddressConfirmType\x10\x33\x12\x1a\n\x16RegisterAppConfirmType\x10\x34\x12\x1b\n\x17StartSessionConfirmType\x10\x35\x12\x1b\n\x17\x43loseSessionConfirmType\x10\x36\x12!\n\x1dListRegisteredAppsConfirmType\x10\x37\x12\x1c\n\x18\x44\x65registerAppConfirmType\x10\x38\x12\x18\n\x14\x43hangePinConfirmType\x10\x39\x12 \n\x1cGetRemoteAccessIdConfirmType\x10:\x12 \n\x1cSetRemoteAccessIdConfirmType\x10;\x12\x1b\n\x17GetSupportIdConfirmType\x10<\x12\x1b\n\x17SetSupportIdConfirmType\x10=\x12\x17\n\x13GetWebIdConfirmType\x10>\x12\x17\n\x13SetWebIdConfirmType\x10?\x12\x18\n\x14SetPushIdConfirmType\x10@\x12\x14\n\x10\x44\x65\x62ugConfirmType\x10\x41\x12\x16\n\x12UpgradeConfirmType\x10\x42\x12 \n\x1cSetDeviceSettingsConfirmType\x10\x43\x12\x16\n\x12VersionConfirmType\x10\x44\x12\x1b\n\x17GatewayNotificationType\x10\x64\x12\x11\n\rKeepAliveType\x10\x65\x12\x14\n\x10\x46\x61\x63toryResetType\x10\x66\x12\x15\n\x11\x43nTimeRequestType\x10\x1e\x12\x15\n\x11\x43nTimeConfirmType\x10\x1f\x12\x15\n\x11\x43nNodeRequestType\x10*\x12\x1a\n\x16\x43nNodeNotificationType\x10 \x12\x14\n\x10\x43nRmiRequestType\x10!\x12\x15\n\x11\x43nRmiResponseType\x10\"\x12\x19\n\x15\x43nRmiAsyncRequestType\x10#\x12\x19\n\x15\x43nRmiAsyncConfirmType\x10$\x12\x1a\n\x16\x43nRmiAsyncResponseType\x10%\x12\x15\n\x11\x43nRpdoRequestType\x10&\x12\x15\n\x11\x43nRpdoConfirmType\x10\'\x12\x1a\n\x16\x43nRpdoNotificationType\x10(\x12\x1b\n\x17\x43nAlarmNotificationType\x10)\x12 \n\x1c\x43nFupReadRegisterRequestType\x10\x46\x12 \n\x1c\x43nFupReadRegisterConfirmType\x10G\x12 \n\x1c\x43nFupProgramBeginRequestType\x10H\x12 \n\x1c\x43nFupProgramBeginConfirmType\x10I\x12\x1b\n\x17\x43nFupProgramRequestType\x10J\x12\x1b\n\x17\x43nFupProgramConfirmType\x10K\x12\x1e\n\x1a\x43nFupProgramEndRequestType\x10L\x12\x1e\n\x1a\x43nFupProgramEndConfirmType\x10M\x12\x18\n\x14\x43nFupReadRequestType\x10N\x12\x18\n\x14\x43nFupReadConfirmType\x10O\x12\x19\n\x15\x43nFupResetRequestType\x10P\x12\x19\n\x15\x43nFupResetConfirmType\x10Q\x12\x17\n\x13\x43nWhoAmIRequestType\x10R\x12\x17\n\x13\x43nWhoAmIConfirmType\x10S\x12\x1b\n\x17WiFiSettingsRequestType\x10x\x12\x1b\n\x17WiFiSettingsConfirmType\x10y\x12\x1b\n\x17WiFiNetworksRequestType\x10z\x12\x1b\n\x17WiFiNetworksConfirmType\x10{\x12\x1e\n\x1aWiFiJoinNetworkRequestType\x10|\x12\x1e\n\x1aWiFiJoinNetworkConfirmType\x10}\"\xa3\x01\n\rGatewayResult\x12\x06\n\x02OK\x10\x00\x12\x0f\n\x0b\x42\x41\x44_REQUEST\x10\x01\x12\x12\n\x0eINTERNAL_ERROR\x10\x02\x12\x11\n\rNOT_REACHABLE\x10\x03\x12\x11\n\rOTHER_SESSION\x10\x04\x12\x0f\n\x0bNOT_ALLOWED\x10\x05\x12\x10\n\x0cNO_RESOURCES\x10\x06\x12\r\n\tNOT_EXIST\x10\x07\x12\r\n\tRMI_ERROR\x10\x08\"M\n\x13GatewayNotification\x12\x11\n\tpushUUIDs\x18\x01 \x03(\x0c\x12#\n\x05\x61larm\x18\x02 \x01(\x0b\x32\x14.CnAlarmNotification\"\x0b\n\tKeepAlive\"\'\n\x0c\x46\x61\x63toryReset\x12\x17\n\x08resetKey\x18\x01 \x02(\x0c\x42\x05\x92?\x02\x08\x10\"R\n\x18SetDeviceSettingsRequest\x12\x19\n\nmacAddress\x18\x01 \x02(\x0c\x42\x05\x92?\x02\x08\x10\x12\x1b\n\x0cserialNumber\x18\x02 \x02(\tB\x05\x92?\x02\x08\x10\"\x1a\n\x18SetDeviceSettingsConfirm\"(\n\x11SetAddressRequest\x12\x13\n\x04uuid\x18\x01 \x02(\x0c\x42\x05\x92?\x02\x08\x10\"\x13\n\x11SetAddressConfirm\"Q\n\x12RegisterAppRequest\x12\x13\n\x04uuid\x18\x01 \x02(\x0c\x42\x05\x92?\x02\x08\x10\x12\x0b\n\x03pin\x18\x02 \x02(\r\x12\x19\n\ndevicename\x18\x03 \x02(\tB\x05\x92?\x02\x08 \"\x14\n\x12RegisterAppConfirm\"\'\n\x13StartSessionRequest\x12\x10\n\x08takeover\x18\x01 \x01(\x08\"A\n\x13StartSessionConfirm\x12\x19\n\ndevicename\x18\x01 \x01(\tB\x05\x92?\x02\x08 \x12\x0f\n\x07resumed\x18\x02 \x01(\x08\"\x15\n\x13\x43loseSessionRequest\"\x15\n\x13\x43loseSessionConfirm\"\x1b\n\x19ListRegisteredAppsRequest\"\x80\x01\n\x19ListRegisteredAppsConfirm\x12,\n\x04\x61pps\x18\x01 \x03(\x0b\x32\x1e.ListRegisteredAppsConfirm.App\x1a\x35\n\x03\x41pp\x12\x13\n\x04uuid\x18\x01 \x02(\x0c\x42\x05\x92?\x02\x08\x10\x12\x19\n\ndevicename\x18\x02 \x02(\tB\x05\x92?\x02\x08 \"+\n\x14\x44\x65registerAppRequest\x12\x13\n\x04uuid\x18\x01 \x02(\x0c\x42\x05\x92?\x02\x08\x10\"\x16\n\x14\x44\x65registerAppConfirm\"2\n\x10\x43hangePinRequest\x12\x0e\n\x06oldpin\x18\x01 \x02(\r\x12\x0e\n\x06newpin\x18\x02 \x02(\r\"\x12\n\x10\x43hangePinConfirm\"\x1a\n\x18GetRemoteAccessIdRequest\"/\n\x18GetRemoteAccessIdConfirm\x12\x13\n\x04uuid\x18\x01 \x01(\x0c\x42\x05\x92?\x02\x08\x10\"/\n\x18SetRemoteAccessIdRequest\x12\x13\n\x04uuid\x18\x01 \x01(\x0c\x42\x05\x92?\x02\x08\x10\"\x1a\n\x18SetRemoteAccessIdConfirm\"\x15\n\x13GetSupportIdRequest\"A\n\x13GetSupportIdConfirm\x12\x13\n\x04uuid\x18\x01 \x01(\x0c\x42\x05\x92?\x02\x08\x10\x12\x15\n\rremainingTime\x18\x02 \x01(\r\"=\n\x13SetSupportIdRequest\x12\x13\n\x04uuid\x18\x01 \x01(\x0c\x42\x05\x92?\x02\x08\x10\x12\x11\n\tvalidTime\x18\x02 \x01(\r\"\x15\n\x13SetSupportIdConfirm\"\x11\n\x0fGetWebIdRequest\"&\n\x0fGetWebIdConfirm\x12\x13\n\x04uuid\x18\x01 \x01(\x0c\x42\x05\x92?\x02\x08\x10\"&\n\x0fSetWebIdRequest\x12\x13\n\x04uuid\x18\x01 \x01(\x0c\x42\x05\x92?\x02\x08\x10\"\x11\n\x0fSetWebIdConfirm\"\'\n\x10SetPushIdRequest\x12\x13\n\x04uuid\x18\x01 \x01(\x0c\x42\x05\x92?\x02\x08\x10\"\x12\n\x10SetPushIdConfirm\"\xd2\x01\n\x0eUpgradeRequest\x12H\n\x07\x63ommand\x18\x01 \x01(\x0e\x32%.UpgradeRequest.UpgradeRequestCommand:\x10UPGRADE_CONTINUE\x12\r\n\x05\x63hunk\x18\x02 \x01(\x0c\"g\n\x15UpgradeRequestCommand\x12\x11\n\rUPGRADE_START\x10\x00\x12\x14\n\x10UPGRADE_CONTINUE\x10\x01\x12\x12\n\x0eUPGRADE_FINISH\x10\x02\x12\x11\n\rUPGRADE_ABORT\x10\x03\"\x10\n\x0eUpgradeConfirm\"\xba\x03\n\x0c\x44\x65\x62ugRequest\x12\x32\n\x07\x63ommand\x18\x01 \x02(\x0e\x32!.DebugRequest.DebugRequestCommand\x12\x10\n\x08\x61rgument\x18\x02 \x01(\x05\"\xe3\x02\n\x13\x44\x65\x62ugRequestCommand\x12\x0c\n\x08\x44\x42G_ECHO\x10\x00\x12\r\n\tDBG_SLEEP\x10\x01\x12\x14\n\x10\x44\x42G_SESSION_ECHO\x10\x02\x12\x16\n\x12\x44\x42G_PRINT_SETTINGS\x10\x03\x12\r\n\tDBG_ALARM\x10\x04\x12\x0b\n\x07\x44\x42G_LED\x10\x05\x12\x0b\n\x07\x44\x42G_GPI\x10\x06\x12\x0b\n\x07\x44\x42G_GPO\x10\x07\x12\x13\n\x0f\x44\x42G_RS232_WRITE\x10\x08\x12\x12\n\x0e\x44\x42G_RS232_READ\x10\t\x12\x11\n\rDBG_CAN_WRITE\x10\n\x12\x10\n\x0c\x44\x42G_CAN_READ\x10\x0b\x12\x11\n\rDBG_KNX_WRITE\x10\x0c\x12\x10\n\x0c\x44\x42G_KNX_READ\x10\r\x12\x0e\n\nDBG_TOGGLE\x10\x0e\x12\x0e\n\nDBG_REBOOT\x10\x0f\x12\r\n\tDBG_CLOUD\x10\x10\x12\x13\n\x0f\x44\x42G_EEPROM_READ\x10\x11\x12\x14\n\x10\x44\x42G_EEPROM_WRITE\x10\x12\"\x1e\n\x0c\x44\x65\x62ugConfirm\x12\x0e\n\x06result\x18\x01 \x02(\x05\"\x10\n\x0eVersionRequest\"^\n\x0eVersionConfirm\x12\x16\n\x0egatewayVersion\x18\x01 \x02(\r\x12\x1b\n\x0cserialNumber\x18\x02 \x02(\tB\x05\x92?\x02\x08\x10\x12\x17\n\x0f\x63omfoNetVersion\x18\x03 \x02(\r\" \n\rCnTimeRequest\x12\x0f\n\x07setTime\x18\x01 \x01(\r\"$\n\rCnTimeConfirm\x12\x13\n\x0b\x63urrentTime\x18\x01 \x02(\r\"\x0f\n\rCnNodeRequest\"\xf1\x01\n\x12\x43nNodeNotification\x12\x15\n\x06nodeId\x18\x01 \x02(\rB\x05\x92?\x02\x38\x08\x12\x1b\n\tproductId\x18\x02 \x01(\r:\x01\x30\x42\x05\x92?\x02\x38\x08\x12\x15\n\x06zoneId\x18\x03 \x01(\rB\x05\x92?\x02\x38\x08\x12;\n\x04mode\x18\x04 \x01(\x0e\x32 .CnNodeNotification.NodeModeType:\x0bNODE_LEGACY\"S\n\x0cNodeModeType\x12\x0f\n\x0bNODE_LEGACY\x10\x00\x12\x10\n\x0cNODE_OFFLINE\x10\x01\x12\x0f\n\x0bNODE_NORMAL\x10\x02\x12\x0f\n\x0bNODE_UPDATE\x10\x03\"6\n\x0c\x43nRmiRequest\x12\x15\n\x06nodeId\x18\x01 \x02(\rB\x05\x92?\x02\x38\x08\x12\x0f\n\x07message\x18\x02 \x02(\x0c\"3\n\rCnRmiResponse\x12\x11\n\x06result\x18\x01 \x01(\r:\x01\x30\x12\x0f\n\x07message\x18\x02 \x01(\x0c\";\n\x11\x43nRmiAsyncRequest\x12\x15\n\x06nodeId\x18\x01 \x02(\rB\x05\x92?\x02\x38\x08\x12\x0f\n\x07message\x18\x02 \x02(\x0c\"&\n\x11\x43nRmiAsyncConfirm\x12\x11\n\x06result\x18\x01 \x01(\r:\x01\x30\"8\n\x12\x43nRmiAsyncResponse\x12\x11\n\x06result\x18\x01 \x01(\r:\x01\x30\x12\x0f\n\x07message\x18\x02 \x01(\x0c\"~\n\rCnRpdoRequest\x12\x13\n\x04pdid\x18\x01 \x02(\rB\x05\x92?\x02\x38\x10\x12\x18\n\x04zone\x18\x02 \x01(\r:\x03\x32\x35\x35\x42\x05\x92?\x02\x38\x08\x12\x0c\n\x04type\x18\x03 \x01(\r\x12\x1b\n\x07timeout\x18\x04 \x01(\r:\n4294967295\x12\x13\n\x08interval\x18\x05 \x01(\r:\x01\x30\"\x0f\n\rCnRpdoConfirm\"V\n\x12\x43nRpdoNotification\x12\x13\n\x04pdid\x18\x01 \x02(\rB\x05\x92?\x02\x38\x10\x12\x13\n\x04\x64\x61ta\x18\x02 \x02(\x0c\x42\x05\x92?\x02\x08\x08\x12\x16\n\x04zone\x18\x03 \x01(\r:\x01\x31\x42\x05\x92?\x02\x38\x08\"\xe0\x01\n\x13\x43nAlarmNotification\x12\x13\n\x04zone\x18\x01 \x01(\rB\x05\x92?\x02\x38\x08\x12\x18\n\tproductId\x18\x02 \x01(\rB\x05\x92?\x02\x38\x08\x12\x1d\n\x0eproductVariant\x18\x03 \x01(\rB\x05\x92?\x02\x38\x08\x12\x1b\n\x0cserialNumber\x18\x04 \x01(\tB\x05\x92?\x02\x08 \x12\x18\n\x10swProgramVersion\x18\x05 \x01(\r\x12\x15\n\x06\x65rrors\x18\x06 \x01(\x0c\x42\x05\x92?\x02\x08 \x12\x16\n\x07\x65rrorId\x18\x07 \x01(\rB\x05\x92?\x02\x38\x08\x12\x15\n\x06nodeId\x18\x08 \x01(\rB\x05\x92?\x02\x38\x08\"`\n\x18\x43nFupReadRegisterRequest\x12\x13\n\x04node\x18\x01 \x02(\rB\x05\x92?\x02\x38\x08\x12\x19\n\nregisterId\x18\x02 \x02(\rB\x05\x92?\x02\x38\x08\x12\x14\n\x05index\x18\x03 \x01(\rB\x05\x92?\x02\x38\x08\")\n\x18\x43nFupReadRegisterConfirm\x12\r\n\x05value\x18\x01 \x02(\r\"J\n\x18\x43nFupProgramBeginRequest\x12\x15\n\x04node\x18\x01 \x03(\rB\x07\x92?\x04\x10 8\x08\x12\x17\n\x05\x62lock\x18\x02 \x01(\r:\x01\x30\x42\x05\x92?\x02\x38\x08\"\x1a\n\x18\x43nFupProgramBeginConfirm\"$\n\x13\x43nFupProgramRequest\x12\r\n\x05\x63hunk\x18\x01 \x02(\x0c\"\x15\n\x13\x43nFupProgramConfirm\"\x18\n\x16\x43nFupProgramEndRequest\"\x18\n\x16\x43nFupProgramEndConfirm\"@\n\x10\x43nFupReadRequest\x12\x13\n\x04node\x18\x01 \x02(\rB\x05\x92?\x02\x38\x08\x12\x17\n\x05\x62lock\x18\x02 \x01(\r:\x01\x30\x42\x05\x92?\x02\x38\x08\"6\n\x10\x43nFupReadConfirm\x12\r\n\x05\x63hunk\x18\x01 \x01(\x0c\x12\x13\n\x04last\x18\x02 \x01(\x08:\x05\x66\x61lse\"(\n\x11\x43nFupResetRequest\x12\x13\n\x04node\x18\x01 \x02(\rB\x05\x92?\x02\x38\x08\"\x13\n\x11\x43nFupResetConfirm\"=\n\x0f\x43nWhoAmIRequest\x12\x15\n\x06nodeId\x18\x01 \x01(\rB\x05\x92?\x02\x38\x08\x12\x13\n\x04zone\x18\x02 \x01(\rB\x05\x92?\x02\x38\x08\"\x11\n\x0f\x43nWhoAmIConfirm\"b\n\x0bWiFiNetwork\x12\x13\n\x04ssid\x18\x01 \x02(\tB\x05\x92?\x02\x08 \x12)\n\x08security\x18\x02 \x02(\x0e\x32\r.WiFiSecurity:\x08WPA_WPA2\x12\x13\n\x04rssi\x18\x03 \x02(\x05\x42\x05\x92?\x02\x38\x08\"\x15\n\x13WiFiSettingsRequest\"\xf6\x01\n\x13WiFiSettingsConfirm\x12\x17\n\x04mode\x18\x01 \x02(\x0e\x32\t.WiFiMode\x12\x1d\n\x07\x63urrent\x18\x02 \x01(\x0b\x32\x0c.WiFiNetwork\x12;\n\njoinResult\x18\x03 \x01(\x0e\x32#.WiFiSettingsConfirm.WiFiJoinResult:\x02OK\"j\n\x0eWiFiJoinResult\x12\x06\n\x02OK\x10\x00\x12\r\n\tSCAN_FAIL\x10\x01\x12\r\n\tJOIN_FAIL\x10\x02\x12\r\n\tAUTH_FAIL\x10\x03\x12\x0e\n\nASSOC_FAIL\x10\x04\x12\x13\n\x0f\x43ONN_INPROGRESS\x10\x05\"/\n\x13WiFiNetworksRequest\x12\x18\n\tforceScan\x18\x01 \x01(\x08:\x05\x66\x61lse\"F\n\x13WiFiNetworksConfirm\x12\x1e\n\x08networks\x18\x01 \x03(\x0b\x32\x0c.WiFiNetwork\x12\x0f\n\x07scanAge\x18\x02 \x01(\r\"\x8a\x01\n\x16WiFiJoinNetworkRequest\x12\x17\n\x04mode\x18\x01 \x02(\x0e\x32\t.WiFiMode\x12\x13\n\x04ssid\x18\x02 \x01(\tB\x05\x92?\x02\x08 \x12\x17\n\x08password\x18\x03 \x01(\tB\x05\x92?\x02\x08@\x12)\n\x08security\x18\x04 \x01(\x0e\x32\r.WiFiSecurity:\x08WPA_WPA2\"\x18\n\x16WiFiJoinNetworkConfirm*M\n\x0cWiFiSecurity\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x08\n\x04OPEN\x10\x01\x12\x0c\n\x08WPA_WPA2\x10\x02\x12\x07\n\x03WEP\x10\x03\x12\x0f\n\x0bIEEE_802_1X\x10\x04*\x1b\n\x08WiFiMode\x12\x06\n\x02\x41P\x10\x00\x12\x07\n\x03STA\x10\x01\x42\x15\n\x11\x63om.zehnder.protoH\x01')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'zehnder_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\021com.zehnder.protoH\001'
  _globals['_SEARCHGATEWAYRESPONSE'].fields_by_name['ipaddress']._loaded_options = None
  _globals['_SEARCHGATEWAYRESPONSE'].fields_by_name['ipaddress']._serialized_options = b'\222?\002\010\020'
  _globals['_SEARCHGATEWAYRESPONSE'].fields_by_name['uuid']._loaded_options = None
  _globals['_SEARCHGATEWAYRESPONSE'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_FACTORYRESET'].fields_by_name['resetKey']._loaded_options = None
  _globals['_FACTORYRESET'].fields_by_name['resetKey']._serialized_options = b'\222?\002\010\020'
  _globals['_SETDEVICESETTINGSREQUEST'].fields_by_name['macAddress']._loaded_options = None
  _globals['_SETDEVICESETTINGSREQUEST'].fields_by_name['macAddress']._serialized_options = b'\222?\002\010\020'
  _globals['_SETDEVICESETTINGSREQUEST'].fields_by_name['serialNumber']._loaded_options = None
  _globals['_SETDEVICESETTINGSREQUEST'].fields_by_name['serialNumber']._serialized_options = b'\222?\002\010\020'
  _globals['_SETADDRESSREQUEST'].fields_by_name['uuid']._loaded_options = None
  _globals['_SETADDRESSREQUEST'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_REGISTERAPPREQUEST'].fields_by_name['uuid']._loaded_options = None
  _globals['_REGISTERAPPREQUEST'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_REGISTERAPPREQUEST'].fields_by_name['devicename']._loaded_options = None
  _globals['_REGISTERAPPREQUEST'].fields_by_name['devicename']._serialized_options = b'\222?\002\010 '
  _globals['_STARTSESSIONCONFIRM'].fields_by_name['devicename']._loaded_options = None
  _globals['_STARTSESSIONCONFIRM'].fields_by_name['devicename']._serialized_options = b'\222?\002\010 '
  _globals['_LISTREGISTEREDAPPSCONFIRM_APP'].fields_by_name['uuid']._loaded_options = None
  _globals['_LISTREGISTEREDAPPSCONFIRM_APP'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_LISTREGISTEREDAPPSCONFIRM_APP'].fields_by_name['devicename']._loaded_options = None
  _globals['_LISTREGISTEREDAPPSCONFIRM_APP'].fields_by_name['devicename']._serialized_options = b'\222?\002\010 '
  _globals['_DEREGISTERAPPREQUEST'].fields_by_name['uuid']._loaded_options = None
  _globals['_DEREGISTERAPPREQUEST'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_GETREMOTEACCESSIDCONFIRM'].fields_by_name['uuid']._loaded_options = None
  _globals['_GETREMOTEACCESSIDCONFIRM'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_SETREMOTEACCESSIDREQUEST'].fields_by_name['uuid']._loaded_options = None
  _globals['_SETREMOTEACCESSIDREQUEST'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_GETSUPPORTIDCONFIRM'].fields_by_name['uuid']._loaded_options = None
  _globals['_GETSUPPORTIDCONFIRM'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_SETSUPPORTIDREQUEST'].fields_by_name['uuid']._loaded_options = None
  _globals['_SETSUPPORTIDREQUEST'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_GETWEBIDCONFIRM'].fields_by_name['uuid']._loaded_options = None
  _globals['_GETWEBIDCONFIRM'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_SETWEBIDREQUEST'].fields_by_name['uuid']._loaded_options = None
  _globals['_SETWEBIDREQUEST'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_SETPUSHIDREQUEST'].fields_by_name['uuid']._loaded_options = None
  _globals['_SETPUSHIDREQUEST'].fields_by_name['uuid']._serialized_options = b'\222?\002\010\020'
  _globals['_VERSIONCONFIRM'].fields_by_name['serialNumber']._loaded_options = None
  _globals['_VERSIONCONFIRM'].fields_by_name['serialNumber']._serialized_options = b'\222?\002\010\020'
  _globals['_CNNODENOTIFICATION'].fields_by_name['nodeId']._loaded_options = None
  _globals['_CNNODENOTIFICATION'].fields_by_name['nodeId']._serialized_options = b'\222?\0028\010'
  _globals['_CNNODENOTIFICATION'].fields_by_name['productId']._loaded_options = None
  _globals['_CNNODENOTIFICATION'].fields_by_name['productId']._serialized_options = b'\222?\0028\010'
  _globals['_CNNODENOTIFICATION'].fields_by_name['zoneId']._loaded_options = None
  _globals['_CNNODENOTIFICATION'].fields_by_name['zoneId']._serialized_options = b'\222?\0028\010'
  _globals['_CNRMIREQUEST'].fields_by_name['nodeId']._loaded_options = None
  _globals['_CNRMIREQUEST'].fields_by_name['nodeId']._serialized_options = b'\222?\0028\010'
  _globals['_CNRMIASYNCREQUEST'].fields_by_name['nodeId']._loaded_options = None
  _globals['_CNRMIASYNCREQUEST'].fields_by_name['nodeId']._serialized_options = b'\222?\0028\010'
  _globals['_CNRPDOREQUEST'].fields_by_name['pdid']._loaded_options = None
  _globals['_CNRPDOREQUEST'].fields_by_name['pdid']._serialized_options = b'\222?\0028\020'
  _globals['_CNRPDOREQUEST'].fields_by_name['zone']._loaded_options = None
  _globals['_CNRPDOREQUEST'].fields_by_name['zone']._serialized_options = b'\222?\0028\010'
  _globals['_CNRPDONOTIFICATION'].fields_by_name['pdid']._loaded_options = None
  _globals['_CNRPDONOTIFICATION'].fields_by_name['pdid']._serialized_options = b'\222?\0028\020'
  _globals['_CNRPDONOTIFICATION'].fields_by_name['data']._loaded_options = None
  _globals['_CNRPDONOTIFICATION'].fields_by_name['data']._serialized_options = b'\222?\002\010\010'
  _globals['_CNRPDONOTIFICATION'].fields_by_name['zone']._loaded_options = None
  _globals['_CNRPDONOTIFICATION'].fields_by_name['zone']._serialized_options = b'\222?\0028\010'
  _globals['_CNALARMNOTIFICATION'].fields_by_name['zone']._loaded_options = None
  _globals['_CNALARMNOTIFICATION'].fields_by_name['zone']._serialized_options = b'\222?\0028\010'
  _globals['_CNALARMNOTIFICATION'].fields_by_name['productId']._loaded_options = None
  _globals['_CNALARMNOTIFICATION'].fields_by_name['productId']._serialized_options = b'\222?\0028\010'
  _globals['_CNALARMNOTIFICATION'].fields_by_name['productVariant']._loaded_options = None
  _globals['_CNALARMNOTIFICATION'].fields_by_name['productVariant']._serialized_options = b'\222?\0028\010'
  _globals['_CNALARMNOTIFICATION'].fields_by_name['serialNumber']._loaded_options = None
  _globals['_CNALARMNOTIFICATION'].fields_by_name['serialNumber']._serialized_options = b'\222?\002\010 '
  _globals['_CNALARMNOTIFICATION'].fields_by_name['errors']._loaded_options = None
  _globals['_CNALARMNOTIFICATION'].fields_by_name['errors']._serialized_options = b'\222?\002\010 '
  _globals['_CNALARMNOTIFICATION'].fields_by_name['errorId']._loaded_options = None
  _globals['_CNALARMNOTIFICATION'].fields_by_name['errorId']._serialized_options = b'\222?\0028\010'
  _globals['_CNALARMNOTIFICATION'].fields_by_name['nodeId']._loaded_options = None
  _globals['_CNALARMNOTIFICATION'].fields_by_name['nodeId']._serialized_options = b'\222?\0028\010'
  _globals['_CNFUPREADREGISTERREQUEST'].fields_by_name['node']._loaded_options = None
  _globals['_CNFUPREADREGISTERREQUEST'].fields_by_name['node']._serialized_options = b'\222?\0028\010'
  _globals['_CNFUPREADREGISTERREQUEST'].fields_by_name['registerId']._loaded_options = None
  _globals['_CNFUPREADREGISTERREQUEST'].fields_by_name['registerId']._serialized_options = b'\222?\0028\010'
  _globals['_CNFUPREADREGISTERREQUEST'].fields_by_name['index']._loaded_options = None
  _globals['_CNFUPREADREGISTERREQUEST'].fields_by_name['index']._serialized_options = b'\222?\0028\010'
  _globals['_CNFUPPROGRAMBEGINREQUEST'].fields_by_name['node']._loaded_options = None
  _globals['_CNFUPPROGRAMBEGINREQUEST'].fields_by_name['node']._serialized_options = b'\222?\004\020 8\010'
  _globals['_CNFUPPROGRAMBEGINREQUEST'].fields_by_name['block']._loaded_options = None
  _globals['_CNFUPPROGRAMBEGINREQUEST'].fields_by_name['block']._serialized_options = b'\222?\0028\010'
  _globals['_CNFUPREADREQUEST'].fields_by_name['node']._loaded_options = None
  _globals['_CNFUPREADREQUEST'].fields_by_name['node']._serialized_options = b'\222?\0028\010'
  _globals['_CNFUPREADREQUEST'].fields_by_name['block']._loaded_options = None
  _globals['_CNFUPREADREQUEST'].fields_by_name['block']._serialized_options = b'\222?\0028\010'
  _globals['_CNFUPRESETREQUEST'].fields_by_name['node']._loaded_options = None
  _globals['_CNFUPRESETREQUEST'].fields_by_name['node']._serialized_options = b'\222?\0028\010'
  _globals['_CNWHOAMIREQUEST'].fields_by_name['nodeId']._loaded_options = None
  _globals['_CNWHOAMIREQUEST'].fields_by_name['nodeId']._serialized_options = b'\222?\0028\010'
  _globals['_CNWHOAMIREQUEST'].fields_by_name['zone']._loaded_options = None
  _globals['_CNWHOAMIREQUEST'].fields_by_name['zone']._serialized_options = b'\222?\0028\010'
  _globals['_WIFINETWORK'].fields_by_name['ssid']._loaded_options = None
  _globals['_WIFINETWORK'].fields_by_name['ssid']._serialized_options = b'\222?\002\010 '
  _globals['_WIFINETWORK'].fields_by_name['rssi']._loaded_options = None
  _globals['_WIFINETWORK'].fields_by_name['rssi']._serialized_options = b'\222?\0028\010'
  _globals['_WIFIJOINNETWORKREQUEST'].fields_by_name['ssid']._loaded_options = None
  _globals['_WIFIJOINNETWORKREQUEST'].fields_by_name['ssid']._serialized_options = b'\222?\002\010 '
  _globals['_WIFIJOINNETWORKREQUEST'].fields_by_name['password']._loaded_options = None
  _globals['_WIFIJOINNETWORKREQUEST'].fields_by_name['password']._serialized_options = b'\222?\002\010@'
  _globals['_WIFISECURITY']._serialized_start=7306
  _globals['_WIFISECURITY']._serialized_end=7383
  _globals['_WIFIMODE']._serialized_start=7385
  _globals['_WIFIMODE']._serialized_end=7412
  _globals['_DISCOVERYOPERATION']._serialized_start=32
  _globals['_DISCOVERYOPERATION']._serialized_end=160
  _globals['_SEARCHGATEWAYREQUEST']._serialized_start=162
  _globals['_SEARCHGATEWAYREQUEST']._serialized_end=184
  _globals['_SEARCHGATEWAYRESPONSE']._serialized_start=187
  _globals['_SEARCHGATEWAYRESPONSE']._serialized_end=367
  _globals['_SEARCHGATEWAYRESPONSE_GATEWAYTYPE']._serialized_start=332
  _globals['_SEARCHGATEWAYRESPONSE_GATEWAYTYPE']._serialized_end=367
  _globals['_GATEWAYOPERATION']._serialized_start=370
  _globals['_GATEWAYOPERATION']._serialized_end=2759
  _globals['_GATEWAYOPERATION_OPERATIONTYPE']._serialized_start=550
  _globals['_GATEWAYOPERATION_OPERATIONTYPE']._serialized_end=2593
  _globals['_GATEWAYOPERATION_GATEWAYRESULT']._serialized_start=2596
  _globals['_GATEWAYOPERATION_GATEWAYRESULT']._serialized_end=2759
  _globals['_GATEWAYNOTIFICATION']._serialized_start=2761
  _globals['_GATEWAYNOTIFICATION']._serialized_end=2838
  _globals['_KEEPALIVE']._serialized_start=2840
  _globals['_KEEPALIVE']._serialized_end=2851
  _globals['_FACTORYRESET']._serialized_start=2853
  _globals['_FACTORYRESET']._serialized_end=2892
  _globals['_SETDEVICESETTINGSREQUEST']._serialized_start=2894
  _globals['_SETDEVICESETTINGSREQUEST']._serialized_end=2976
  _globals['_SETDEVICESETTINGSCONFIRM']._serialized_start=2978
  _globals['_SETDEVICESETTINGSCONFIRM']._serialized_end=3004
  _globals['_SETADDRESSREQUEST']._serialized_start=3006
  _globals['_SETADDRESSREQUEST']._serialized_end=3046
  _globals['_SETADDRESSCONFIRM']._serialized_start=3048
  _globals['_SETADDRESSCONFIRM']._serialized_end=3067
  _globals['_REGISTERAPPREQUEST']._serialized_start=3069
  _globals['_REGISTERAPPREQUEST']._serialized_end=3150
  _globals['_REGISTERAPPCONFIRM']._serialized_start=3152
  _globals['_REGISTERAPPCONFIRM']._serialized_end=3172
  _globals['_STARTSESSIONREQUEST']._serialized_start=3174
  _globals['_STARTSESSIONREQUEST']._serialized_end=3213
  _globals['_STARTSESSIONCONFIRM']._serialized_start=3215
  _globals['_STARTSESSIONCONFIRM']._serialized_end=3280
  _globals['_CLOSESESSIONREQUEST']._serialized_start=3282
  _globals['_CLOSESESSIONREQUEST']._serialized_end=3303
  _globals['_CLOSESESSIONCONFIRM']._serialized_start=3305
  _globals['_CLOSESESSIONCONFIRM']._serialized_end=3326
  _globals['_LISTREGISTEREDAPPSREQUEST']._serialized_start=3328
  _globals['_LISTREGISTEREDAPPSREQUEST']._serialized_end=3355
  _globals['_LISTREGISTEREDAPPSCONFIRM']._serialized_start=3358
  _globals['_LISTREGISTEREDAPPSCONFIRM']._serialized_end=3486
  _globals['_LISTREGISTEREDAPPSCONFIRM_APP']._serialized_start=3433
  _globals['_LISTREGISTEREDAPPSCONFIRM_APP']._serialized_end=3486
  _globals['_DEREGISTERAPPREQUEST']._serialized_start=3488
  _globals['_DEREGISTERAPPREQUEST']._serialized_end=3531
  _globals['_DEREGISTERAPPCONFIRM']._serialized_start=3533
  _globals['_DEREGISTERAPPCONFIRM']._serialized_end=3555
  _globals['_CHANGEPINREQUEST']._serialized_start=3557
  _globals['_CHANGEPINREQUEST']._serialized_end=3607
  _globals['_CHANGEPINCONFIRM']._serialized_start=3609
  _globals['_CHANGEPINCONFIRM']._serialized_end=3627
  _globals['_GETREMOTEACCESSIDREQUEST']._serialized_start=3629
  _globals['_GETREMOTEACCESSIDREQUEST']._serialized_end=3655
  _globals['_GETREMOTEACCESSIDCONFIRM']._serialized_start=3657
  _globals['_GETREMOTEACCESSIDCONFIRM']._serialized_end=3704
  _globals['_SETREMOTEACCESSIDREQUEST']._serialized_start=3706
  _globals['_SETREMOTEACCESSIDREQUEST']._serialized_end=3753
  _globals['_SETREMOTEACCESSIDCONFIRM']._serialized_start=3755
  _globals['_SETREMOTEACCESSIDCONFIRM']._serialized_end=3781
  _globals['_GETSUPPORTIDREQUEST']._serialized_start=3783
  _globals['_GETSUPPORTIDREQUEST']._serialized_end=3804
  _globals['_GETSUPPORTIDCONFIRM']._serialized_start=3806
  _globals['_GETSUPPORTIDCONFIRM']._serialized_end=3871
  _globals['_SETSUPPORTIDREQUEST']._serialized_start=3873
  _globals['_SETSUPPORTIDREQUEST']._serialized_end=3934
  _globals['_SETSUPPORTIDCONFIRM']._serialized_start=3936
  _globals['_SETSUPPORTIDCONFIRM']._serialized_end=3957
  _globals['_GETWEBIDREQUEST']._serialized_start=3959
  _globals['_GETWEBIDREQUEST']._serialized_end=3976
  _globals['_GETWEBIDCONFIRM']._serialized_start=3978
  _globals['_GETWEBIDCONFIRM']._serialized_end=4016
  _globals['_SETWEBIDREQUEST']._serialized_start=4018
  _globals['_SETWEBIDREQUEST']._serialized_end=4056
  _globals['_SETWEBIDCONFIRM']._serialized_start=4058
  _globals['_SETWEBIDCONFIRM']._serialized_end=4075
  _globals['_SETPUSHIDREQUEST']._serialized_start=4077
  _globals['_SETPUSHIDREQUEST']._serialized_end=4116
  _globals['_SETPUSHIDCONFIRM']._serialized_start=4118
  _globals['_SETPUSHIDCONFIRM']._serialized_end=4136
  _globals['_UPGRADEREQUEST']._serialized_start=4139
  _globals['_UPGRADEREQUEST']._serialized_end=4349
  _globals['_UPGRADEREQUEST_UPGRADEREQUESTCOMMAND']._serialized_start=4246
  _globals['_UPGRADEREQUEST_UPGRADEREQUESTCOMMAND']._serialized_end=4349
  _globals['_UPGRADECONFIRM']._serialized_start=4351
  _globals['_UPGRADECONFIRM']._serialized_end=4367
  _globals['_DEBUGREQUEST']._serialized_start=4370
  _globals['_DEBUGREQUEST']._serialized_end=4812
  _globals['_DEBUGREQUEST_DEBUGREQUESTCOMMAND']._serialized_start=4457
  _globals['_DEBUGREQUEST_DEBUGREQUESTCOMMAND']._serialized_end=4812
  _globals['_DEBUGCONFIRM']._serialized_start=4814
  _globals['_DEBUGCONFIRM']._serialized_end=4844
  _globals['_VERSIONREQUEST']._serialized_start=4846
  _globals['_VERSIONREQUEST']._serialized_end=4862
  _globals['_VERSIONCONFIRM']._serialized_start=4864
  _globals['_VERSIONCONFIRM']._serialized_end=4958
  _globals['_CNTIMEREQUEST']._serialized_start=4960
  _globals['_CNTIMEREQUEST']._serialized_end=4992
  _globals['_CNTIMECONFIRM']._serialized_start=4994
  _globals['_CNTIMECONFIRM']._serialized_end=5030
  _globals['_CNNODEREQUEST']._serialized_start=5032
  _globals['_CNNODEREQUEST']._serialized_end=5047
  _globals['_CNNODENOTIFICATION']._serialized_start=5050
  _globals['_CNNODENOTIFICATION']._serialized_end=5291
  _globals['_CNNODENOTIFICATION_NODEMODETYPE']._serialized_start=5208
  _globals['_CNNODENOTIFICATION_NODEMODETYPE']._serialized_end=5291
  _globals['_CNRMIREQUEST']._serialized_start=5293
  _globals['_CNRMIREQUEST']._serialized_end=5347
  _globals['_CNRMIRESPONSE']._serialized_start=5349
  _globals['_CNRMIRESPONSE']._serialized_end=5400
  _globals['_CNRMIASYNCREQUEST']._serialized_start=5402
  _globals['_CNRMIASYNCREQUEST']._serialized_end=5461
  _globals['_CNRMIASYNCCONFIRM']._serialized_start=5463
  _globals['_CNRMIASYNCCONFIRM']._serialized_end=5501
  _globals['_CNRMIASYNCRESPONSE']._serialized_start=5503
  _globals['_CNRMIASYNCRESPONSE']._serialized_end=5559
  _globals['_CNRPDOREQUEST']._serialized_start=5561
  _globals['_CNRPDOREQUEST']._serialized_end=5687
  _globals['_CNRPDOCONFIRM']._serialized_start=5689
  _globals['_CNRPDOCONFIRM']._serialized_end=5704
  _globals['_CNRPDONOTIFICATION']._serialized_start=5706
  _globals['_CNRPDONOTIFICATION']._serialized_end=5792
  _globals['_CNALARMNOTIFICATION']._serialized_start=5795
  _globals['_CNALARMNOTIFICATION']._serialized_end=6019
  _globals['_CNFUPREADREGISTERREQUEST']._serialized_start=6021
  _globals['_CNFUPREADREGISTERREQUEST']._serialized_end=6117
  _globals['_CNFUPREADREGISTERCONFIRM']._serialized_start=6119
  _globals['_CNFUPREADREGISTERCONFIRM']._serialized_end=6160
  _globals['_CNFUPPROGRAMBEGINREQUEST']._serialized_start=6162
  _globals['_CNFUPPROGRAMBEGINREQUEST']._serialized_end=6236
  _globals['_CNFUPPROGRAMBEGINCONFIRM']._serialized_start=6238
  _globals['_CNFUPPROGRAMBEGINCONFIRM']._serialized_end=6264
  _globals['_CNFUPPROGRAMREQUEST']._serialized_start=6266
  _globals['_CNFUPPROGRAMREQUEST']._serialized_end=6302
  _globals['_CNFUPPROGRAMCONFIRM']._serialized_start=6304
  _globals['_CNFUPPROGRAMCONFIRM']._serialized_end=6325
  _globals['_CNFUPPROGRAMENDREQUEST']._serialized_start=6327
  _globals['_CNFUPPROGRAMENDREQUEST']._serialized_end=6351
  _globals['_CNFUPPROGRAMENDCONFIRM']._serialized_start=6353
  _globals['_CNFUPPROGRAMENDCONFIRM']._serialized_end=6377
  _globals['_CNFUPREADREQUEST']._serialized_start=6379
  _globals['_CNFUPREADREQUEST']._serialized_end=6443
  _globals['_CNFUPREADCONFIRM']._serialized_start=6445
  _globals['_CNFUPREADCONFIRM']._serialized_end=6499
  _globals['_CNFUPRESETREQUEST']._serialized_start=6501
  _globals['_CNFUPRESETREQUEST']._serialized_end=6541
  _globals['_CNFUPRESETCONFIRM']._serialized_start=6543
  _globals['_CNFUPRESETCONFIRM']._serialized_end=6562
  _globals['_CNWHOAMIREQUEST']._serialized_start=6564
  _globals['_CNWHOAMIREQUEST']._serialized_end=6625
  _globals['_CNWHOAMICONFIRM']._serialized_start=6627
  _globals['_CNWHOAMICONFIRM']._serialized_end=6644
  _globals['_WIFINETWORK']._serialized_start=6646
  _globals['_WIFINETWORK']._serialized_end=6744
  _globals['_WIFISETTINGSREQUEST']._serialized_start=6746
  _globals['_WIFISETTINGSREQUEST']._serialized_end=6767
  _globals['_WIFISETTINGSCONFIRM']._serialized_start=6770
  _globals['_WIFISETTINGSCONFIRM']._serialized_end=7016
  _globals['_WIFISETTINGSCONFIRM_WIFIJOINRESULT']._serialized_start=6910
  _globals['_WIFISETTINGSCONFIRM_WIFIJOINRESULT']._serialized_end=7016
  _globals['_WIFINETWORKSREQUEST']._serialized_start=7018
  _globals['_WIFINETWORKSREQUEST']._serialized_end=7065
  _globals['_WIFINETWORKSCONFIRM']._serialized_start=7067
  _globals['_WIFINETWORKSCONFIRM']._serialized_end=7137
  _globals['_WIFIJOINNETWORKREQUEST']._serialized_start=7140
  _globals['_WIFIJOINNETWORKREQUEST']._serialized_end=7278
  _globals['_WIFIJOINNETWORKCONFIRM']._serialized_start=7280
  _globals['_WIFIJOINNETWORKCONFIRM']._serialized_end=7304
# @@protoc_insertion_point(module_scope)
