""" Sunology config flow """

import logging
from homeassistant import config_entries
import voluptuous as vol
from .const import CONF_GATEWAY_IP, DOMAIN, PACKAGE_NAME


_LOGGER = logging.getLogger(PACKAGE_NAME)

@config_entries.HANDLERS.register(DOMAIN)
class SunologyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Sunology config flow """
    
    async def async_step_user(self, user_input=None): #pylint: disable=W0613
        """ handle info to help to configure Sunology """

        if self._async_current_entries():
            return self.async_abort(reason="one_instance_allowed")

        return self.async_show_form(step_id='sunology_setup', data_schema=vol.Schema({
            vol.Required(CONF_GATEWAY_IP): vol.All(str, vol.Length(min=3)),
        }))

    async def async_step_import(self, user_input=None): #pylint: disable=W0613
        """Import a config flow from configuration."""
        if self._async_current_entries():
            return self.async_abort(reason="one_instance_allowed")

        return self.async_show_form(step_id='sunology_setup', data_schema=vol.Schema({
            vol.Required(CONF_GATEWAY_IP): vol.All(str, vol.Length(min=3)),
        }))

    async def async_step_sunology_setup(self, user_input):
        """ try to setup sunology ehub """

        schema = vol.Schema({
            vol.Required(CONF_GATEWAY_IP): vol.All(str, vol.Length(min=3)),
        })
        
        if user_input is None:
            return self.async_show_form(step_id='sunology_setup', data_schema=schema)
        
        gateway_ip = user_input[CONF_GATEWAY_IP]
        
        try:
            data = {
                CONF_GATEWAY_IP: gateway_ip,
            }
            return self.async_create_entry(title=gateway_ip, data=data)
        except: 
            _LOGGER.error("Unknown error")
            errors = {"base": "unkonwn"}
            return self.async_show_form(step_id="georide_login", data_schema=schema, errors=errors)
        