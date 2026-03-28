from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, ATTRIBUTION

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data
    sensors = [RetimBalanceSensor(coordinator, entry)]
    
    # Logic for dynamic sensors...
    if "user" in data and isinstance(data["user"], dict):
        for key, value in data["user"].items():
            if isinstance(value, (int, float, str, bool)):
                sensors.append(DynamicUserSensor(coordinator, entry, key))
    
    async_add_entities(sensors)

class RetimBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"RER Account ({entry.data['email']})",
            manufacturer="RER Group",
            model="Customer Portal",
        )

class RetimBalanceSensor(RetimBaseSensor):
    _attr_name = "Account Balance"
    _attr_native_unit_of_measurement = "RON"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_icon = "mdi:cash-multiple"

    @property
    def native_value(self):
        invoices = self.coordinator.data.get("invoices", {}).get("data", [])
        return round(sum(float(i.get("amount", 0)) for i in invoices if i.get("unpaid")), 2)

class DynamicUserSensor(RetimBaseSensor):
    _attr_entity_category = EntityCategory.DIAGNOSTIC # Keeps UI clean
    
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = field_name.replace("_", " ").title()
        self._attr_unique_id = f"{entry.entry_id}_user_{field_name}"

    @property
    def native_value(self):
        return self.coordinator.data.get("user", {}).get(self.field_name)