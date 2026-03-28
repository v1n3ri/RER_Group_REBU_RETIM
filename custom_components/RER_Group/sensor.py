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
    sensors = []
    
    # Static sensor: Account Balance
    sensors.append(RetimBalanceSensor(coordinator))
    
    # Dynamic sensors from user data
    if "user" in data and isinstance(data["user"], dict):
        for key, value in data["user"].items():
            if isinstance(value, (int, float, str, bool)):
                sensors.append(DynamicUserSensor(coordinator, key, value))
    
    # Dynamic sensors from invoices
    if "invoices" in data and isinstance(data["invoices"], dict):
        invoices_data = data["invoices"].get("data", [])
        if invoices_data and isinstance(invoices_data, list):
            first_invoice = invoices_data[0]
            for key in first_invoice.keys():
                if key not in ["id", "pdf"]:
                    sensors.append(DynamicInvoiceSensor(coordinator, key))

    # NEW: Dynamic sensors from customers data
    if "customers" in data and isinstance(data["customers"], dict):
        customers_list = data["customers"].get("data", [])
        if customers_list and isinstance(customers_list, list):
            # We track the primary account details (first item in data list)
            first_customer = customers_list[0]
            for key, value in first_customer.items():
                # Avoid complex structures like 'addresses' for simple sensors
                if isinstance(value, (int, float, str, bool)) and key != "id":
                    sensors.append(DynamicCustomerSensor(coordinator, key))
    
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

# NEW: Customer sensor class
class DynamicCustomerSensor(RetimBaseSensor):
    """Dynamically created sensor for customer data fields."""
    
    def __init__(self, coordinator, field_name):
        super().__init__(coordinator)
        self.field_name = field_name
        self._attr_name = f"Customer {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_customer_{field_name}"

    @property
    def native_value(self):
        customers = self.coordinator.data.get("customers", {}).get("data", [])
        if not customers:
            return None
        return customers[0].get(self.field_name)