# auth/token_manager.py
import json
import os
from typing import Optional

import requests

from auth.token_models import TokenData


class TokenManager:
    """
    Maneja los tokens de UNA cuenta (leer tokens.json, validar, crear session).
    """

    def __init__(self, account_path: str):
        """
        account_path: ruta a la carpeta de la cuenta (ej: auth/cuenta1)
        """
        self.account_path = account_path
        self.tokens: Optional[TokenData] = None

    @property
    def tokens_file(self) -> str:
        return os.path.join(self.account_path, "tokens.json")

    def load_tokens(self) -> TokenData:
        """
        Lee tokens.json y devuelve TokenData.
        """
        if not os.path.exists(self.tokens_file):
            raise FileNotFoundError(f"No existe tokens.json en: {self.tokens_file}")

        with open(self.tokens_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Campos mínimos
        auth_cookie = data.get("auth_cookie")
        vtex_session = data.get("vtex_session")
        vtex_segment = data.get("vtex_segment")

        if not auth_cookie or not vtex_session or not vtex_segment:
            raise ValueError(f"tokens.json incompleto en {self.tokens_file}")

        email = data.get("email")
        expires_at = data.get("expires_at")

        account_name = os.path.basename(self.account_path.rstrip("/\\"))

        self.tokens = TokenData(
            account_name=account_name,
            email=email,
            auth_cookie=auth_cookie,
            vtex_session=vtex_session,
            vtex_segment=vtex_segment,
            expires_at=expires_at,
        )
        return self.tokens

    def get_or_load_tokens(self) -> TokenData:
        if self.tokens is None:
            return self.load_tokens()
        return self.tokens

    def build_requests_session(self, base_url: str) -> requests.Session:
        """
        Crea una requests.Session lista con headers y cookies para esta cuenta.
        """
        tokens = self.get_or_load_tokens()

        s = requests.Session()
        s.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Referer": base_url.rstrip("/") + "/",
            "Origin": base_url.rstrip("/"),
        })

        # Cookies críticas VTEX/Nike
        # Ajusta dominios si quieres ser más fino después
        cookies = {
            "VtexIdclientAutCookie_nikeclprod": tokens.auth_cookie,
            "vtex_session": tokens.vtex_session,
            "vtex_segment": tokens.vtex_segment,
        }

        for name, value in cookies.items():
            if not value:
                continue
            # agregamos cookies para dominios típicos VTEX/Nike
            for domain in [".nike.cl", "www.nike.cl", ".checkout.vtex.com"]:
                s.cookies.set(name, value, domain=domain)

        return s
