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
   - Enter the IP address or hostname of your STREAM Connect device.
   - Enter the network port of your STREAM Connect device.

## Logging

To enable detailed logging for troubleshooting, you can configure the logger in your `configuration.yaml` file:

