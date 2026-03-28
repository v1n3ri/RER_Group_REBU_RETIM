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
                    # Extract token from response
                    self.auth_token = data.get("token") or data.get("access_token")
                    
                    # Validate that we got a token
                    if not self.auth_token:
                        _LOGGER.error("Login response did not contain a valid token")
                        return False
                    
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
                        if retry_resp.status != 200:
                            _LOGGER.error("Failed to fetch invoices after re-authentication: %s", retry_resp.status)
                            raise Exception(f"Invoices API returned status {retry_resp.status}")
                        invoices = await retry_resp.json()
                else:
                    if resp.status != 200:
                        _LOGGER.error("Failed to fetch invoices: %s", resp.status)
                        raise Exception(f"Invoices API returned status {resp.status}")
                    invoices = await resp.json()
            
            async with self.session.get(
                f"{self.base_url}/user", 
                headers=self.headers
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to fetch user info: %s", resp.status)
                    raise Exception(f"User API returned status {resp.status}")
                user_info = await resp.json()

            return {
                "user": user_info,
                "invoices": invoices
            }
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise