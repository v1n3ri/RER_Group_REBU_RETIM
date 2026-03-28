from homeassistant.helpers.entity import DeviceInfo  
from homeassistant.components.sensor import SensorEntity  

class RERGroupSensor(SensorEntity):  
    def __init__(self, name, device_email):  
        self._name = name  
        self._unique_id = name.lower().replace(' ', '_')  
        self._device_email = device_email  
        self._device_info = DeviceInfo(  
            identifiers={("rer_group", self._unique_id)},  
            name=self._name,  
            manufacturer="RER Group",  
            model="Group Device",  
            sw_version="1.0",  
            configuration_url=f"https://example.com/devices/{self._unique_id}",  
        )  

    @property  
    def device_info(self):  
        return self._device_info  

    # Additional implementation details for your sensor would go here...  
