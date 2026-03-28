import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

class RetimAPI:
    def __init__(self, email, password, session, base_url):
        self.email = email
        self.password = password
        self.session = session
        self.base_url = base_url  # Now dynamic
        self.headers = {"Accept": "application/json"}

    async def login(self):
        """Attempt to login to verify credentials."""
        url = f"{self.base_url}/auth/login"
        payload = {"email": self.email, "password": self.password}
        try:
            async with self.session.post(url, json=payload) as resp:
                return resp.status == 200
        except Exception as err:
            _LOGGER.error("Error connecting to Retim during login: %s", err)
            return False

    async def get_data(self):
        """Fetch all data using the authenticated session."""
        # Use the session passed in __init__, don't create a new one
        async with self.session.get(f"{self.base_url}/invoices") as resp:
            invoices = await resp.json()
        
        async with self.session.get(f"{self.base_url}/user") as resp:
            user_info = await resp.json()

        return {
            "user": user_info,
            "invoices": invoices
        }