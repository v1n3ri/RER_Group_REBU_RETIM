from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RetimAPI
from .const import CONF_EMAIL, CONF_PASSWORD, CONF_DOMAIN # Ensure CONF_DOMAIN is imported

_LOGGER = logging.getLogger(__name__)

# List the platforms you want to support (just sensors for now)
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Retim Timisoara from a config entry."""
    session = async_get_clientsession(hass)
    api = RetimAPI(
    entry.data[CONF_EMAIL], 
    entry.data[CONF_PASSWORD], 
    session, 
    entry.data[CONF_DOMAIN] # Pass the selected URL
)

    async def async_update_data():
        """Fetch data from Retim API."""
        try:
            # This calls the fetch_data method we defined in api.py
            return await api.get_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    # The Coordinator handles the 'heartbeat' of your integration
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Retim Data",
        update_method=async_update_data,
        # We check every 6 hours; trash schedules and bills don't change fast
        update_interval=timedelta(hours=6),
    )

    # Fetch initial data so the sensors aren't empty on startup
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator so sensors can access it
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Set up the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok