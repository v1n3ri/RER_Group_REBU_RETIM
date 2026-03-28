"""Constants for the Retim Timisoara integration."""
import logging
from homeassistant.const import Platform
DOMAIN = "RER_Group"
PLATFORMS = [Platform.SENSOR]
CONF_DOMAIN = "domain_url"

SUPPORTED_DOMAINS = {
    "RETIM": "https://cp.retim.ro/api",
    "REBU": "https://cp.rebu.ro/api",
    "RER Vest": "https://cp.rervest.ro/api",
    "RER Sud": "https://cp.rervest.ro/api",
    "RER Braila": "https://cp.rerbraila.ro/api",
    "RER Galati": "https://cp.rergalati.ro/api",
    "RER Data": "https://cp.rervest.ro/api",
    "RER Group": "https://cp.rervest.ro/api"
}

# Configuration keys
CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# Attribution to show in the UI
ATTRIBUTION = "Data provided by RER_Group"

# Refresh interval
# This can be used in __init__.py for the coordinator
SCAN_INTERVAL_HOURS = 1

# Logger
_LOGGER = logging.getLogger(__package__)