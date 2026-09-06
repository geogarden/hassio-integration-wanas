# Wanas Rekuperator — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)

Full control of your **Wanas recuperator** directly from Home Assistant via **Modbus** (TCP / UDP / RTU over TCP).

Monitor temperatures, airflow, fan speeds, filter status — and toggle bypass, heater, cooler, humidifier, vacation mode, fireplace, and party mode — all from your dashboard.

![Wanas-pip-boy](https://github.com/jrx-code/hassio-integration-wanas/blob/main/images/pip-boy.jpg)
---

## Features

- **34 entities** built on the manufacturer register table: airflow, five temperatures, fan
  speeds, filter countdown, the six status flags, the four digital inputs, and writable
  controls for bypass, GWC, humidifier, heater, cooler, the timed functions and the fan
  power setpoints
- **Polish and English** entity and config-flow names, picked from the Home Assistant language
- **Asks which optional modules the unit has** (heater, cooler, humidifier) and skips their
  entities entirely when they are not fitted; changeable afterwards without re-adding
- **Three protocols**: RTU over TCP (default), plain TCP, UDP
- **Advanced mode** lets you retarget every Modbus register and rename any entity
- **Short reads**: registers are grouped into blocks of at most 16, because RS485 gateways
  stop answering long requests and one unanswered read takes down every entity
- **Auto-reconnect** on a dropped connection, and writes rejected by the device surface as a
  Home Assistant error naming the register and the value

## Installation

### HACS (recommended)

1. Open HACS → **Integrations** → three-dot menu → **Custom repositories**
2. Add this repository URL, category: **Integration**
3. Search for **Wanas** and install
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/wanas` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Wanas**
3. Enter connection details:

   | Field | Default | Description |
   |-------|---------|-------------|
   | Host | — | IP address of the recuperator |
   | Port | `502` | Modbus port |
   | Slave ID | `1` | Modbus device ID |
   | Protocol | `rtu_over_tcp` | `rtu_over_tcp`, `tcp`, or `udp` |

4. Tick only the optional modules the unit actually has. The controller answers on the
   heater, cooler and humidifier registers whether or not the modules are fitted, so their
   presence cannot be probed. Clearing one means its entities are never created:

   | Module | Entities skipped |
   |---|---|
   | Heater | `binary_sensor` heater state, `switch` heater, `number` heater days |
   | Cooler | `binary_sensor` cooler state, `switch` cooler, `number` cooler days |
   | Humidifier | `binary_sensor` humidifier state, `switch` humidifier |

5. The integration will test the connection before saving

Answers can be corrected later under **Configure** on the integration card. Turning a module
off removes its entities from the registry rather than leaving them unavailable.

### Advanced: Custom Register Addresses

If your device uses non-standard register mapping:

1. Enable **Advanced Mode** in your Home Assistant user profile
2. Add the integration — after successful connection test, a second step appears
3. Modify any register address (all fields are pre-filled with defaults)

This is useful for custom firmware or alternative Wanas device variants.

## Entities

34 entities: 11 sensors, 10 binary sensors, 5 switches and 8 numbers. Names are translated,
so the Polish column is what a Polish instance displays.

### Sensors

| Register | English | Polish |
|---|---|---|
| 0 | Supply airflow | Wydatek nawiewu |
| 1 | Exhaust airflow | Wydatek wywiewu |
| 2 | Supply fan speed | Bieg nawiewu |
| 3 | Exhaust fan speed | Bieg wywiewu |
| 4 | Outdoor temperature | Temperatura zewnętrzna |
| 5 | Exhaust temperature | Temperatura wyrzutowa |
| 6 | Supply temperature | Temperatura nawiewu |
| 7 | Room temperature | Temperatura pomieszczenia |
| 29 | Extra probe temperature | Temperatura dodatkowa |
| 36 | Filter replacement | Wymiana filtra |
| 37 | System errors | Błędy systemu |

### Binary sensors

Registers 46 to 49 are the controller's read-only digital inputs.

| Register | English | Polish |
|---|---|---|
| 30 | Ground heat exchanger | Stan GWC |
| 31 | Bypass | Stan bypassu |
| 32 | Humidifier | Stan nawilżacza |
| 33 | Heater | Stan nagrzewnicy |
| 34 | Cooler | Stan chłodnicy |
| 35 | Vacation mode | Tryb urlopowy |
| 46 | Speed 1 input | Wejście biegu 1 |
| 47 | Speed 3 input | Wejście biegu 3 |
| 48 | Hood input | Wejście okapu |
| 49 | Fire alarm input | Wejście przeciwpożarowe |

### Switches

| Write → verify | English | Polish |
|---|---|---|
| 38 → 30 | Ground heat exchanger | GWC |
| 39 → 31 | Bypass | Bypass |
| 40 → 32 | Humidifier | Nawilżacz |
| 41 → 33 | Heater | Nagrzewnica |
| 42 → 34 | Cooler | Chłodnica |

### Numbers

| Register | Range | Unit | English | Polish |
|---|---|---|---|---|
| 41 | 0 to 60 | dni | Heater days | Nagrzewnica (dni) |
| 42 | 0 to 60 | dni | Cooler days | Chłodnica (dni) |
| 43 | 0 to 30 | dni | Vacation days | Tryb urlopowy (dni) |
| 44 | 0 to 180 | s | Fireplace | Funkcja kominek |
| 45 | 0 to 720 | min | Party | Funkcja impreza |
| 52 | 1 to 100 | % | Fan power 1 | Moc biegu 1 |
| 53 | 1 to 100 | % | Fan power 2 | Moc biegu 2 |
| 54 | 1 to 100 | % | Fan power 3 | Moc biegu 3 |

Registers 41 and 42 are day counters on the device. The switches write 1, arming them
for a day; the matching Heater days / Cooler days numbers give the full 0 to 60 range.

## Requirements

- **Home Assistant 2024.6 or newer.** The integration stores its coordinator in
  `ConfigEntry.runtime_data` and the advanced step uses `data_entry_flow.section`; neither
  exists in earlier releases.
- **pymodbus 3.10 or newer** (installed automatically). Release 3.10.0 renamed the client
  parameter `slave=` to `device_id=`, which is what this code calls.
- Network access to the recuperator over Modbus TCP or UDP.

## Languages

Entity names and the config flow are translated into **English** and **Polish**; Home
Assistant picks the language from the instance setting. Renaming an entity in the advanced
register step overrides the translation for that entity only.

Adding a language means one file in `custom_components/wanas/translations/` with the same
keys as `strings.json`. The `entity` block carries all 34 entity names.

## Troubleshooting

**"Cannot connect to the device"**
- Verify the IP address is reachable (`ping <host>`)
- Check Modbus port (default 502) is not blocked by firewall
- Confirm Slave ID matches device configuration
- Try switching protocol (some devices prefer plain TCP over RTU)

**Sensors show "Unknown"**
- The device may not support all registers — this is normal for some variants
- In Advanced Mode, you can remap registers to match your device

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**JI ENGINEERING**

---

<sub>Built with Modbus and determination. Działa jak złoto.</sub>
