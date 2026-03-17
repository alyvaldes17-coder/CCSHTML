#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/account_manager.py — v2.0

FIXES v2.0:
  - Puertos únicos y persistidos en account.json — nunca cambian
  - Puerto base 9223, secuencial, sin colisiones
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from config.settings import AUTH_ROOT


# =============================================================================
# MODELO DE CUENTA
# =============================================================================

@dataclass
class AccountInfo:
    # Identidad
    account_id:   str   = ""          # nombre carpeta: "cuenta2"
    display_name: str   = ""          # nombre visible: "Mi cuenta principal"
    email:        str   = ""          # email Nike: "usuario@gmail.com"
    notas:        str   = ""          # notas personales

    # Config bot
    payment_mode: str         = "transfer"
    skus:         list[str]   = field(default_factory=list)
    cdp_port:     int         = 0     # 0 = auto-calcular

    # Estado
    state:        str   = "NO_AUTH"   # NO_AUTH | READY | BANNED | EJECUTANDO
    last_login:   float = 0.0         # timestamp ultimo login exitoso
    last_buy:     float = 0.0         # timestamp ultima compra
    total_buys:   int   = 0           # compras exitosas totales

    # Historial (ultimas 20 compras)
    historial:    list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AccountInfo":
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)

    @property
    def display(self) -> str:
        """Texto visible en la UI: 'Mi cuenta (usuario@gmail.com)'"""
        if self.display_name and self.email:
            return f"{self.display_name} ({self.email})"
        elif self.display_name:
            return self.display_name
        elif self.email:
            return self.email
        return self.account_id

    @property
    def short_email(self) -> str:
        """Email abreviado para la tabla: 'usua...@gmail.com'"""
        if not self.email:
            return "—"
        parts = self.email.split("@")
        if len(parts) != 2:
            return self.email
        user, domain = parts
        if len(user) <= 4:
            return self.email
        return f"{user[:4]}...@{domain}"

    @property
    def is_ready(self) -> bool:
        return self.state == "READY"

    @property
    def port(self) -> int:
        return self.cdp_port if self.cdp_port > 0 else 9223


# =============================================================================
# MANAGER
# =============================================================================

