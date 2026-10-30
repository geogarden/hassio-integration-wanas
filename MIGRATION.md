# Coexistence: geogarden/hassio-integration-wanas as the "Wanas (Community)" edition

Status date: 2026-10-22. Source of truth for the live set: prod HA entity registry
(`core.entity_registry`, read 2026-10-20) and micpub `0.2.1` translations.

## Decision (2026-10-22): coexist, do not retire

Earlier plan was to retire this integration and move to `micpub/homeassistant-wanas` after
upstreaming our extras. Dropped, because micpub's reviews gated our key feature on the vendor:
on PR #9 (heat recovery) he wrote "i will have to ask the company if they want to show such
sensors", and he wants #8 and #12 reworked to his design. We do not control that timeline.

Instead this integration continues as a parallel **community edition** under its own domain
`wanas_community` (renamed from `wanas` in v4.0.0, 2026-10-22). Two integrations can now be
installed side by side, same pattern as core `tuya` + `localtuya` or `xiaomi_miio` +
`xiaomi_miot`. micpub stays the default/vendor-blessed one; this one carries the extras
(heat recovery, clock-sync button, writable mode switches, the `switch.wanas_chlodnica`
logic the TV-room automations use).

The `hacs/default#11501` submission (withdrawn 2026-10-19 over the `wanas` domain clash) can
be resubmitted under the distinct `wanas_community` domain, which no longer collides.

Upstream PRs stay **open** as goodwill; micpub is free to take any of them. Their ideas are
tracked here as issues #24 (diagnostics as modbus operation history + connection-status
attributes, under coordinator lock), #25 (opt-in auto-sync clock switch), #26 (skip-unsupported
logic must cover the weekly schedule read).

## Cutover on prod HA — still gated

The `wanas` → `wanas_community` domain rename orphans all 64 live entities exactly as a move
to micpub would (unique_ids do not carry across a domain change), so the prod entity remap is
the same scale of work. It is **not** done yet: it runs only after an explicit go, on VM 103
first, via `rest`/reload rather than a restart.

## This is a rewrite, not a rename

1. **No `unique_id` overlap.** Ours: `192.168.18.74:502:1_<key>`. micpub: `wanas_<device_id>_<key>`
   with `has_entity_name=True`. None of the 64 live entities carry over; HA creates a fresh set
   and orphans the old ones. Every reference must be remapped.
2. **Different control model.** Our writable `switch.*` for cooler/heater/vacation/party/fireplace
   are **mode numbers** in micpub (`number.cooler_mode`, `number.heater_mode`, `number.vacation_mode`,
   `number.party_mode`, `number.fireplace_mode`); cooler/heater also exist as read-only
   `binary_sensor`. `switch.wanas_chlodnica` (48 references, the writers'-room AC logic in
   `hvac/`) has no switch equivalent — that automation needs logic rework, not a rename.
3. **Features implemented differently (not missing).** The controller clock IS in micpub as
   writable `date.device_date` + `time.device_time` (reg 50/51, same encoding) — our combined
   `controller_clock` sensor is redundant; only our `sync_clock` button has no equivalent
   (proposed upstream as micpub PR #12). The weekly schedule IS in micpub: full read
   (`sensor.weekly_schedule` / `weekly_schedule_day`) + edit service `update_weekly_schedule_zone`
   + card `wanas-vent-card`; our editable `time.period_*_until` / `select.program_day` are a
   different UX that conflicts with micpub's day-restore logic, so they are not upstreamed.
   The cooler/heater/vacation/party/fireplace registers (41-45) are days/seconds/minutes
   counters, so micpub's `number.*_mode` is more correct than our on/off `switch.*`; we do not
   upstream switches.

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
| controller_clock (sensor) | sensor.wanas_rekuperator_zegar_sterownika | date.device_date + time.device_time (reg 50/51) | ~ clock exists, split read/write |
| sync_clock (button) | button.wanas_rekuperator_ustaw_zegar... | (micpub PR #12, pending) | ✗ pending #12 |
| period_1..4_until (time) | time.rekuperator_wanas_..._przedzial_* | service update_weekly_schedule_zone | ~ service-based, no editable entity |
| program_day (select) | select.wanas_rekuperator_dzien_programu | sensor.weekly_schedule_day + service | ~ service-based, day not UI-settable |
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
- `feature/sync-clock-button` → PR #12 (OPEN, 2026-10-20) — the one genuinely missing feature.
- Deliberately NOT upstreamed (would be rejected or regressive): on/off `switch.*` for
  cooler/heater/vacation/party/fireplace (micpub's `number.*_mode` is correct for the
  days/seconds counters); editable schedule entities (conflict with micpub's day-restore);
  the richer two-card frontend (micpub ships his own card). These become micpub equivalents
  at migration, not upstream PRs.
