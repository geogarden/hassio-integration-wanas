# Migration: jrx-code/hassio-integration-wanas → micpub/homeassistant-wanas

Status date: 2026-10-20. Source of truth for the live set: prod HA entity registry
(`core.entity_registry`, read 2026-10-20) and micpub `0.2.1` translations.

## Why

`micpub/homeassistant-wanas` is in the HACS **default** store and owns the same `wanas`
domain, so the two integrations cannot be installed side by side. Our hacs/default PR
(`hacs/default#11501`) was withdrawn 2026-10-19. The plan is to retire this custom
integration and run micpub's, after pushing our extra features upstream.

## HOLD — do not cut over yet

Cutover on prod HA and archiving this repo are **blocked** until micpub merges our open
PRs and ships a release that contains them:

- `micpub/homeassistant-wanas#9` — heat recovery sensors (power / efficiency / energy). **OPEN.**
- `micpub/homeassistant-wanas#8` — skip unsupported registers instead of failing the poll. **OPEN.**
- `micpub/homeassistant-wanas#10` — config entry diagnostics. **MERGED 2026-10-20** (not yet in a tagged release; latest tag is 0.2.1, 2026-08-19).

Cutting over to released 0.2.1 now would drop heat recovery (the feature we are upstreaming),
so it waits for a release that includes #9.

## This is a rewrite, not a rename

1. **No `unique_id` overlap.** Ours: `192.168.18.74:502:1_<key>`. micpub: `wanas_<device_id>_<key>`
   with `has_entity_name=True`. None of the 64 live entities carry over; HA creates a fresh set
   and orphans the old ones. Every reference must be remapped.
2. **Different control model.** Our writable `switch.*` for cooler/heater/vacation/party/fireplace
   are **mode numbers** in micpub (`number.cooler_mode`, `number.heater_mode`, `number.vacation_mode`,
   `number.party_mode`, `number.fireplace_mode`); cooler/heater also exist as read-only
   `binary_sensor`. `switch.wanas_chlodnica` (48 references, the writers'-room AC logic in
   `hvac/`) has no switch equivalent — that automation needs logic rework, not a rename.
3. **Features micpub 0.2.1 lacks entirely**: `controller_clock` sensor, `sync_clock` button,
   our schedule-editing entities (`time.period_*_until`, `select.program_day`). micpub does the
   weekly schedule differently: `sensor.weekly_schedule` / `weekly_schedule_day` + service
   `update_weekly_schedule_zone` + card `wanas-vent-card`.

## Entity crosswalk (by internal key)

Our key (uid suffix) → micpub 0.2.1 key. `=` clean map, `~` semantic but different platform/model,
`✗` no equivalent in 0.2.1.

| Our key | Our live entity_id | micpub key | Map |
|---|---|---|---|
| supply_temperature | sensor.wanas_temperatura_nawiewu | sensor.supply_temp | = |
| exhaust_temperature | sensor.wanas_temperatura_wyrzutowa | sensor.exhaust_temp | = |
| outdoor_temperature | sensor.wanas_temperatura_zewnetrzna | sensor.outdoor_temp | = |
| indoor_temperature | sensor.wanas_temperatura_wewnatrz | sensor.extract_temp | ~ (verify: extract vs indoor) |
| current_temperature | sensor.wanas_temperatura_chlodnicy | sensor.extra_temp | ~ (verify) |
| supply_fan_speed | sensor.wanas_bieg_nawiewu | sensor.supply_fan_speed | = |
| exhaust_fan_speed | sensor.wanas_bieg_wywiewu | sensor.extract_fan_speed | ~ |
| supply_airflow | sensor.wanas_wydatek_nawiewu | sensor.supply_airflow | = |
| exhaust_airflow | sensor.wanas_wydatek_wywiewu | sensor.extract_airflow | ~ |
| filter_replacement | sensor.wanas_wymiana_filtra | sensor.filter_wear_status | ~ |
| cooler (switch) | switch.wanas_chlodnica | number.cooler_mode + binary_sensor.cooler | ✗ model change (48 refs) |
| heater (switch) | switch.wanas_nagrzewnica | number.heater_mode + binary_sensor.heater | ✗ model change |
| humidifier (switch) | switch.wanas_nawilzacz | switch.humidifier_mode | ~ |
| bypass (switch) | switch.wanas_bypass | switch.summer_bypass_mode | ~ |
| gwc (switch) | switch.wanas_rekuperator_gwc | switch.ghe_mode | ~ (GWC = ghe) |
| vacation_switch (switch) | switch.wanas_urlop | number.vacation_mode | ✗ model change (3 refs) |
| party_switch (switch) | switch.wanas_impreza | number.party_mode | ✗ model change |
| fireplace_switch (switch) | switch.wanas_kominek | number.fireplace_mode | ✗ model change |
| zone_1..5_speed (number) | number.wanas_rekuperator_bieg_strefy_* | speed1/2/3_airflow / manual_fan_speed | ✗ zones differ |
| controller_clock (sensor) | sensor.wanas_rekuperator_zegar_sterownika | — | ✗ none |
| sync_clock (button) | button.wanas_rekuperator_ustaw_zegar... | — | ✗ none |
| period_1..4_until (time) | time.rekuperator_wanas_..._przedzial_* | — | ✗ none (service-based) |
| program_day (select) | select.wanas_rekuperator_dzien_programu | — | ✗ none |
| schedule_summary / current_period | sensor.rekuperator_wanas_... | weekly_schedule / weekly_schedule_day | ~ different |
| heat_recovery_power/efficiency/energy | sensor.rekuperator_wanas_... | (micpub#9, not released) | ✗ pending |

## Remap targets (repo, deploy-side)

Active references to our entity_ids (prod registry + repo grep 2026-10-20):

- `hassio/automatyzacje/hvac/` — `automations/klimatyzacja.yaml`, `automations/klimatyzacja_pisarze.yaml`,
  `packages/klimatyzacja.yaml`: `switch.wanas_chlodnica` (×48), `sensor.wanas_temperatura_nawiewu`,
  `sensor.wanas_temperatura_zewnetrzna`. **Needs cooler switch→number.cooler_mode rework.**
- `hassio/automatyzacje/pogoda/automations/pogoda.yaml` — `sensor.wanas_temperatura_zewnetrzna`.
- `hassio/automatyzacje/home-energy-hub/` — influx/telemetry packages referencing wanas sensors.
- `hassio/hassio-ventilation-card/wanas_card_code.yaml` — replaced by micpub `wanas-vent-card`.
- Live-only (not in repo): any Lovelace dashboards referencing `*.wanas_*` — enumerate from
  `core.lovelace*` / storage before cutover.

## Cutover procedure (when the release lands)

1. Confirm micpub release contains #9 (+ #8). Update this map with the real generated entity_ids
   by first installing micpub on **VM 103** pointed at the **mock** (`services/modbus-server`,
   LXC 419, RTU-over-TCP `192.168.19.49:5503`), **never the real unit** at `192.168.18.74:502`:
   its Waveshare gateway runs transparent and broadcasts RS485 to every TCP socket, so a second
   Modbus master corrupts prod readings.
2. Branch the remap in `hassio/automatyzacje/*` and the dashboards; rewrite cooler/heater/vacation/
   party/fireplace from switch to number.*_mode.
3. VM 103: remove this custom integration, install micpub via HACS, reconfigure, restart, verify.
4. Prod (explicit go required): same sequence; `ha core check` then `/ha restart`.
5. Archive this repo (GitHub archived + Forgejo) with a README note pointing at micpub.

## Our upstreaming branches (fork jrx-code/homeassistant-wanas)

- `feature/heat-recovery` → PR #9 (OPEN, rebased on upstream/main 2026-10-20).
- `fix/unsupported-registers` → PR #8 (OPEN, rebased 2026-10-20).
- `feature/diagnostics` → PR #10 (MERGED).
- Not yet upstreamed (would reduce the ✗ list above): controller clock + sync button, the
  schedule-editing entities, the richer two-card frontend.
