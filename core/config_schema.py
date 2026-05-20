"""Parameter definitions used by the configuration UI and CLI layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


FieldType = Literal["int", "float", "string", "enum", "bool"]


@dataclass(frozen=True)
class ParameterDef:
    """Describes one configurable module CLI parameter."""

    key: str
    label: str
    field_type: FieldType
    default: Any
    description: str
    minimum: int | float | None = None
    maximum: int | float | None = None
    step: int | float = 1
    options: tuple[str, ...] = ()
    option_values: dict[str, str] | None = None
    favorite: bool = False
    group: str = "TX"


PARAMETERS: tuple[ParameterDef, ...] = (
    ParameterDef(
        "tx_power",
        "TX Power",
        "int",
        0,
        "RF transmit power level. CLI: p tx_power=0-5;",
        minimum=0,
        maximum=5,
        favorite=True,
    ),
    ParameterDef(
        "rf_band",
        "RF Band",
        "enum",
        "2.4GHz",
        "RF band. CLI: p rf_band=0-2;",
        options=("2.4GHz", "915MHz", "868MHz"),
        option_values={"2.4GHz": "0", "915MHz": "1", "868MHz": "2"},
        favorite=True,
    ),
    ParameterDef(
        "tx_ch_source",
        "CH Source",
        "enum",
        "None",
        "Channel source. CLI: p tx_ch_source=0-3;",
        options=("None", "Sbus", "CRSF", "mBridge"),
        option_values={"None": "0", "Sbus": "1", "CRSF": "2", "mBridge": "3"},
        favorite=True,
    ),
    ParameterDef(
        "bind_phrase",
        "Bind Phrase",
        "string",
        "",
        "Bind phrase string. CLI: p bind_phrase={phrase};",
        favorite=True,
    ),
    ParameterDef(
        "mode",
        "Mode",
        "enum",
        "50Hz",
        "Radio mode. CLI: p mode=0-4;",
        options=("50Hz", "31Hz", "19Hz", "FLRC", "FSK"),
        option_values={"50Hz": "0", "31Hz": "1", "19Hz": "2", "FLRC": "3", "FSK": "4"},
        favorite=True,
    ),
    ParameterDef(
        "tx_ch_order",
        "CH Order",
        "enum",
        "AETR",
        "Channel order. CLI: p tx_ch_order=0-2;",
        options=("AETR", "TAER", "ETAR"),
        option_values={"AETR": "0", "TAER": "1", "ETAR": "2"},
    ),
    ParameterDef(
        "tx_ser_dest",
        "Ser Dest",
        "enum",
        "Serial",
        "Serial destination. CLI: p tx_ser_dest=0-1;",
        options=("Serial", "mBridge"),
        option_values={"Serial": "0", "mBridge": "1"},
    ),
    ParameterDef(
        "tx_power_sw_ch",
        "TX Power CH",
        "enum",
        "OFF",
        "RC channel used to switch TX power. CLI: p tx_power_sw_ch=0,8,9,10,11;",
        options=("OFF", "CH12", "CH13", "CH14", "CH15"),
        option_values={"OFF": "0", "CH12": "8", "CH13": "9", "CH14": "10", "CH15": "11"},
    ),
    ParameterDef(
        "tx_ser_baudrate",
        "TX Baudrate",
        "enum",
        "115200",
        "TX serial baudrate. CLI: p tx_ser_baudrate=0-4;",
        options=("9600", "19200", "38400", "57600", "115200"),
        option_values={"9600": "0", "19200": "1", "38400": "2", "57600": "3", "115200": "4"},
        favorite=True,
    ),
    ParameterDef(
        "tx_snd_radiostat",
        "Snd RadioStat",
        "enum",
        "OFF",
        "Send radio status telemetry. CLI: p tx_snd_radiostat=0-1;",
        options=("OFF", "1Hz"),
        option_values={"OFF": "0", "1Hz": "1"},
    ),
    ParameterDef(
        "TX_MAV_COMPONENT",
        "Mav Component",
        "enum",
        "OFF",
        "MAV component output. CLI: p TX_MAV_COMPONENT=0-1;",
        options=("OFF", "ENABLED"),
        option_values={"OFF": "0", "ENABLED": "1"},
    ),
    ParameterDef(
        "RF_Ortho",
        "RF Ortho",
        "enum",
        "OFF",
        "RF orthogonal mode. CLI: p RF_Ortho=0-3;",
        options=("OFF", "1/3", "2/3", "3/3"),
        option_values={"OFF": "0", "1/3": "1", "2/3": "2", "3/3": "3"},
    ),
    ParameterDef(
        "rx_power",
        "RX Power",
        "int",
        0,
        "RX power level. CLI: p rx_power=0-5;",
        minimum=0,
        maximum=5,
        favorite=True,
        group="RX",
    ),
    ParameterDef(
        "RX_OUT_MODE",
        "RX Out Mode",
        "enum",
        "Sbus",
        "RX output mode. CLI: p RX_OUT_MODE=0-2;",
        options=("Sbus", "CRSF", "Sbus INV"),
        option_values={"Sbus": "0", "CRSF": "1", "Sbus INV": "2"},
        favorite=True,
        group="RX",
    ),
    ParameterDef(
        "rx_ser_baudrate",
        "RX Ser Baudrate",
        "enum",
        "115200",
        "RX serial baudrate. CLI: p rx_ser_baudrate=0-4;",
        options=("9600", "19200", "38400", "57600", "115200"),
        option_values={"9600": "0", "19200": "1", "38400": "2", "57600": "3", "115200": "4"},
        favorite=True,
        group="RX",
    ),
    ParameterDef(
        "RX_SER_LINK_MODE",
        "RX Ser Link Mode",
        "enum",
        "MAVLINK",
        "RX serial link mode. CLI: p RX_SER_LINK_MODE=0-3;",
        options=("Transp", "MAVLINK", "MAVLINKX", "MSPX"),
        option_values={"Transp": "0", "MAVLINK": "1", "MAVLINKX": "2", "MSPX": "3"},
        favorite=True,
        group="RX",
    ),
    ParameterDef(
        "Rx_Snd_RadioStat",
        "RX Snd RadioStat",
        "enum",
        "Off",
        "RX send radio status. CLI: p Rx_Snd_RadioStat=0-2;",
        options=("Off", "Ardu_1", "meth_b"),
        option_values={"Off": "0", "Ardu_1": "1", "meth_b": "2"},
        group="RX",
    ),
    ParameterDef(
        "Rx_Ser_Port",
        "RX Ser Port",
        "enum",
        "Serial",
        "RX serial port. CLI: p Rx_Ser_Port=0-1;",
        options=("Serial", "Can"),
        option_values={"Serial": "0", "Can": "1"},
        group="RX",
    ),
    ParameterDef(
        "RX_SND_RCCHANNEL",
        "RX Snd RcChannel",
        "enum",
        "Off",
        "RX send RC channel message. CLI: p RX_SND_RCCHANNEL=0-2;",
        options=("Off", "rc Override", "rc Channels"),
        option_values={"Off": "0", "rc Override": "1", "rc Channels": "2"},
        group="RX",
    ),
    ParameterDef(
        "RX_OUT_RSSI_CH",
        "RX OUT RSSI CH",
        "enum",
        "Off",
        "RX output RSSI channel. CLI: p RX_OUT_RSSI_CH=0,10,11,12,13;",
        options=("Off", "CH 14", "CH 15", "CH 16", "CH 17"),
        option_values={"Off": "0", "CH 14": "10", "CH 15": "11", "CH 16": "12", "CH 17": "13"},
        group="RX",
    ),
    ParameterDef(
        "RX_OUT_LQ_CH",
        "RX OUT LQ CH",
        "enum",
        "Off",
        "RX output link quality channel. CLI: p RX_OUT_LQ_CH=0,10,11,12,13;",
        options=("Off", "CH 14", "CH 15", "CH 16", "CH 17"),
        option_values={"Off": "0", "CH 14": "10", "CH 15": "11", "CH 16": "12", "CH 17": "13"},
        group="RX",
    ),
    ParameterDef(
        "rx_power_sw_ch",
        "RX Power Sw Ch",
        "enum",
        "Off",
        "RX power switch channel. CLI: p rx_power_sw_ch=0,10,11,12,13;",
        options=("Off", "CH 14", "CH 15", "CH 16", "CH 17"),
        option_values={"Off": "0", "CH 14": "10", "CH 15": "11", "CH 16": "12", "CH 17": "13"},
        group="RX",
    ),
)


PARAMETER_MAP = {param.key: param for param in PARAMETERS}
CANONICAL_KEY_MAP = {param.key.lower(): param.key for param in PARAMETERS}
