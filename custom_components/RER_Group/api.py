import logging
import asyncio
import aiohttp

_LOGGER = logging.getLogger(__name__)

class RetimAPI:
    def __init__(self, email, password, session: aiohttp.ClientSession, base_url):
        self.email = email
        self.password = password
        self.session = session
        self.base_url = base_url
        self.auth_token = None

    async def login(self) -> bool:
        """Attempt to login and store the bearer token in the session."""
        url = f"{self.base_url}/auth/login"
        payload = {"email": self.email, "password": self.password}
        try:
            async with self.session.post(url, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.auth_token = data.get("token") or data.get("access_token")
                    if self.auth_token:
                        # Apply token to all future session requests
                        self.session._default_headers.update(
                            {"Authorization": f"Bearer {self.auth_token}"}
                        )
                    _LOGGER.debug("Successfully authenticated with Retim API")
                    return True
                _LOGGER.error("Login failed: %s", resp.status)
                return False
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Connection error during login: %s", err)
            return False

    async def _request(self, method, endpoint):
        """Internal helper to handle requests and auto-retry on 401."""
        url = f"{self.base_url}/{endpoint}"
        
        async with self.session.request(method, url) as resp:
            if resp.status == 401:
                _LOGGER.warning("Token expired, attempting re-auth")
                if await self.login():
                    async with self.session.request(method, url) as retry_resp:
                        return await retry_resp.json()
            return await resp.json()

    async def get_data(self):
        """Fetch all data using the authenticated session."""
        try:
            # Fetch invoices
            async with self.session.get(
                f"{self.base_url}/invoices", 
                headers=self.headers
            ) as resp:
                if resp.status == 401:
                    await self.login()
                    async with self.session.get(
                        f"{self.base_url}/invoices", 
                        headers=self.headers
                    ) as retry_resp:
                        invoices = await retry_resp.json()
                else:
                    invoices = await resp.json()
            
            # Fetch user info
            async with self.session.get(
                f"{self.base_url}/user", 
                headers=self.headers
            ) as resp:
                user_info = await resp.json()

            # NEW: Fetch customers info
            async with self.session.get(
                f"{self.base_url}/customers", 
                headers=self.headers
            ) as resp:
                customers_info = await resp.json()

            return {
                "user": user_info,
                "invoices": invoices,
                "customers": customers_info  # Added this field
            }
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise