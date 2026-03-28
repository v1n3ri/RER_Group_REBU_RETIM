from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, ATTRIBUTION

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data
    if not data:
        return

    sensors = [RetimBalanceSensor(coordinator, entry)]
    
    # User sensors
    user_info = data.get("user", {})
    if isinstance(user_info, dict):
        for key, value in user_info.items():
            if isinstance(value, (int, float, str, bool)) and key != "id":
                sensors.append(DynamicUserSensor(coordinator, entry, key))
    
    # Invoice sensors
    inv_data = data.get("invoices", {}).get("data", [])
    if inv_data and isinstance(inv_data, list):
        for key in inv_data[0].keys():
            if key not in ["id", "pdf", "unpaid", "status"]:
                sensors.append(DynamicInvoiceSensor(coordinator, entry, key))

    # CUSTOMER sensors (Nou)
    cust_data = data.get("customers", {}).get("data", [])
    if cust_data and isinstance(cust_data, list):
        for key, value in cust_data[0].items():
            if isinstance(value, (int, float, str, bool)) and key != "id":
                sensors.append(DynamicCustomerSensor(coordinator, entry, key))
    
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
        )

class RetimBalanceSensor(RetimBaseSensor):
    _attr_name = "Account Balance"
    _attr_native_unit_of_measurement = "RON"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash-multiple"
    _attr_unique_id = f"rer_balance_unique" # Schimbă dacă ai mai multe conturi

    @property
    def native_value(self):
        invoices = self.coordinator.data.get("invoices", {}).get("data", [])
        return round(sum(float(i.get("amount", 0)) for i in invoices if i.get("unpaid")), 2)

class DynamicUserSensor(RetimBaseSensor):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = f"User {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{entry.entry_id}_user_{field_name}"
    @property
    def native_value(self):
        return self.coordinator.data.get("user", {}).get(self.field_name)

class DynamicInvoiceSensor(RetimBaseSensor):
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = f"Latest Invoice {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{entry.entry_id}_inv_{field_name}"
    @property
    def native_value(self):
        invs = self.coordinator.data.get("invoices", {}).get("data", [])
        return invs[0].get(self.field_name) if invs else None

class DynamicCustomerSensor(RetimBaseSensor):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = f"Customer {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{entry.entry_id}_cust_{field_name}"
    @property
    def native_value(self):
        custs = self.coordinator.data.get("customers", {}).get("data", [])
        return custs[0].get(self.field_name) if custs else None