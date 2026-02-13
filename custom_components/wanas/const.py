"""Constants for the Wanas integration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfTime, UnitOfVolumeFlowRate

DOMAIN = "wanas"

DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30

CONF_SLAVE_ID = "slave_id"
CONF_PROTOCOL = "protocol"
CONF_REGISTERS = "registers"

PROTOCOL_RTU_OVER_TCP = "rtu_over_tcp"
PROTOCOL_TCP = "tcp"
PROTOCOL_UDP = "udp"
DEFAULT_PROTOCOL = PROTOCOL_RTU_OVER_TCP

PROTOCOL_OPTIONS = [
    PROTOCOL_RTU_OVER_TCP,
    PROTOCOL_TCP,
    PROTOCOL_UDP,
]


class RegisterDataType(IntEnum):
    """Data type for register values."""

    UINT16 = 0
    INT16 = 1


@dataclass(frozen=True)
class WanasSensorDescription:
    """Describes a Wanas sensor."""

    key: str
    name: str
    address: int
    data_type: RegisterDataType = RegisterDataType.UINT16
    scale: float | None = None
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None


@dataclass(frozen=True)
class WanasSwitchDescription:
    """Describes a Wanas switch."""

    key: str
    name: str
    write_address: int
    verify_address: int
    on_value: int = 1
    off_value: int = 0


SENSOR_DESCRIPTIONS: tuple[WanasSensorDescription, ...] = (
    WanasSensorDescription(
        key="supply_airflow",
        name="Wydatek nawiewu",
        address=0,
        unit=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WanasSensorDescription(
        key="exhaust_airflow",
        name="Wydatek wywiewu",
        address=1,
        unit=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WanasSensorDescription(
        key="supply_fan_speed",
        name="Bieg nawiewu",
        address=2,
    ),
    WanasSensorDescription(
        key="exhaust_fan_speed",
        name="Bieg wywiewu",
        address=3,
    ),
    WanasSensorDescription(
        key="outdoor_temperature",
        name="Temperatura zewnętrzna",
        address=4,
        data_type=RegisterDataType.INT16,
        scale=0.1,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WanasSensorDescription(
        key="exhaust_temperature",
        name="Temperatura wyrzutowa",
        address=5,
        data_type=RegisterDataType.INT16,
        scale=0.1,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WanasSensorDescription(
        key="supply_temperature",
        name="Temperatura nawiewu",
        address=6,
        data_type=RegisterDataType.INT16,
        scale=0.1,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WanasSensorDescription(
        key="indoor_temperature",
        name="Temperatura wewnątrz",
        address=7,
        data_type=RegisterDataType.INT16,
        scale=0.1,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WanasSensorDescription(
        key="current_temperature",
        name="Aktualna temperatura",
        address=29,
        data_type=RegisterDataType.INT16,
        scale=0.1,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WanasSensorDescription(
        key="bypass_state",
        name="Stan bypass",
        address=31,
    ),
    WanasSensorDescription(
        key="humidifier_state",
        name="Stan nawilżacza",
        address=32,
    ),
    WanasSensorDescription(
        key="heater_state",
        name="Stan nagrzewnicy",
        address=33,
    ),
    WanasSensorDescription(
        key="cooler_state",
        name="Stan chłodnicy",
        address=34,
    ),
    WanasSensorDescription(
        key="vacation_mode",
        name="Tryb urlopowy",
        address=35,
    ),
    WanasSensorDescription(
        key="filter_replacement",
        name="Wymiana filtra",
        address=36,
        unit=UnitOfTime.DAYS,
    ),
    WanasSensorDescription(
        key="party_time",
        name="Impreza (czas)",
        address=45,
        data_type=RegisterDataType.INT16,
        scale=0.17,
        unit=UnitOfTime.MINUTES,
    ),
    WanasSensorDescription(
        key="fan_speed_1",
        name="Bieg I",
        address=46,
        data_type=RegisterDataType.INT16,
    ),
    WanasSensorDescription(
        key="fan_speed_3",
        name="Bieg III",
        address=47,
        data_type=RegisterDataType.INT16,
    ),
    WanasSensorDescription(
        key="hood_state",
        name="Okap - stan",
        address=48,
        data_type=RegisterDataType.INT16,
    ),
)

SWITCH_DESCRIPTIONS: tuple[WanasSwitchDescription, ...] = (
    WanasSwitchDescription(
        key="bypass",
        name="Bypass",
        write_address=39,
        verify_address=31,
    ),
    WanasSwitchDescription(
        key="humidifier",
        name="Nawilżacz",
        write_address=40,
        verify_address=32,
    ),
    WanasSwitchDescription(
        key="heater",
        name="Nagrzewnica",
        write_address=41,
        verify_address=33,
    ),
    WanasSwitchDescription(
        key="cooler",
        name="Chłodnica",
        write_address=42,
        verify_address=34,
    ),
    WanasSwitchDescription(
        key="vacation",
        name="Urlop",
        write_address=43,
        verify_address=35,
        on_value=30,
    ),
    WanasSwitchDescription(
        key="fireplace",
        name="Kominek",
        write_address=44,
        verify_address=44,
        on_value=180,
    ),
    WanasSwitchDescription(
        key="party",
        name="Impreza",
        write_address=45,
        verify_address=45,
        on_value=720,
    ),
)

def get_default_registers() -> dict[str, int]:
    """Build default register address mapping from descriptions."""
    regs: dict[str, int] = {}
    for desc in SENSOR_DESCRIPTIONS:
        regs[f"{desc.key}_address"] = desc.address
    for desc in SWITCH_DESCRIPTIONS:
        regs[f"{desc.key}_write_address"] = desc.write_address
        regs[f"{desc.key}_verify_address"] = desc.verify_address
    return regs