class CoreAccountManager:
    """
    Gestiona todas las cuentas del bot.
    Lee/escribe auth/<cuenta>/account.json.
    """

    def __init__(self, auth_root: str = AUTH_ROOT):
        self.auth_root = auth_root
        self._cache: dict[str, AccountInfo] = {}
        self._load_all()

    # =========================================================================
    # CARGA / GUARDADO
    # =========================================================================

    def _account_path(self, account_id: str) -> str:
        return os.path.join(self.auth_root, account_id, "account.json")

    def _load_all(self) -> None:
        if not os.path.exists(self.auth_root):
            return

        # Recopilar entradas válidas
        entradas = []
        for entry in sorted(os.listdir(self.auth_root)):
            account_dir = os.path.join(self.auth_root, entry)
            if not os.path.isdir(account_dir):
                continue
            has_profile = os.path.exists(os.path.join(account_dir, "profile_login"))
            has_login   = os.path.exists(os.path.join(account_dir, ".login_ok"))
            if not (has_profile or has_login):
                continue
            entradas.append(entry)

        # Cargar todas primero para conocer puertos ya asignados
        infos = {}
        for entry in entradas:
            infos[entry] = self._load_one(entry)

        # Puertos ya persistidos en disco
        puertos_usados = {
            info.cdp_port
            for info in infos.values()
            if info.cdp_port > 0
        }

        # Asignar puertos únicos a las que no tienen
        puerto_siguiente = 9223
        for entry in entradas:
            info = infos[entry]
            if info.cdp_port <= 0:
                # Buscar siguiente puerto libre
                while puerto_siguiente in puertos_usados:
                    puerto_siguiente += 1
                info.cdp_port = puerto_siguiente
                puertos_usados.add(puerto_siguiente)
                puerto_siguiente += 1
                # Persistir en disco para que no cambie
                self.save(info)

            self._cache[entry] = info

    def _load_one(self, account_id: str) -> AccountInfo:
        path = self._account_path(account_id)
        info = AccountInfo(account_id=account_id)

        # Leer account.json si existe
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                info = AccountInfo.from_dict({**data, "account_id": account_id})
            except Exception as e:
                print(f"[AccountManager] Error leyendo {path}: {e}")

        # Migrar config.json legacy si no hay account.json
        else:
            info = self._migrar_legacy(account_id, info)

        # Sincronizar estado con .login_ok
        login_ok_path = os.path.join(self.auth_root, account_id, ".login_ok")
        if os.path.exists(login_ok_path) and info.state == "NO_AUTH":
            info.state = "READY"
        elif not os.path.exists(login_ok_path):
            info.state = "NO_AUTH"

        return info

    def _migrar_legacy(self, account_id: str, info: AccountInfo) -> AccountInfo:
        cfg_path = os.path.join(self.auth_root, account_id, "config.json")
        if not os.path.exists(cfg_path):
            return info
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            info.email        = cfg.get("email", "") or cfg.get("nike_email", "")
            info.payment_mode = cfg.get("payment_mode", "transfer")
            info.skus         = [s for s in cfg.get("skus", []) if s]
            sku = cfg.get("sku")
            if sku and sku not in info.skus:
                info.skus.insert(0, sku)
            # NO guardar aquí — puerto aún no asignado
            print(f"[AccountManager] Migrado {account_id} desde config.json")
        except Exception as e:
            print(f"[AccountManager] Error migrando {account_id}: {e}")
        return info

    def save(self, info: AccountInfo) -> None:
        """Guarda account.json en disco."""
        account_dir = os.path.join(self.auth_root, info.account_id)
        os.makedirs(account_dir, exist_ok=True)

        path = self._account_path(info.account_id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(info.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[AccountManager] Error guardando {path}: {e}")

    def reload(self, account_id: str) -> AccountInfo:
        """Recarga una cuenta desde disco."""
        info = self._load_one(account_id)
        self._cache[account_id] = info
        return info

    def reload_all(self) -> None:
        """Recarga todas las cuentas."""
        self._cache.clear()
        self._load_all()

    # =========================================================================
    # ACCESO
    # =========================================================================

    def get(self, account_id: str) -> Optional[AccountInfo]:
        return self._cache.get(account_id)

    def get_all(self) -> list[AccountInfo]:
        return list(self._cache.values())

    def get_ready(self) -> list[AccountInfo]:
        return [a for a in self._cache.values() if a.is_ready]

    def find_by_email(self, email: str) -> Optional[AccountInfo]:
        email = email.lower().strip()
        return next(
            (a for a in self._cache.values() if a.email.lower() == email),
            None
        )

    def find_by_name(self, name: str) -> Optional[AccountInfo]:
        name = name.lower().strip()
        return next(
            (a for a in self._cache.values()
             if name in a.display_name.lower() or name in a.account_id.lower()),
            None
        )

    # =========================================================================
    # ACTUALIZACION
    # =========================================================================

    def set_state(self, account_id: str, state: str) -> None:
        info = self._cache.get(account_id)
        if not info:
            return
        info.state = state
        if state == "READY":
            info.last_login = time.time()
        self.save(info)

    def registrar_compra(
        self,
        account_id: str,
        sku:        str,
        precio:     int  = 0,
        telemetria: dict = None,
    ) -> None:
        info = self._cache.get(account_id)
        if not info:
            return

        info.last_buy   = time.time()
        info.total_buys += 1

        entrada = {
            "ts":         time.strftime("%Y-%m-%d %H:%M:%S"),
            "sku":        sku,
            "precio":     precio,
            "telemetria": telemetria or {},
        }
        info.historial.insert(0, entrada)
        info.historial = info.historial[:20]  # Mantener solo las ultimas 20

        self.save(info)
        print(f"[AccountManager] Compra registrada: {account_id} -> SKU {sku}")

    def update_config(
        self,
        account_id:   str,
        display_name: str  = None,
        email:        str  = None,
        payment_mode: str  = None,
        skus:         list = None,
        notas:        str  = None,
    ) -> None:
        info = self._cache.get(account_id)
        if not info:
            return
        if display_name is not None:
            info.display_name = display_name
        if email is not None:
            info.email = email
        if payment_mode is not None:
            info.payment_mode = payment_mode
        if skus is not None:
            info.skus = [s for s in skus if s]
        if notas is not None:
            info.notas = notas
        self.save(info)

    def crear_cuenta(
        self,
        account_id:   str,
        display_name: str = "",
        email:        str = "",
        payment_mode: str = "transfer",
        skus:         list = None,
    ) -> AccountInfo:
        info = AccountInfo(
            account_id   = account_id,
            display_name = display_name,
            email        = email,
            payment_mode = payment_mode,
            skus         = skus or [],
            state        = "NO_AUTH",
        )
        # Asignar puerto único
        usados = {i.cdp_port for i in self._cache.values() if i.cdp_port > 0}
        puerto = 9223
        while puerto in usados:
            puerto += 1
        info.cdp_port = puerto
        self._cache[account_id] = info
        self.save(info)
        return info

    # =========================================================================
    # STATS / RESUMEN
    # =========================================================================

    def resumen(self) -> dict:
        """Resumen rapido para mostrar en la UI."""
        cuentas = self.get_all()
        return {
            "total":        len(cuentas),
            "ready":        sum(1 for c in cuentas if c.is_ready),
            "no_auth":      sum(1 for c in cuentas if c.state == "NO_AUTH"),
            "total_buys":   sum(c.total_buys for c in cuentas),
            "con_sku":      sum(1 for c in cuentas if c.skus),
            "con_email":    sum(1 for c in cuentas if c.email),
        }

    def __repr__(self) -> str:
        r = self.resumen()
        return (f"<AccountManager {r['total']} cuentas | "
                f"{r['ready']} READY | {r['total_buys']} compras>")


# =============================================================================
# INSTANCIA GLOBAL
# =============================================================================

_manager: Optional[CoreAccountManager] = None


def get_manager() -> CoreAccountManager:
    global _manager
    if _manager is None:
        _manager = CoreAccountManager()
    return _manager
