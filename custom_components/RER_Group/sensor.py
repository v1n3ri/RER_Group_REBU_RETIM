from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTRIBUTION

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Retim sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Get the first batch of data to discover available sensors
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
        if invoices_data and isinstance(invoices_data, list) and invoices_data:
            first_invoice = invoices_data[0]
            for key in first_invoice.keys():
                if key not in ["id", "pdf"]:  # Skip IDs and non-numeric data
                    sensors.append(DynamicInvoiceSensor(coordinator, key))
    
    async_add_entities(sensors)

class RetimBaseSensor(CoordinatorEntity, SensorEntity):
    """Common properties for all Retim sensors."""
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{self.__class__.__name__}"

class RetimBalanceSensor(RetimBaseSensor):
    """Sensor for the current unpaid balance."""
    _attr_name = "Account Balance"
    _attr_native_unit_of_measurement = "RON"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self):
        data_wrapper = self.coordinator.data.get("invoices", {})
        invoices = data_wrapper.get("data", [])
        
        if not invoices:
            return 0.0
            
        total_due = sum(
            float(inv.get("amount", 0)) 
            for inv in invoices 
            if inv.get("unpaid") is True or inv.get("status") != 2
        )
        return round(total_due, 2)

    @property
    def extra_state_attributes(self):
        """Add metadata about the last invoice."""
        data_wrapper = self.coordinator.data.get("invoices", {})
        invoices = data_wrapper.get("data", [])
        
        if not invoices:
            return {}

        last_invoice = invoices[0] if invoices else {}
        
        return {
            "last_invoice_date": last_invoice.get("date"),
            "due_date": last_invoice.get("dueDate"),
            "invoice_number": last_invoice.get("number")
        }

class DynamicUserSensor(RetimBaseSensor):
    """Dynamically created sensor for user data fields."""
    
    def __init__(self, coordinator, field_name, initial_value):
        super().__init__(coordinator)
        self.field_name = field_name
        self._attr_name = field_name.replace("_", " ").title()
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_user_{field_name}"

    @property
    def native_value(self):
        user_data = self.coordinator.data.get("user", {})
        return user_data.get(self.field_name)

class DynamicInvoiceSensor(RetimBaseSensor):
    """Dynamically created sensor for invoice aggregate data."""
    
    def __init__(self, coordinator, field_name):
        super().__init__(coordinator)
        self.field_name = field_name
        self._attr_name = f"Invoice {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_invoice_{field_name}"

    @property
    def native_value(self):
        invoices = self.coordinator.data.get("invoices", {}).get("data", [])
        if not invoices:
            return None
        # Return the first invoice's value for this field
        return invoices[0].get(self.field_name)