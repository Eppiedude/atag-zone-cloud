# ATAG Zone Cloud

ATAG Zone Cloud is an unofficial, read-only Home Assistant custom integration for monitoring ATAG Zone systems through the ATAG Zone cloud API. It creates entities only for menu items actually returned by the configured installation and polls every 60 seconds.

## Why a cloud integration?

Some older or legacy ATAG integrations use a local interface on TCP port 10000 with discovery on UDP port 11000. On the ATAG ONE system used during development (firmware 142.00.76), TCP/10000 refused connections and UDP/11000 did not provide a usable legacy interface. Docker isolation was excluded because Home Assistant used host networking. The thermostat's local HomeKit support remained available, but exposed substantially less monitoring data.

This integration therefore targets systems with access to the ATAG Zone cloud service, including installations where that legacy local interface is unavailable. A local integration may remain preferable wherever the local API works. These observations do **not** imply that every ATAG model or firmware lacks a local API.

## Read-only by design

Version 1 performs reads only. It cannot change heating, domestic hot water, zone, or heat-pump settings. Existing thermostat control, including HomeKit-based control, remains independent.

## Available entities

The curated registry includes outdoor and room temperatures, relative humidity, heat request by zone, domestic-hot-water temperature and setpoint, signal level, heat-pump mode and temperatures, central-heating flow temperature and target, plus optional hydraulic-scheme, quiet-mode, and buffer status diagnostics.

Capabilities vary between installations. Only values returned by your system become entities; absent zones and unsupported features are silently omitted.

## Installation with HACS

1. In HACS, open **Integrations**, select the menu, then **Custom repositories**.
2. Add https://github.com/Eppiedude/atag-zone-cloud.git with category **Integration**.
3. Search for **ATAG Zone Cloud**, download it, and restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and select **ATAG Zone Cloud**.

## Configuration

The config flow asks for your ATAG account e-mail/username, password, and system/plant ID. Automatic system discovery is not included because no discovery endpoint has been verified.

To find the system/plant ID:

Sign in to the ATAG Zone web portal.
Open your installation.
Look at the browser address bar.
The system/plant ID is the value shown after /Plant/Index/.

Example:
https://www.atagzone.remotethermo.com/Plant/Index/YOUR_SYSTEM_ID

Enter only the YOUR_SYSTEM_ID part in the Home Assistant config flow without the "?" in the end.

Credentials and the system ID are used only at runtime. Never post them in bug reports.

Example values in documentation and tests are synthetic, such as `user@example.com` and `YOUR_SYSTEM_ID`.

## API provenance

ATAG was contacted regarding technical/API documentation but declined to provide it because the documentation is considered confidential/proprietary. This integration was therefore developed independently based on behavior observable through the owner's own ATAG system and account.

## Disclaimer

This is an unofficial community integration and is not affiliated with or endorsed by ATAG. The cloud API is undocumented and may change without notice.

## Development

Run `pytest`. Tests use synthetic mocked responses and never contact the live API. Run `ruff check .` for linting.

## License

[MIT](LICENSE)
