from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RetimAPI
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = RetimAPI(
        entry.data[CONF_EMAIL], 
        entry.data[CONF_PASSWORD], 
        session, 
        entry.data[CONF_DOMAIN]
    )

    async def async_update_data():
        try:
            # The API class now handles 401/Login internally
            return await api.get_data()
        except Exception as err:
            raise UpdateFailed(f"API Error: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"RER Group ({entry.data[CONF_EMAIL]})",
        update_method=async_update_data,
        update_interval=timedelta(hours=6),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True