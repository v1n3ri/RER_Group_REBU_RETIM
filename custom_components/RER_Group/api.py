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
        self.headers = {"Accept": "application/json"} # Aceasta lipsea

    async def login(self) -> bool:
        """Autentificare și salvare token."""
        url = f"{self.base_url}/auth/login"
        payload = {"email": self.email, "password": self.password}
        try:
            async with self.session.post(url, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.auth_token = data.get("token") or data.get("access_token")
                    if self.auth_token:
                        self.headers["Authorization"] = f"Bearer {self.auth_token}"
                        # Actualizăm și sesiunea globală pentru siguranță
                        self.session._default_headers.update(self.headers)
                    return True
                _LOGGER.error("Login eșuat: %s", resp.status)
                return False
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Eroare de conexiune la login: %s", err)
            return False

    async def get_data(self):
        """Preia facturile, datele de utilizator și clienții."""
        try:
            # Reutilizăm logica de login dacă token-ul lipsește
            if not self.auth_token:
                await self.login()

            # Helper pentru request-uri
            async def fetch(endpoint):
                async with self.session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as resp:
                    if resp.status == 401: # Token expirat
                        await self.login()
                        async with self.session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as retry_resp:
                            return await retry_resp.json()
                    return await resp.json()

            invoices = await fetch("invoices")
            user_info = await fetch("user")
            customers = await fetch("customers")

            return {
                "user": user_info,
                "invoices": invoices,
                "customers": customers
            }
        except Exception as err:
            _LOGGER.error("Eroare la preluarea datelor: %s", err)
            raise