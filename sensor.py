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
    
    # We only initialize the Balance sensor now
    async_add_entities([RetimBalanceSensor(coordinator)])

class RetimBaseSensor(CoordinatorEntity, SensorEntity):
    """Common properties for all Retim sensors."""
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        # Unique ID allows for entity renaming in the HA UI
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
            
        # Checks both the 'unpaid' boolean and the 'status' field for reliability
        total_due = sum(
            float(inv.get("amount", 0)) 
            for inv in invoices 
            if inv.get("unpaid") is True or inv.get("status") != 2
        )
        return round(total_due, 2)

    @property
    def extra_state_attributes(self):
        """Add metadata about the last invoice to the sensor attributes."""
        data_wrapper = self.coordinator.data.get("invoices", {})
        invoices = data_wrapper.get("data", [])
        
        if not invoices:
            return {}

        # Sort by date to find the most recent invoice
        # Invoices use format "DD.MM.YYYY" in the API
        last_invoice = invoices[0] if invoices else {}
        
        return {
            "last_invoice_date": last_invoice.get("date"),
            "due_date": last_invoice.get("dueDate"),
            "invoice_number": last_invoice.get("number")
        }