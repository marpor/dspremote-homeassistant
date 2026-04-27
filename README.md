# dspremote Home Assistant custom integration

Connects Home Assistant to an existing **dspremote** HTTP/WebSocket API server.

## Install

### Option A: HACS (recommended)

1. In Home Assistant, open **HACS**.
2. Add this repository as a **Custom repository** (type: **Integration**).
3. Install **dspremote** and restart Home Assistant when prompted.
4. Go to **Settings → Devices & Services → Add Integration** and choose **dspremote**.
5. Enter your dspremote server host/port (default port **8787**).
6. Enter **selected field paths** (wildcards allowed, e.g. `/outputs/*/gain`). See [INSTALL.md](INSTALL.md).

### Option B: Manual install

1. Download the release asset **`dspremote-ha.zip`**.
2. Unzip; you should have `custom_components/dspremote/`.
3. Copy that folder into your Home Assistant configuration directory under `custom_components/`.
4. Restart Home Assistant.
5. Add the integration under **Settings → Devices & Services**.

## Behavior

- Discovers metadata from `/v1/discovery` and `/v1/fields`.
- Polls values with `POST /v1/read-prefixes`.
- Optional live updates via WebSocket `/v1/stream`.
- Creates **only** entities for paths you select (supports `*` patterns).
- Platforms: `number`, `select`, `switch`, `sensor`, `button`.

## Development note

Automated tests that run against a local **dspremote** Rust server live in the main **dspremote** repository (`homeassistant/tests/` there), not in this integration-only tree.
