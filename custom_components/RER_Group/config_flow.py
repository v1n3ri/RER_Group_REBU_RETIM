import logging
import voluptuous as vol
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import RetimAPI
from .const import DOMAIN, CONF_DOMAIN, CONF_EMAIL, CONF_PASSWORD, SUPPORTED_DOMAINS

_LOGGER = logging.getLogger(__name__)

# This is the schema for the data we want to collect
DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_DOMAIN): SelectSelector(
        SelectSelectorConfig(
            options=[{"value": v, "label": k} for k, v in SUPPORTED_DOMAINS.items()],
            mode=SelectSelectorMode.DROPDOWN,
        )
    ),
    vol.Required(CONF_EMAIL): str,
    vol.Required(CONF_PASSWORD): str,
})

class RetimConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_reauth(self, user_data):
        """Handle re-auth if credentials expire."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # 1. Check if this account is already configured to prevent duplicates
            await self.async_set_unique_id(user_input[CONF_EMAIL].lower())
            self._abort_if_unique_id_configured()

            # 2. Validate credentials using the API class we wrote
            session = async_get_clientsession(self.hass)
            api = RetimAPI(user_input[CONF_EMAIL], user_input[CONF_PASSWORD], session, user_input[CONF_DOMAIN] # Pass the URL selected in the dropdown
)
            
            try:
                login_success = await api.login()
                if login_success:
                    # Success! Create the integration entry
                    return self.async_create_entry(
                        title=user_input[CONF_EMAIL], 
                        data=user_input
                    )
                else:
                    errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception during Retim login")
                errors["base"] = "cannot_connect"

        # 3. Show the form (either for the first time or with error messages)
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )