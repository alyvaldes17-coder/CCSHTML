#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ui/account_editor.py — v4.0

MEJORAS v4.0:
- Búsqueda SKU via curl + cookies reales de Chrome (sin 403)
- Extrae cookies del browser via CDP antes de hacer el request
- Fallback a CDP directo si curl no está disponible
- Timeout 10s, retry automático
"""

import json
import os
import subprocess
import threading
import urllib.request
import customtkinter as ctk

C_BG        = "#0a0a0a"
C_PANEL     = "#111111"
C_ROW       = "#161616"
C_BORDER    = "#2a2a2a"
C_GREEN     = "#00e676"
C_GREEN_DIM = "#0d2e1a"
C_YELLOW    = "#ffd600"
C_RED       = "#ff1744"
C_RED_DIM   = "#2e0010"
C_BLUE      = "#2979ff"
C_BLUE_DIM  = "#0a1a3d"
C_TEXT      = "#e8e8e8"
C_TEXT_DIM  = "#555555"
C_TEXT_MED  = "#888888"


# =============================================================================
# CURL + COOKIES — método principal
# =============================================================================

def _extraer_cookies_cdp(port: int) -> dict:
    """Extrae todas las cookies de nike.cl desde Chrome via CDP."""
    try:
        import websocket
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/json", timeout=2
        ) as r:
            tabs = json.loads(r.read())

        tab = next((t for t in tabs
                    if t.get("type") == "page"
                    and "webSocketDebuggerUrl" in t), None)
        if not tab:
            return {}

        ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=5)
        ws.send(json.dumps({
            "id": 1,
            "method": "Network.getAllCookies",
            "params": {}
        }))

        import time
        deadline = time.time() + 5
        while time.time() < deadline:
            try:
                ws.settimeout(0.5)
                msg = json.loads(ws.recv())
                if msg.get("id") == 1:
                    cookies = msg.get("result", {}).get("cookies", [])
                    ws.close()
                    # Filtrar solo cookies de nike.cl
                    return {
                        c["name"]: c["value"]
                        for c in cookies
                        if "nike" in c.get("domain", "")
                    }
            except Exception:
                continue
        ws.close()
    except Exception:
        pass
    return {}


def _cookies_to_header(cookies: dict) -> str:
    """Convierte dict de cookies a string para curl."""
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def _buscar_con_curl(sku: str, cookies: dict) -> dict | None:
    """
    Busca SKU via curl con cookies reales de Chrome.
    Evita el 403 que Nike devuelve a requests de Python.
    """
    cookie_str = _cookies_to_header(cookies)

    urls = [
        f"https://www.nike.cl/api/catalog_system/pub/products/search?fq=skuId%3A{sku}&sc=1",
        f"https://www.nike.cl/api/catalog_system/pub/products/search?fq=skuId:{sku}&sc=1",
    ]

    for url in urls:
        try:
            cmd = [
                "curl", "-s", "-L",
                "--max-time", "8",
                "--connect-timeout", "5",
                "-H", f"Cookie: {cookie_str}",
                "-H", "Accept: application/json",
                "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "-H", "Referer: https://www.nike.cl/",
                "-H", "Origin: https://www.nike.cl",
                "-H", "Accept-Language: es-CL,es;q=0.9",
                url
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                # Windows: buscar curl en PATH
                shell=False
            )

            if result.returncode != 0 or not result.stdout.strip():
                continue

            data = json.loads(result.stdout)
            if isinstance(data, list) and data:
                return _parse_vtex_product(data[0])

        except subprocess.TimeoutExpired:
            continue
        except json.JSONDecodeError:
            continue
        except FileNotFoundError:
            # curl no está instalado
            return None
        except Exception:
            continue

    return None


def _buscar_con_cdp(sku: str, port: int) -> dict | None:
    """Fallback: búsqueda via CDP directo (fetch inyectado en browser)."""
    try:
        import websocket, time

        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/json", timeout=2
        ) as r:
            tabs = json.loads(r.read())

        tab = next((t for t in tabs
                    if t.get("type") == "page"
                    and "nike.cl" in t.get("url", "")
                    and "webSocketDebuggerUrl" in t), None) or \
              next((t for t in tabs
                    if t.get("type") == "page"
                    and t.get("url", "").startswith("http")
                    and "webSocketDebuggerUrl" in t), None)

        if not tab:
            return None

        js = f"""
        (() => {{
            return new Promise((resolve) => {{
                fetch('https://www.nike.cl/api/catalog_system/pub/products/search?fq=skuId%3A{sku}&sc=1', {{
                    credentials: 'include',
                    headers: {{'Accept': 'application/json'}}
                }})
                .then(r => r.json())
                .then(d => {{
                    if (Array.isArray(d) && d.length > 0)
                        resolve(JSON.stringify(d[0]));
                    else
                        resolve('NOT_FOUND');
                }})
                .catch(e => resolve('ERROR:' + e.message));
            }});
        }})();
        """

        ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=5)
        ws.send(json.dumps({
            "id": 77,
            "method": "Runtime.evaluate",
            "params": {"expression": js, "awaitPromise": True, "timeout": 8000}
        }))

        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                ws.settimeout(0.5)
                msg = json.loads(ws.recv())
                if msg.get("id") != 77:
                    continue
                val = msg.get("result", {}).get("result", {}).get("value", "") or ""
                ws.close()
                if val and val not in ("NOT_FOUND", "") and not val.startswith("ERROR"):
                    product = json.loads(val)
                    if isinstance(product, dict):
                        return _parse_vtex_product(product)
                return None
            except Exception:
                continue
        ws.close()
    except Exception:
        pass
    return None


def _buscar_producto_api(query: str, cdp_port: int = 0) -> dict:
    """
    Estrategia:
      1. Extraer cookies de Chrome (cualquier puerto abierto)
      2. Buscar via curl con esas cookies → sin 403
      3. Si curl no disponible → fallback CDP directo
    """
    import time

    query = query.strip()

    # Encontrar puertos Chrome activos
    puertos = []
    if cdp_port > 0:
        puertos.append(cdp_port)
    puertos += [p for p in range(9222, 9242) if p != cdp_port]

    chrome_port = None
    for port in puertos:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/json", timeout=0.5
            ) as r:
                tabs = json.loads(r.read())
                if any(t.get("type") == "page" for t in tabs):
                    chrome_port = port
                    break
        except Exception:
            continue

    if not chrome_port:
        return {
            "error": (
                "No hay Chrome abierto.\n"
                "Abre Nav con una cuenta primero."
            )
        }

    # Intentar curl + cookies
    cookies = _extraer_cookies_cdp(chrome_port)
    if cookies:
        result = _buscar_con_curl(query, cookies)
        if result:
            return result
        # curl falló o no está — intentar CDP
        result = _buscar_con_cdp(query, chrome_port)
        if result:
            return result
    else:
        # Sin cookies — intentar CDP directo
        result = _buscar_con_cdp(query, chrome_port)
        if result:
            return result

    return {
        "error": (
            f"SKU '{query}' no encontrado en Nike.cl.\n"
            "Verifica que el número sea correcto."
        )
    }


def _parse_vtex_product(product: dict) -> dict:
    """Parsea respuesta VTEX a formato interno."""
    name  = product.get("productName", "Producto")
    price = 0
    skus  = []

    for item in product.get("items", []):
        sku_id  = item.get("itemId", "")
        sellers = item.get("sellers", [{}])
        offer   = sellers[0].get("commertialOffer", {}) if sellers else {}
        stock   = offer.get("AvailableQuantity", 0)
        p       = offer.get("Price", 0)
        if p:
            price = p

        variations = {}
        for v in item.get("variations", []):
            if v.get("fieldValues"):
                variations[v["fieldName"]] = v["fieldValues"][0]

        talla = (
            variations.get("Talla M")
            or variations.get("Talla")
            or variations.get("Size")
            or item.get("name", "")
        )
        color = (
            variations.get("Cor")
            or variations.get("Color")
            or variations.get("Colour")
            or ""
        )

        skus.append({
            "sku":   sku_id,
            "talla": talla,
            "color": color,
            "stock": stock,
        })

    def _sort_key(s):
        try:
            return float(s["talla"].split()[0])
        except Exception:
            return 999

    skus.sort(key=_sort_key)

    return {
        "name":      name,
        "price":     price,
        "skus":      skus,
        "con_stock": sum(1 for s in skus if s["stock"] > 0),
        "total":     len(skus),
    }


def _darken(hex_color: str, factor: float = 0.7) -> str:
    try:
        h    = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
    except Exception:
        return hex_color


# =============================================================================
# EDITOR PRINCIPAL
# =============================================================================

class AccountEditor(ctk.CTkToplevel):

    def __init__(self, parent, account, manager, cdp_port: int = 0):
        super().__init__(parent)
        self.account  = account
        self.manager  = manager
        self.cdp_port = cdp_port

        self.title(f"Editar cuenta: {account.name}")
        self.geometry("820x750")
        self.minsize(760, 650)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        raw = getattr(account, "skus", None)
        if raw and isinstance(raw, list):
            self._selected_skus = [str(s) for s in raw if s]
        elif account.sku:
            self._selected_skus = [str(account.sku)]
        else:
            self._selected_skus = []

        self._sku_labels: dict[str, str] = {}
        saved = self._load_field("sku_labels")
        if isinstance(saved, dict):
            self._sku_labels = saved

        self._search_result: dict | None = None
        self._sku_btns: dict[str, tuple] = {}

        self._build()

    # =========================================================================
    # BUILD
    # =========================================================================

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        left = ctk.CTkScrollableFrame(self, fg_color=C_BG, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=(12, 6))

        right = ctk.CTkFrame(self, fg_color=C_PANEL, corner_radius=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=(12, 6))
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)

        save_bar = ctk.CTkFrame(self, fg_color=C_PANEL, height=56, corner_radius=0)
        save_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        save_bar.grid_propagate(False)
        ctk.CTkButton(
            save_bar, text="GUARDAR CAMBIOS",
            fg_color=C_GREEN_DIM, hover_color="#1a4d2e",
            text_color=C_GREEN, height=40,
            font=("Segoe UI Semibold", 13),
            command=self._save_and_close,
        ).pack(fill="x", padx=16, pady=8)

        self._build_left(left)
        self._build_right(right)

    def _lbl(self, parent, text, size=10, color=C_TEXT_MED, **kw):
        return ctk.CTkLabel(
            parent, text=text,
            font=("Segoe UI", size), text_color=color, **kw,
        )

    def _entry(self, parent, placeholder="", **kw):
        return ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            fg_color=C_ROW, border_color=C_BORDER, text_color=C_TEXT, **kw,
        )

    def _section(self, parent, title):
        ctk.CTkLabel(
            parent, text=title,
            font=("Segoe UI Semibold", 11), text_color=C_GREEN,
        ).pack(anchor="w", pady=(16, 2))
        ctk.CTkFrame(parent, fg_color=C_BORDER, height=1).pack(fill="x", pady=(0, 8))

    # =========================================================================
    # PANEL IZQUIERDO
    # =========================================================================

    def _build_left(self, parent):
        self._section(parent, "Identidad")

        self._lbl(parent, "Nombre visible en la tabla").pack(anchor="w")
        self._lbl(parent, "Si está vacío se muestra el email",
                  color=C_TEXT_DIM, size=9).pack(anchor="w", pady=(0, 3))
        self.display_name_entry = self._entry(parent, "Mi cuenta principal")
        self.display_name_entry.pack(fill="x", pady=(0, 10))
        dn = self._load_field("display_name")
        if dn:
            self.display_name_entry.insert(0, dn)

        self._lbl(parent, "Email Nike").pack(anchor="w")
        self.email_entry = self._entry(parent, "ejemplo@gmail.com")
        self.email_entry.pack(fill="x", pady=(0, 10))
        email = self._load_field("email") or self._load_field("nike_email")
        if email:
            self.email_entry.insert(0, email)

        self._section(parent, "SKUs seleccionados")
        self._lbl(parent, "Búscalos en el panel derecho o agrégalos manualmente",
                  color=C_TEXT_DIM, size=9).pack(anchor="w", pady=(0, 6))

        self._skus_display = ctk.CTkFrame(parent, fg_color=C_ROW, corner_radius=6)
        self._skus_display.pack(fill="x", pady=(0, 4))
        self._refresh_skus_display()

        manual_row = ctk.CTkFrame(parent, fg_color="transparent")
        manual_row.pack(fill="x", pady=(4, 0))
        self._manual_entry = self._entry(manual_row, "SKU manual: 191502")
        self._manual_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._manual_entry.bind("<Return>", lambda _: self._add_manual_sku())
        ctk.CTkButton(
            manual_row, text="+ Agregar", width=90, height=28,
            fg_color=C_GREEN_DIM, hover_color="#1a4d2e", text_color=C_GREEN,
            font=("Segoe UI", 10), command=self._add_manual_sku,
        ).pack(side="right")

        self._section(parent, "Configuración")

        self._lbl(parent, "Seller ID").pack(anchor="w")
        self.seller_entry = self._entry(parent, "1")
        self.seller_entry.pack(fill="x", pady=(0, 10))
        sv = getattr(self.account, "seller_id", None) or getattr(self.account, "seller", "1") or "1"
        self.seller_entry.insert(0, sv)

        self.auto_var = ctk.BooleanVar(value=self.account.auto_checkout)
        ctk.CTkCheckBox(
            parent, text="Auto Checkout",
            variable=self.auto_var, text_color=C_TEXT,
            checkmark_color=C_GREEN, fg_color=C_GREEN_DIM,
        ).pack(anchor="w", pady=(0, 10))

        self._section(parent, "Método de pago")

        pm = getattr(self.account, "payment_method", None) or getattr(self.account, "payment_mode", "transfer")
        self.payment_var = ctk.StringVar(value=pm)

        pay_frame = ctk.CTkFrame(parent, fg_color=C_ROW, corner_radius=6)
        pay_frame.pack(fill="x", pady=(0, 12))

        for text, val in [
            ("Transferencia banco / Fintoc", "transfer"),
            ("MercadoPago",                  "mercadopago"),
            ("Tarjeta de crédito",           "credit_card"),
            ("Tarjeta de débito",            "debit"),
            ("Manual",                       "manual"),
        ]:
            ctk.CTkRadioButton(
                pay_frame, text=text,
                variable=self.payment_var, value=val,
                command=self._on_payment, text_color=C_TEXT, fg_color=C_GREEN,
            ).pack(anchor="w", padx=12, pady=5)

        self._card_frame = ctk.CTkFrame(parent, fg_color=C_ROW, corner_radius=6)
        self._build_card_fields()
        self._on_payment()

    # ── SKUs ─────────────────────────────────────────────────────────────────

    def _refresh_skus_display(self):
        for w in self._skus_display.winfo_children():
            w.destroy()

        if not self._selected_skus:
            self._lbl(self._skus_display,
                      "Sin SKUs — agrega desde el buscador →",
                      color=C_TEXT_DIM).pack(padx=12, pady=10)
            return

        for sku in self._selected_skus:
            chip = ctk.CTkFrame(self._skus_display, fg_color=C_GREEN_DIM, corner_radius=4)
            chip.pack(fill="x", padx=8, pady=3)
            lbl_text = sku
            talla = self._sku_labels.get(sku, "")
            if talla:
                lbl_text += f"  ({talla})"
            ctk.CTkLabel(chip, text=lbl_text,
                         font=("Consolas", 11), text_color=C_GREEN).pack(side="left", padx=8, pady=4)
            ctk.CTkButton(
                chip, text="×", width=24, height=24,
                fg_color=C_RED_DIM, hover_color="#5c1f1f",
                text_color=C_RED, font=("Segoe UI", 11),
                command=lambda s=sku: self._remove_sku(s),
            ).pack(side="right", padx=4)

    def _add_manual_sku(self):
        val = self._manual_entry.get().strip()
        if val and val not in self._selected_skus:
            self._selected_skus.append(val)
            self._refresh_skus_display()
            self._refresh_grid_selection()
            self._manual_entry.delete(0, "end")

    def _remove_sku(self, sku: str):
        if sku in self._selected_skus:
            self._selected_skus.remove(sku)
        self._sku_labels.pop(sku, None)
        self._refresh_skus_display()
        self._refresh_grid_selection()

    # ── Tarjeta ──────────────────────────────────────────────────────────────

    def _build_card_fields(self):
        self._lbl(self._card_frame, "Datos de tarjeta",
                  size=11, color=C_TEXT).pack(anchor="w", padx=12, pady=(10, 4))
        card = self._load_card_data()
        fields = [
            ("Número",   "card_number",    "1234 5678 9012 3456"),
            ("Nombre",   "card_name",      "NOMBRE APELLIDO"),
            ("Mes exp.", "card_expiry_mm", "12"),
            ("Año exp.", "card_expiry_aa", "27"),
            ("CVV",      "card_cvv",       "123"),
            ("RUT",      "card_rut",       "12345678-9"),
        ]
        self._card_entries: dict[str, ctk.CTkEntry] = {}
        for label, key, ph in fields:
            self._lbl(self._card_frame, label, color=C_TEXT_MED).pack(anchor="w", padx=12)
            e = self._entry(self._card_frame, ph, show="*" if key == "card_cvv" else "")
            e.pack(fill="x", padx=12, pady=(2, 6))
            v = card.get(key, "")
            if v:
                e.insert(0, v)
            self._card_entries[key] = e

    def _on_payment(self):
        if self.payment_var.get() in ("credit_card", "debit"):
            self._card_frame.pack(fill="x", pady=(0, 12))
        else:
            self._card_frame.pack_forget()

    # =========================================================================
    # PANEL DERECHO — buscador
    # =========================================================================

    def _build_right(self, parent):
        header = ctk.CTkFrame(parent, fg_color=C_BORDER, height=40, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        self._lbl(header, "BUSCADOR DE PRODUCTO  (curl + cookies Chrome)",
                  size=9, color=C_TEXT_MED).pack(side="left", padx=12, pady=10)

        search_bar = ctk.CTkFrame(parent, fg_color="transparent")
        search_bar.grid(row=1, column=0, sticky="ew", padx=12, pady=(10, 6))
        search_bar.grid_columnconfigure(0, weight=1)

        self._search_entry = ctk.CTkEntry(
            search_bar,
            placeholder_text="SKU  (Ej: 191351)",
            fg_color=C_ROW, border_color=C_BORDER, text_color=C_TEXT,
            font=("Consolas", 12), height=36,
        )
        self._search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._search_entry.bind("<Return>", lambda _: self._buscar())

        self._btn_buscar = ctk.CTkButton(
            search_bar, text="Buscar", width=80, height=36,
            fg_color=C_BLUE_DIM, hover_color="#1a2a4d",
            text_color=C_BLUE, font=("Segoe UI Semibold", 11),
            command=self._buscar,
        )
        self._btn_buscar.grid(row=0, column=1)

        self._search_status = ctk.CTkLabel(
            parent, text="Ingresa un SKU — usa curl con cookies de Chrome",
            font=("Segoe UI", 9), text_color=C_TEXT_DIM,
        )
        self._search_status.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 4))

        self._result_area = ctk.CTkScrollableFrame(
            parent, fg_color="transparent",
            scrollbar_button_color=C_BORDER,
        )
        self._result_area.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def _buscar(self):
        import re
        query_raw = self._search_entry.get().strip()
        if not query_raw:
            return
        query = re.sub(r'[^0-9]', '', query_raw)
        if not query:
            self._search_status.configure(
                text=f"SKU inválido: '{query_raw}' — solo números", text_color=C_RED)
            return
        if query != query_raw:
            self._search_entry.delete(0, "end")
            self._search_entry.insert(0, query)

        self._search_status.configure(
            text=f"Buscando '{query}' via curl...", text_color=C_YELLOW)
        self._btn_buscar.configure(state="disabled", text="...")
        self._clear_results()

        def do():
            result = None
            try:
                result = _buscar_producto_api(query, cdp_port=self.cdp_port)
            except Exception as e:
                result = {"error": f"Error: {e}"}
            finally:
                try:
                    if self.winfo_exists():
                        r = result or {"error": "Sin resultado"}
                        self.after(0, lambda r=r: self._mostrar_resultado(r))
                except Exception:
                    pass

        threading.Thread(target=do, daemon=True, name="sku-search").start()

    def _clear_results(self):
        for w in self._result_area.winfo_children():
            w.destroy()
        self._sku_btns = {}

    def _mostrar_resultado(self, result: dict):
        try:
            if not self.winfo_exists():
                return
            if not self._btn_buscar.winfo_exists():
                return
        except Exception:
            return

        self._btn_buscar.configure(state="normal", text="Buscar")
        self._clear_results()

        if "error" in result:
            self._search_status.configure(text=result["error"], text_color=C_RED)
            return

        self._search_result = result
        skus      = result["skus"]
        con_stock = result["con_stock"]
        total     = result["total"]
        precio    = f"${result['price']:,.0f}".replace(",", ".") if result["price"] else ""

        self._search_status.configure(
            text=f"{result['name']}  ·  {total} tallas  ·  {con_stock} con stock  ·  {precio}",
            text_color=C_GREEN,
        )

        info = ctk.CTkFrame(self._result_area, fg_color=C_ROW, corner_radius=6)
        info.pack(fill="x", pady=(4, 8))
        self._lbl(info, result["name"], size=12, color=C_TEXT).pack(anchor="w", padx=12, pady=(8, 2))
        if precio:
            self._lbl(info, precio, size=13, color=C_GREEN).pack(anchor="w", padx=12, pady=(0, 4))
        self._lbl(info, f"{con_stock} de {total} tallas disponibles",
                  size=9, color=C_TEXT_MED).pack(anchor="w", padx=12, pady=(0, 8))

        self._lbl(self._result_area,
                  "Haz clic en una talla para agregarla/quitarla:",
                  color=C_TEXT_MED, size=9).pack(anchor="w", padx=4, pady=(0, 6))

        grid = ctk.CTkFrame(self._result_area, fg_color="transparent")
        grid.pack(fill="x")

        COLS = 4
        for i, sku_data in enumerate(skus):
            row_idx = i // COLS
            col_idx = i % COLS
            sku_id  = sku_data["sku"]
            talla   = sku_data["talla"]
            color   = sku_data["color"]
            stock   = sku_data["stock"]

            chip_text = talla or sku_id
            if color:
                chip_text += f"\n{color[:12]}"

            ya_sel = sku_id in self._selected_skus
            if ya_sel:
                bg, tc = C_GREEN_DIM, C_GREEN
            elif stock > 0:
                bg, tc = "#1a1a2e", C_BLUE
            else:
                bg, tc = "#1a0a0a", C_RED

            if stock == 0:
                chip_text += "\n✗ sin stock"

            btn = ctk.CTkButton(
                grid, text=chip_text,
                width=140, height=52,
                fg_color=bg, hover_color=_darken(bg),
                text_color=tc, font=("Segoe UI", 9),
                corner_radius=6,
                border_width=1 if ya_sel else 0,
                border_color=C_GREEN if ya_sel else "transparent",
                command=lambda sid=sku_id, t=talla: self._toggle_sku(sid, t),
            )
            btn.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="ew")
            grid.grid_columnconfigure(col_idx, weight=1)
            self._sku_btns[sku_id] = (btn, sku_data)

    def _toggle_sku(self, sku_id: str, talla: str):
        if sku_id in self._selected_skus:
            self._selected_skus.remove(sku_id)
            self._sku_labels.pop(sku_id, None)
        else:
            self._selected_skus.append(sku_id)
            if talla:
                self._sku_labels[sku_id] = talla
        self._refresh_grid_selection()
        self._refresh_skus_display()

    def _refresh_grid_selection(self):
        for sku_id, (btn, sku_data) in self._sku_btns.items():
            ya_sel = sku_id in self._selected_skus
            stock  = sku_data["stock"]
            if ya_sel:
                btn.configure(fg_color=C_GREEN_DIM, text_color=C_GREEN,
                               border_width=1, border_color=C_GREEN)
            else:
                bg = "#1a1a2e" if stock > 0 else "#1a0a0a"
                tc = C_BLUE if stock > 0 else C_RED
                btn.configure(fg_color=bg, text_color=tc, border_width=0)

    # =========================================================================
    # PERSISTENCIA
    # =========================================================================

    def _config_path(self) -> str:
        base = getattr(self.account, "account_path", None) or os.path.join("auth", self.account.name)
        return os.path.join(base, "config.json")

    def _load_field(self, key: str, default=""):
        try:
            with open(self._config_path(), "r", encoding="utf-8") as f:
                return json.load(f).get(key, default)
        except Exception:
            return default

    def _load_card_data(self) -> dict:
        try:
            with open(self._config_path(), "r", encoding="utf-8") as f:
                return json.load(f).get("card", {})
        except Exception:
            return {}

    def _save_and_close(self):
        skus = [s for s in self._selected_skus if s]
        if not skus:
            skus = [None]

        self.account.skus = skus
        self.account.sku  = skus[0]

        dn     = self.display_name_entry.get().strip()
        email  = self.email_entry.get().strip()
        seller = self.seller_entry.get().strip() or "1"
        pm     = self.payment_var.get()

        if hasattr(self.account, "payment_method"):
            self.account.payment_method = pm
        else:
            self.account.payment_mode = pm

        self.account.auto_checkout = self.auto_var.get()

        if hasattr(self.account, "seller_id"):
            self.account.seller_id = seller
        else:
            self.account.seller = seller

        try:
            cfg_path = self._config_path()
            existing = {}
            if os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)

            existing.update({
                "sku":           skus[0],
                "skus":          skus,
                "sku_labels":    self._sku_labels,
                "display_name":  dn,
                "email":         email,
                "nike_email":    email,
                "seller":        seller,
                "auto_checkout": self.account.auto_checkout,
                "payment_mode":  pm,
            })

            # Guardar tarjeta para credit_card Y debit
            if hasattr(self, "_card_entries") and self._card_entries:
                card_data = {k: e.get().strip() for k, e in self._card_entries.items()}
                if any(v for v in card_data.values()):
                    existing["card"] = card_data

            os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)

            label = dn or email or self.account.name
            print(f"[Editor] Guardado: {self.account.name} -> '{label}' SKUs={skus} pago={pm}")

        except Exception as e:
            print(f"[Editor] Error guardando: {e}")

        try:
            if self.manager:
                self.manager.save_accounts()
        except Exception:
            pass

        self.destroy()