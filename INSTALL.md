# Install dspremote in Home Assistant (Simple Guide)

This guide explains how to install the `dspremote` integration in Home Assistant.

If you are not technical, use **Option 1 (HACS)**.

---

## Before you start

You need:

- A running Home Assistant instance
- A running `dspremote` server (for example on your network)
- The server address and port (example: `192.168.1.50:8787`)

---

## Option 1 (Recommended): Install with HACS

This is the easiest method and gives update notifications.

1. Open Home Assistant in your browser.
2. Open **HACS**.
3. Add this repository as a **Custom repository** of type **Integration**.
4. Search for **dspremote** in HACS and install it.
5. Restart Home Assistant when prompted.
6. Go to **Settings -> Devices & Services**.
7. Click **Add Integration** and select **dspremote**.
8. Enter:
   - Host/IP of your `dspremote` server
   - Port (usually `8787`)
   - The fields you want (for example `/outputs/*/gain` and `/outputs/*/mute`)

Done. Entities should appear after setup.

---

## Option 2: Manual install (without HACS)

Use this if you do not want to use HACS.

1. Download the latest release zip: `dspremote-ha.zip`.
2. Unzip the file on your computer.
3. You should get a folder structure like:
   - `custom_components/dspremote`
4. Copy the `dspremote` folder into your Home Assistant config under:
   - `custom_components`
   - Final location should be: `custom_components/dspremote`
5. Restart Home Assistant.
6. Go to **Settings -> Devices & Services**.
7. Click **Add Integration** and select **dspremote**.
8. Enter your server host/port and selected field paths.

---

## How to choose field paths

To avoid too many entities, choose only the fields you need.

Examples:

- `/outputs/*/gain` (output gain sliders)
- `/outputs/*/mute` (output mute switches)
- `/outputs/*/high_pass/type` (filter type selects)

You can edit this later in integration options.

---

## Troubleshooting

### I cannot see the integration in "Add Integration"

- Confirm folder path is exactly: `custom_components/dspremote`
- Confirm `manifest.json` exists inside that folder
- Restart Home Assistant again

### Integration is added but no entities appear

- Check your `dspremote` server is running and reachable
- Check host/port are correct
- Add at least one valid selected field path

### I changed files but Home Assistant did not update

- Restart Home Assistant after updating files

---

## Updating later

- HACS install: update from HACS and restart Home Assistant.
- Manual install: replace `custom_components/dspremote` with the newer version, then restart.

