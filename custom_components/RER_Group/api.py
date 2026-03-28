import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

class RetimAPI:
    def __init__(self, email, password, session, base_url):
        self.email = email
        self.password = password
        self.session = session
        self.base_url = base_url
        self.headers = {"Accept": "application/json"}
        self.auth_token = None

    async def login(self):
        """Attempt to login to verify credentials and get auth token."""
        url = f"{self.base_url}/auth/login"
        payload = {"email": self.email, "password": self.password}
        try:
            async with self.session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Try to extract token (adjust based on your API response)
                    self.auth_token = data.get("token") or data.get("access_token")
                    if self.auth_token:
                        self.headers["Authorization"] = f"Bearer {self.auth_token}"
                    _LOGGER.debug("Successfully authenticated with Retim API")
                    return True
                else:
                    _LOGGER.error("Login failed with status %s", resp.status)
                    return False
        except Exception as err:
            _LOGGER.error("Error connecting to Retim during login: %s", err)
            return False

    async def get_data(self):
        """Fetch all data using the authenticated session."""
        try:
            async with self.session.get(
                f"{self.base_url}/invoices", 
                headers=self.headers
            ) as resp:
                if resp.status == 401:
                    # Re-authenticate if session expired
                    _LOGGER.warning("Session expired, re-authenticating...")
                    await self.login()
                    async with self.session.get(
                        f"{self.base_url}/invoices", 
                        headers=self.headers
                    ) as retry_resp:
                        invoices = await retry_resp.json()
                else:
                    invoices = await resp.json()
            
            async with self.session.get(
                f"{self.base_url}/user", 
                headers=self.headers
            ) as resp:
                user_info = await resp.json()

            return {
                "user": user_info,
                "invoices": invoices
            }
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise