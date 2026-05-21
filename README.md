# Sunology Integration for Home Assistant

![Logo Sunology](sunology.jpg)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![install_badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.sunology.total)](https://analytics.home-assistant.io/)

Our website: https://www.sunology.eu

## Description
This component offers you a way to add PV System and EMS to your favorite SmartHome device.

You need to have an Home Assistant and a Sunology STREAM Connect

## Technical add the logo for custom integration:
1. Open a PR on this repo like this one to register the integration
    https://github.com/home-assistant/wheels-custom-integrations/pull/62
2. Open a PR on this repo to add the listed logo
    https://github.com/home-assistant/brands/pull/1643

## Installation
### Flow
- Just follow the integration config steps.

## Features

- **Monitoring**: Monitor the status and performance of your Sunology device.
- **Automation**: Create automations based on the data from your Sunology device.

## Installation

1. **Using HACS (Recommended)**:
   - Ensure you have [HACS](https://hacs.xyz/) installed.
   - Go to HACS > Integrations > Explore & Add Repositories.
   - Add this repository and install the Sunology integration.
   - Restart Home Assistant.

2. **Manual Installation**:
   - Copy the `sunology` directory to your `custom_components` directory.
   - Restart Home Assistant.

## Configuration

1. Go to **Configuration** > **Integrations** > **Add Integration**.
2. Search for "Sunology" and select it.
3. Follow the prompts to configure your Sunology device:
   * Enter the IP address or hostname of your STREAM Connect device.
   * Enter the network port of your STREAM Connect device.
   * *(Optional)* Enter your Sunology account email and password — the same
     credentials you use in the official mobile app. Leave blank for
     read-only mode.

To change your Sunology credentials later (for example after a password
reset), open **Settings** > **Devices & Services** > **Sunology** >
**Configure**. No need to remove and re-add the integration.

## How writes work

When Sunology account credentials are provided, write operations to STOREY
batteries are routed through Sunology's cloud API at
`backend-mobile.stream.sunology.eu`. This is the same path the official
mobile app uses — the local WebSocket on the STREAM Connect gateway only
accepts a small whitelist of write commands and silently rejects writes to
STOREY-level configuration.

After a successful write, the gateway echoes the new state on its local
WebSocket within roughly 30 seconds, so Home Assistant entity state stays
consistent with what the mobile app shows. The cloud session cookie is
cached (~400 days) and reused across restarts; re-authentication happens
automatically on expiry.

If credentials are not provided, the integration runs in read-only mode and
the write-capable entities (`number.minsoc_*`, `datetime.pause_until_*`,
`button.*_pause_*`) are simply not created.

## Logging

To enable detailed logging for troubleshooting, you can configure the logger in your `configuration.yaml` file:
