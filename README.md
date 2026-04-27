# dspremote

Custom integration for [Home Assistant](https://www.home-assistant.io/). Connects HA to an existing **dspremote** connected device over its HTTP/WebSocket API (discovery, reads, writes, actions).

## Requirements

- **Home Assistant** 2024.1 or newer (see `hacs.json`).
- A reachable **dspremote** HTTP API (host/IP and port).

## Installation

### HACS (recommended)

1. In Home Assistant, open **HACS**.
2. Go to **Integrations** (or **Explore & download**), search for **dspremote**, open it, then **Download** / **Install**. Restart Home Assistant when prompted.

   If HACS says the repository **already exists in the store**, it is listed as a default integration—**do not** add it under **Custom repositories**; installing from **Integrations** as above is enough.

3. Go to **Settings → Devices & services → Add integration** and select **dspremote**.
4. Enter the dspremote **host** (or IP), **port**, and **selected field paths** (see [Configuration](#configuration)).

**Fork or unlisted copy only:** use the HACS menu (⋮) → **Custom repositories**, add your Git URL with category **Integration**. You cannot add the default store URL again; HACS will reject it with “exists in the store”.

### Manual install

1. Copy this repository (e.g. **Code → Download ZIP** on GitHub, then unzip—or `git clone`).
2. Copy the folder `custom_components/dspremote` into your Home Assistant configuration directory so you have:

   `config/custom_components/dspremote/` (alongside `configuration.yaml`).

3. Confirm `manifest.json` exists under `custom_components/dspremote/`.
4. **Restart Home Assistant**.
5. **Settings → Devices & services → Add integration** → **dspremote**, then enter host, port, and field paths as in the HACS flow above.

## Configuration

During setup (and later under **Configure** on the integration entry), you choose which API paths become entities. Use **wildcards** (`*`) where the API supports them.

**Examples**

- `/outputs/*/gain` → number (gain sliders)
- `/outputs/*/mute` → switches
- `/outputs/*/high_pass/type` → select

Pick only what you need—each path (or pattern) can create multiple entities. You can **change paths anytime** in the integration options.

## Features

- Loads schema from `/v1/discovery` and `/v1/fields`.
- Refreshes values with `POST /v1/read-prefixes`.
- Optional live updates via WebSocket `/v1/stream`.
- Entities **only** for paths you select (no full-device flood).
- Platforms: `number`, `select`, `switch`, `sensor`, `button`.

## Troubleshooting

**Integration does not appear under “Add integration”**

- Path must be exactly `custom_components/dspremote` with `manifest.json` inside it.
- Restart Home Assistant after copying files.

**Integration added but no entities**

- Confirm the dspremote server is running and reachable from Home Assistant (host/port/firewall).
- Add at least one valid path or pattern; check dspremote discovery for real paths.

**Changes to files not picked up**

- Restart Home Assistant after replacing integration files.

## Updating

- **HACS:** open the integration in HACS → update, then restart Home Assistant.
- **Manual:** replace `custom_components/dspremote` with the new version and restart.

## Development

Automated tests that exercise this integration against a local dspremote server live in the main **dspremote** repository under `homeassistant/tests/` (not in this repo).
