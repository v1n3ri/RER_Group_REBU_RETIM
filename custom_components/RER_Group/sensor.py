from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, ATTRIBUTION

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Retim sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data
    if not data:
        return

    # 1. Adăugăm senzorul principal de Sold (logica nouă cu dueAmount)
    sensors = [RetimBalanceSensor(coordinator, entry)]
    
    # 2. Adăugăm dinamic senzorii de Utilizator
    user_info = data.get("user", {})
    if isinstance(user_info, dict):
        for key, value in user_info.items():
            if isinstance(value, (int, float, str, bool)) and key != "id":
                sensors.append(DynamicUserSensor(coordinator, entry, key))
    
    # 3. Adăugăm dinamic senzorii pentru Ultima Factură
    inv_wrapper = data.get("invoices", {})
    inv_data = inv_wrapper.get("data", [])
    if inv_data and isinstance(inv_data, list):
        # Folosim cheile primei facturi pentru a crea senzori
        for key in inv_data[0].keys():
            if key not in ["id", "pdf", "unpaid", "status", "lines"]:
                sensors.append(DynamicInvoiceSensor(coordinator, entry, key))

    # 4. Adăugăm dinamic senzorii de Client (Diagnostic)
    cust_wrapper = data.get("customers", {})
    cust_data = cust_wrapper.get("data", [])
    if cust_data and isinstance(cust_data, list):
        for key in cust_data[0].keys():
            if key not in ["id"]:
                sensors.append(DynamicCustomerSensor(coordinator, entry, key))

    async_add_entities(sensors)

class RetimBaseSensor(CoordinatorEntity, SensorEntity):
    """Clasa de bază care grupează toate entitățile sub același Device."""
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self.entry = entry
        # Această secțiune asigură gruparea în interfață sub un singur dispozitiv
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Cont Retim ({entry.data.get('email')})",
            "manufacturer": "RER Group",
        }

class RetimBalanceSensor(RetimBaseSensor):
    """Senzorul principal pentru Soldul Total."""
    _attr_name = "Sold Total de Plată"
    _attr_native_unit_of_measurement = "RON"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_unique_id = f"{DOMAIN}_total_balance"

    @property
    def native_value(self):
        """Suma dueAmount pentru toate facturile cu unpaid: true."""
        inv_wrapper = self.coordinator.data.get("invoices", {})
        invoices = inv_wrapper.get("data", [])
        if not invoices:
            return 0.0
        
        return round(sum(
            float(inv.get("dueAmount") or 0) 
            for inv in invoices 
            if inv.get("unpaid") is True
        ), 2)

class DynamicUserSensor(RetimBaseSensor):
    """Senzori pentru profilul de utilizator."""
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = f"User {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{entry.entry_id}_user_{field_name}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.coordinator.data.get("user", {}).get(self.field_name)

class DynamicInvoiceSensor(RetimBaseSensor):
    """Senzori pentru detaliile ultimei facturi."""
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = f"Factură {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{entry.entry_id}_inv_{field_name}"

    @property
    def native_value(self):
        inv_wrapper = self.coordinator.data.get("invoices", {})
        inv_list = inv_wrapper.get("data", [])
        return inv_list[0].get(self.field_name) if inv_list else None

class DynamicCustomerSensor(RetimBaseSensor):
    """Senzori pentru datele de client (loc de consum, contract)."""
    def __init__(self, coordinator, entry, field_name):
        super().__init__(coordinator, entry)
        self.field_name = field_name
        self._attr_name = f"Client {field_name.replace('_', ' ').title()}"
        self._attr_unique_id = f"{entry.entry_id}_cust_{field_name}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        cust_wrapper = self.coordinator.data.get("customers", {})
        cust_list = cust_wrapper.get("data", [])
        return cust_list[0].get(self.field_name) if cust_list else None