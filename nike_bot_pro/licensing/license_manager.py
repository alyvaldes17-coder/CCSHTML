#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
licensing/license_manager.py

Sistema de licencias para Nike Bot Pro.

ARQUITECTURA:
  - Las licencias viven en un GitHub Gist PRIVADO tuyo
  - El bot valida contra ese Gist al iniciar y cada hora
  - Sin internet o key invalida → bot no corre
  - Tu generas/revogas keys desde tu PC con este mismo archivo

SEGURIDAD:
  - Keys hasheadas con SHA256 — nadie puede ver las keys reales en el Gist
  - El Gist es privado — solo visible con tu token de GitHub
  - El .exe compilado con PyInstaller no muestra el codigo
  - Comunicacion HTTPS siempre

PLANES:
  basic:  3 cuentas, 1 drop/dia
  pro:    6 cuentas, 3 drops/dia
  full:   10 cuentas, ilimitado

USO (tu lado):
  python licensing/license_manager.py generate --plan pro --days 30 --client "Juan Perez"
  python licensing/license_manager.py revoke   --key NIKE-XXXX-XXXX-XXXX
  python licensing/license_manager.py list

USO (bot lado, automatico):
  from licensing.license_manager import LicenseValidator
  ok, info = LicenseValidator.validar()
  if not ok:
      sys.exit(1)
