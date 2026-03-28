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
        """Fetch user profile and invoices."""
        user_info = await self._request("GET", "user")
        invoices = await self._request("GET", "invoices")
        return {
            "user": user_info,
            "invoices": invoices
        }