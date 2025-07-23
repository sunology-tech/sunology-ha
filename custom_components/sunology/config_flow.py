""" Sunology config flow """

import logging
from homeassistant import config_entries
from  homeassistant.helpers.service_info import zeroconf
from homeassistant.const import CONF_HOST, CONF_PORT
import voluptuous as vol
from .const import CONF_GATEWAY_HOST, CONF_GATEWAY_PORT, DOMAIN, PACKAGE_NAME

_LOGGER = logging.getLogger(PACKAGE_NAME)

@config_entries.HANDLERS.register(DOMAIN)
class SunologyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Sunology config flow """

    def __init__(self):
        """Initialize the Daikin config flow."""
        self.hostname = None
        self.port = 20199
    
    @property
    def schema(self):
        """Return current schema."""
        return vol.Schema({
            vol.Required(CONF_GATEWAY_HOST, default=self.hostname): vol.All(str),
            vol.Required(CONF_GATEWAY_PORT, default=self.port): vol.All(int, vol.Range(min=1, max=65535))
        })
    
    async def async_step_user(self, user_input=None): #pylint: disable=W0613
        """ handle info to help to configure Sunology """
        if user_input is None:
            return self.async_show_form(step_id='sunology_setup', data_schema=self.schema)
        gateway_host = user_input[CONF_GATEWAY_HOST]
        gateway_port = user_input[CONF_GATEWAY_PORT]
        try:
            data = {
                CONF_GATEWAY_HOST: gateway_host,
                CONF_GATEWAY_PORT: gateway_port,
            }
            return self.async_create_entry(title=gateway_host, data=data)
        except: 
            _LOGGER.error("Unknown error")
            errors = {"base": "unkonwn"}
            return self.async_show_form(step_id="sunology_setup", data_schema=self.schema, errors=errors)
        
    
    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo): #pylint: disable=W0613
        """ handle info to help to configure Sunology """
        await self.async_set_unique_id(discovery_info.hostname)
        self._abort_if_unique_id_configured()
        _LOGGER.info("New device dicovered %s", discovery_info)
        if discovery_info is not None:
            self.hostname = discovery_info.hostname
            self.port = discovery_info.port
            self.context.update({"title_placeholders": {"name": discovery_info.hostname}})
            return await self.async_step_user()
        return None


    async def async_step_import(self, user_input=None): #pylint: disable=W0613
        """Import a config flow from configuration."""
        return await self.async_step_user()

    async def async_step_sunology_setup(self, user_input):
        """ try to setup sunology ehub """
        if user_input is None:
            return self.async_show_form(step_id='sunology_setup', data_schema=self.schema)
        gateway_host = user_input[CONF_GATEWAY_HOST]
        gateway_port = user_input[CONF_GATEWAY_PORT]
        try:
            data = {
                CONF_GATEWAY_HOST: gateway_host,
                CONF_GATEWAY_PORT: gateway_port,
            }
            return self.async_create_entry(title=gateway_host, data=data)
        except: 
            _LOGGER.error("Unknown error")
            errors = {"base": "unkonwn"}
            return self.async_show_form(step_id="sunology_setup", data_schema=self.schema, errors=errors)