"""

import argparse
import hashlib
import json
import os
import random
import string
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests


# =============================================================================
# CONFIGURACION — solo tu la tienes
# =============================================================================

# Tu GitHub personal access token (Settings → Developer settings → Personal access tokens)
# Permisos necesarios: gist (read/write)
# NUNCA commitear esto — va en variable de entorno o archivo .env local
GITHUB_TOKEN = os.environ.get("NIKE_BOT_GITHUB_TOKEN", "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")

# ID de tu Gist privado (lo creas una vez, despues solo editas)
# Crear en: https://gist.github.com — marcar como "Secret"
GIST_ID = os.environ.get("NIKE_BOT_GIST_ID", "548b914135c63a0eef1ba78dc3662361")

# Salt secreto para hashear keys — cambialo por uno tuyo
# Este string va DENTRO del .exe compilado, nadie lo ve
_SALT = "NikeBot2025_##CL_drop_secret_salt_v1"

# Planes disponibles
PLANES = {
    "basic": {"cuentas": 3,  "drops_dia": 1,  "precio": 25000},
    "pro":   {"cuentas": 6,  "drops_dia": 3,  "precio": 45000},
    "full":  {"cuentas": 10, "drops_dia": 99, "precio": 70000},
}


# =============================================================================
# GENERADOR DE KEYS (tu lado)
# =============================================================================

class LicenseGenerator:
    """
    Genera, lista y revoca licencias.
    Solo tu usas esto — nunca va al cliente.
    """

    @staticmethod
    def _generar_key_raw() -> str:
        """Genera una key legible: NIKE-XXXX-XXXX-XXXX"""
        chars = string.ascii_uppercase + string.digits
        segmentos = ["".join(random.choices(chars, k=4)) for _ in range(3)]
        return "NIKE-" + "-".join(segmentos)

    @staticmethod
    def _hashear_key(key_raw: str) -> str:
        """Hash SHA256 de la key — esto es lo que se guarda en GitHub."""
        return hashlib.sha256(f"{_SALT}{key_raw}".encode()).hexdigest()

    @staticmethod
    def _cargar_gist() -> dict:
        """Descarga el JSON de licencias desde el Gist privado."""
        if not GITHUB_TOKEN or not GIST_ID:
            raise ValueError("NIKE_BOT_GITHUB_TOKEN y NIKE_BOT_GIST_ID no configurados.")

        r = requests.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10,
        )
        r.raise_for_status()
        files = r.json().get("files", {})
        content = next(iter(files.values()), {}).get("content", "{}")
        return json.loads(content)

    @staticmethod
    def _guardar_gist(data: dict) -> None:
        """Sube el JSON actualizado al Gist."""
        if not GITHUB_TOKEN or not GIST_ID:
            raise ValueError("NIKE_BOT_GITHUB_TOKEN y NIKE_BOT_GIST_ID no configurados.")

        payload = {
            "files": {
                "licenses.json": {
                    "content": json.dumps(data, indent=2, ensure_ascii=False)
                }
            }
        }
        r = requests.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json=payload,
            timeout=10,
        )
        r.raise_for_status()

    @classmethod
    def generar(cls, plan: str, dias: int, cliente: str) -> str:
        """
        Genera una nueva licencia y la sube al Gist.

        Returns:
            La key raw que le das al cliente (NIKE-XXXX-XXXX-XXXX)
        """
        if plan not in PLANES:
            raise ValueError(f"Plan invalido: {plan}. Opciones: {list(PLANES.keys())}")

        key_raw  = cls._generar_key_raw()
        key_hash = cls._hashear_key(key_raw)

        expira = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")

        data = cls._cargar_gist()
        data[key_hash] = {
            "plan":     plan,
            "cliente":  cliente,
            "expira":   expira,
            "dias":     dias,
            "activa":   True,
            "creada":   datetime.now().strftime("%Y-%m-%d %H:%M"),
            "usos":     0,
        }
        cls._guardar_gist(data)

        print(f"\n{'='*50}")
        print(f"LICENCIA GENERADA")
        print(f"{'='*50}")
        print(f"Cliente: {cliente}")
        print(f"Plan:    {plan.upper()} ({PLANES[plan]['cuentas']} cuentas)")
        print(f"Expira:  {expira} ({dias} dias)")
        print(f"{'='*50}")
        print(f"KEY PARA EL CLIENTE:")
        print(f"  {key_raw}")
        print(f"{'='*50}")
        print(f"Mandala por privado — nunca por grupo\n")

        return key_raw

    @classmethod
    def revocar(cls, key_raw: str) -> bool:
        """Desactiva una licencia inmediatamente."""
        key_hash = cls._hashear_key(key_raw)
        data = cls._cargar_gist()

        if key_hash not in data:
            print(f"Key no encontrada: {key_raw}")
            return False

        data[key_hash]["activa"] = False
        cls._guardar_gist(data)
        print(f"Licencia revocada: {data[key_hash]['cliente']}")
        return True

    @classmethod
    def listar(cls) -> None:
        """Muestra todas las licencias activas."""
        data = cls._cargar_gist()

        if not data:
            print("Sin licencias registradas.")
            return

        print(f"\n{'='*70}")
        print(f"{'CLIENTE':<20} {'PLAN':<8} {'EXPIRA':<12} {'ESTADO':<10} {'USOS'}")
        print(f"{'='*70}")

        hoy = datetime.now().date()
        for key_hash, lic in data.items():
            expira = datetime.strptime(lic["expira"], "%Y-%m-%d").date()
            dias_restantes = (expira - hoy).days
            estado = "ACTIVA" if lic["activa"] and dias_restantes > 0 else "EXPIRADA"
            print(
                f"{lic['cliente']:<20} "
                f"{lic['plan'].upper():<8} "
                f"{lic['expira']:<12} "
                f"{estado:<10} "
                f"{lic.get('usos', 0)} usos"
            )
            if lic["activa"] and dias_restantes > 0:
                print(f"  -- {dias_restantes} dias restantes")

        print(f"{'='*70}\n")

    @classmethod
    def extender(cls, key_raw: str, dias_extra: int) -> bool:
        """Extiende una licencia X dias adicionales."""
        key_hash = cls._hashear_key(key_raw)
        data = cls._cargar_gist()

        if key_hash not in data:
            print(f"Key no encontrada.")
            return False

        lic = data[key_hash]
        expira_actual = datetime.strptime(lic["expira"], "%Y-%m-%d")
        nueva_expira  = expira_actual + timedelta(days=dias_extra)
        lic["expira"] = nueva_expira.strftime("%Y-%m-%d")
        lic["activa"] = True

        cls._guardar_gist(data)
        print(f"Licencia extendida: {lic['cliente']} -> nueva expira: {lic['expira']}")
        return True


# =============================================================================
# VALIDADOR (va dentro del .exe)
# =============================================================================

class LicenseValidator:
    """
    Valida la licencia del cliente al iniciar el bot.
    Esta clase va compilada dentro del .exe.
    """

    # Cache local para no consultar GitHub en cada accion
    _cache_path = Path.home() / ".nikebotpro" / "license.cache"
    _cache_ttl  = 3600  # 1 hora — revalidar cada hora

    @classmethod
    def _hashear_key(cls, key_raw: str) -> str:
        return hashlib.sha256(f"{_SALT}{key_raw}".encode()).hexdigest()

    @classmethod
    def _leer_key_guardada(cls) -> str | None:
        """Lee la key guardada localmente (cifrada)."""
        key_file = Path.home() / ".nikebotpro" / "key.dat"
        try:
            if key_file.exists():
                # XOR simple con salt — no es criptografia fuerte
                # pero evita que el cliente vea su key en texto plano
                raw = key_file.read_bytes()
                salt_bytes = _SALT.encode()
                decoded = bytes(b ^ salt_bytes[i % len(salt_bytes)]
                                for i, b in enumerate(raw))
                return decoded.decode()
        except Exception:
            pass
        return None

    @classmethod
    def _guardar_key(cls, key_raw: str) -> None:
        """Guarda la key cifrada localmente."""
        key_file = Path.home() / ".nikebotpro" / "key.dat"
        key_file.parent.mkdir(parents=True, exist_ok=True)
        salt_bytes = _SALT.encode()
        encoded = bytes(b ^ salt_bytes[i % len(salt_bytes)]
                        for i, b in enumerate(key_raw.encode()))
        key_file.write_bytes(encoded)

    @classmethod
    def _validar_contra_gist(cls, key_hash: str) -> tuple[bool, dict]:
        """Valida el hash contra el Gist publico de solo lectura."""
        try:
            # El GIST_ID va hardcodeado en el .exe
            # El Gist es SECRET (no publico) — solo accesible con la URL directa
            # No requiere token para leer si conoces el ID
            r = requests.get(
                f"https://api.github.com/gists/{GIST_ID}",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=8,
            )
            if r.status_code != 200:
                return False, {"error": f"HTTP {r.status_code}"}

            files   = r.json().get("files", {})
            content = next(iter(files.values()), {}).get("content", "{}")
            data    = json.loads(content)

            if key_hash not in data:
                return False, {"error": "Key no encontrada"}

            lic = data[key_hash]

            if not lic.get("activa", False):
                return False, {"error": "Licencia revocada"}

            expira = datetime.strptime(lic["expira"], "%Y-%m-%d").date()
            if datetime.now().date() > expira:
                return False, {"error": f"Licencia expirada el {lic['expira']}"}

            return True, lic

        except requests.exceptions.ConnectionError:
            return False, {"error": "Sin conexion a internet"}
        except Exception as e:
            return False, {"error": str(e)}

    @classmethod
    def _leer_cache(cls) -> dict | None:
        """Lee la cache local si es reciente."""
        try:
            if cls._cache_path.exists():
                data = json.loads(cls._cache_path.read_text())
                if time.time() - data.get("timestamp", 0) < cls._cache_ttl:
                    return data
        except Exception:
            pass
        return None

    @classmethod
    def _escribir_cache(cls, lic_data: dict) -> None:
        try:
            cls._cache_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"timestamp": time.time(), **lic_data}
            cls._cache_path.write_text(json.dumps(data))
        except Exception:
            pass

    @classmethod
    def validar(cls, key_input: str | None = None) -> tuple[bool, dict]:
        """
        Valida la licencia. Retorna (ok, info).

        Flujo:
          1. Si hay key en cache reciente -> usar cache
          2. Si no -> pedir key al usuario o usar la guardada
          3. Validar contra GitHub Gist
          4. Guardar en cache si OK

        Returns:
            (True, {"plan": "pro", "cuentas": 6, "cliente": "...", "dias_restantes": 15})
            (False, {"error": "Licencia expirada"})
        """
        # Intentar cache primero
        cache = cls._leer_cache()
        if cache and not key_input:
            dias_rest = (
                datetime.strptime(cache["expira"], "%Y-%m-%d").date()
                - datetime.now().date()
            ).days
            if dias_rest > 0:
                cache["dias_restantes"] = dias_rest
                return True, cache

        # Obtener key
        key_raw = key_input or cls._leer_key_guardada()

        if not key_raw:
            # Primera vez — pedir al usuario
            print("\n" + "="*50)
            print("NIKE BOT PRO — Validacion de licencia")
            print("="*50)
            key_raw = input("Ingresa tu key de licencia (NIKE-XXXX-XXXX-XXXX): ").strip().upper()
            if not key_raw:
                return False, {"error": "No se ingreso key"}

        # Validar formato basico
        if not key_raw.startswith("NIKE-") or len(key_raw) != 19:
            return False, {"error": "Formato de key invalido"}

        key_hash = cls._hashear_key(key_raw)
        ok, lic  = cls._validar_contra_gist(key_hash)

        if ok:
            cls._guardar_key(key_raw)
            cls._escribir_cache(lic)

            dias_rest = (
                datetime.strptime(lic["expira"], "%Y-%m-%d").date()
                - datetime.now().date()
            ).days
            lic["dias_restantes"] = dias_rest
            lic["cuentas_max"]    = PLANES.get(lic["plan"], {}).get("cuentas", 3)

        return ok, lic

    @classmethod
    def max_cuentas(cls) -> int:
        """Retorna cuantas cuentas puede usar esta licencia."""
        ok, info = cls.validar()
        if not ok:
            return 0
        return PLANES.get(info.get("plan", "basic"), {}).get("cuentas", 3)


# =============================================================================
# CLI — solo para ti
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Nike Bot Pro — Gestor de licencias")
    sub    = parser.add_subparsers(dest="cmd")

    # generate
    gen = sub.add_parser("generate", help="Generar nueva licencia")
    gen.add_argument("--plan",   required=True, choices=PLANES.keys())
    gen.add_argument("--days",   required=True, type=int)
    gen.add_argument("--client", required=True)

    # revoke
    rev = sub.add_parser("revoke", help="Revocar licencia")
    rev.add_argument("--key", required=True)

    # list
    sub.add_parser("list", help="Listar todas las licencias")

    # extend
    ext = sub.add_parser("extend", help="Extender licencia")
    ext.add_argument("--key",  required=True)
    ext.add_argument("--days", required=True, type=int)

    args = parser.parse_args()

    if args.cmd == "generate":
        LicenseGenerator.generar(args.plan, args.days, args.client)

    elif args.cmd == "revoke":
        LicenseGenerator.revocar(args.key)

    elif args.cmd == "list":
        LicenseGenerator.listar()

    elif args.cmd == "extend":
        LicenseGenerator.extender(args.key, args.days)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
