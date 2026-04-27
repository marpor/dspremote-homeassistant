# dspremote

Custom integration for [Home Assistant](https://www.home-assistant.io/). Connects HA to an existing **dspremote** connected device over its HTTP/WebSocket API (discovery, reads, writes, actions).

## Requirements

- **Home Assistant** 2024.1 or newer (see `hacs.json`).
- A reachable **dspremote** HTTP API (host/IP and port).

## Installation

### HACS (recommended)

1. In Home Assistant, open **HACS**.
2. Open the menu (⋮) → **Custom repositories**.
3. Add this repository URL, category **Integration**, then **Add**.
4. In **HACS → Integrations**, open **dspremote** (or use **Explore & download** and search for **dspremote**).
5. Choose **Download** / **Install** and complete the flow; **restart Home Assistant** when prompted.
6. Go to **Settings → Devices & services → Add integration** and select **dspremote**.
7. Enter the dspremote **host** (or IP), **port**, and **selected field paths** (see [Configuration](#configuration)).

### Manual install

1. Copy this repository (e.g. **Code → Download ZIP** on GitHub, then unzip—or `git clone`).
2. Copy the folder `custom_components/dspremote` into your Home Assistant configuration directory so you have:

   `config/custom_components/dspremote/` (alongside `configuration.yaml`).

3. Confirm `manifest.json` exists under `custom_components/dspremote/`.
4. **Restart Home Assistant**.
5. **Settings → Devices & services → Add integration** → **dspremote**, then enter host, port, and field paths as in HACS step 7.

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
