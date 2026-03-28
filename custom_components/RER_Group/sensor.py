from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTRIBUTION

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Retim sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data
    
    if not data:
        return

    sensors = []
    
    # 1. Main Balance Sensor
    sensors.append(RetimBalanceSensor(coordinator, entry))
    
    # 2. Dynamic User Details (Marked as Diagnostic)
    user_info = data.get("user", {})
    if isinstance(user_info, dict):
        for key, value in user_info.items():
            if isinstance(value, (int, float, str, bool)) and key not in ["id"]:
                sensors.append(DynamicUserSensor(coordinator, entry, key))
    
    # 3. Dynamic Invoice Sensors (Tracking the latest invoice)
    invoices_wrapper = data.get("invoices", {})
    invoices_list = invoices_wrapper.get("data", [])
    if isinstance(invoices_list, list) and len(invoices_list) > 0:
        first_invoice = invoices_list[0]
        for key in first_invoice.keys():
            if key not in ["id", "pdf", "unpaid", "status"]:
                sensors.append(DynamicInvoiceSensor(coordinator, entry, key))
    
    async_add_entities(sensors)

class RetimBaseSensor(CoordinatorEntity, SensorEntity):
    """Common properties for all Retim sensors."""
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
    """Sensor for the current unpaid balance."""
    _attr_name = "Account Balance"
    _attr_native_unit_of_measurement = "RON"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_icon = "mdi:cash-multiple"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_balance"

    @property
    def native_value(self):
        invoices = self.coordinator.data.get("invoices", {}).get("data", [])
        total_due = sum(
            float(inv.get("amount", 0)) 
            for inv in invoices 
            if inv.get("unpaid") is True or inv.get("status") != 2
        )
        return round(total_due, 2)

class DynamicUserSensor(RetimBaseSensor):
    """Diagnostic sensors for user profile data."""
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = field_name.replace("_", " ").title()
        self._attr_unique_id = f"{entry.entry_id}_user_{field_name}"

    @property
    def native_value(self):
        return self.coordinator.data.get("user", {}).get(self.field_name)

class DynamicInvoiceSensor(RetimBaseSensor):
    """Sensors tracking the latest invoice details."""
    
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = f"Latest Invoice {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{entry.entry_id}_invoice_{field_name}"

    @property
    def native_value(self):
        invoices = self.coordinator.data.get("invoices", {}).get("data", [])
        if not invoices:
            return None
        return invoices[0].get(self.field_name)