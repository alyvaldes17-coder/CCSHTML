# INTEGRACION EXACTA EN app.py (CustomTkinter)

## Cambios Necesarios (MINIMOS)

Solo necesitas agregar 5 lineas de codigo en app.py para conectar PLAY.

---

## 1. IMPORTS (agregar al top)

```python
# Agregar estas lineas al inicio de app.py
from runtime.state_bus import make_state_bus
from ui.play_launcher import launch_play_for_accounts
from ui.state_listener import start_state_listener
```

---

## 2. INICIALIZACION (en __init__)

```python
class AppUI:
    def __init__(self):
        self.window = ctk.CTk()
        # ... otros inits ...
        
        # AGREGAR ESTO:
        self.bus = make_state_bus()
        start_state_listener(self.bus, self.on_state_update)
```

---

## 3. CALLBACK PARA ESTADOS

```python
class AppUI:
    # ... otros metodos ...
    
    # AGREGAR ESTO:
    def on_state_update(self, user: str, state: str, msg: str = ""):
        """
        Llamado cuando hay cambio de estado (desde listener)
        
        Actualiza tabla con: usuario, estado, color, mensaje
        """
        print(f"[STATE] {user}: {state} ({msg})")
        
        # TODO: actualizar tabla
        # self.table.update_row(user, state, msg)
        # self.table.set_row_color(user, self.state_to_color(state))
```

---

## 4. MAPEO DE COLORES (opcional)

```python
class AppUI:
    # ... otros metodos ...
    
    # AGREGAR ESTO:
    def state_to_color(self, state: str):
        """Mapea estado a color de tabla"""
        colors = {
            "STARTING": "#FFE5B4",      # peach
            "CLONING": "#87CEEB",       # light blue (spinner)
            "PREFLIGHT": "#87CEEB",     # light blue
            "BACKEND": "#FFC0CB",       # pink
            "HANDOVER": "#FFD700",      # gold
            "WAITING_HUMAN": "#FF6347", # rojo oscuro
            "DONE": "#90EE90",          # light green
            "ERROR": "#FF4444",         # rojo
        }
        return colors.get(state, "#FFFFFF")  # default white
```

---

## 5. BOTON PLAY (reemplazar existente)

```python
class AppUI:
    def setup_buttons(self):
        # ... otros botones ...
        
        # REEMPLAZAR ESTO:
        play_button = ctk.CTkButton(
            master=self.button_frame,
            text="PLAY",
            command=self.on_play_button
        )
        play_button.pack(side="left", padx=5)
    
    # AGREGAR ESTA FUNCION:
    def on_play_button(self):
        """
        Boton PLAY presionado
        
        - Obtiene cuentas seleccionadas
        - Lanza multiprocessing (no bloquea UI)
        - listener actualiza tabla en tiempo real
        """
        selected = self.table.get_selected_accounts()
        if not selected:
            print("[UI] Sin cuentas seleccionadas")
            return
        
        print(f"[UI] Lanzando PLAY para: {selected}")
        
        # Lanza en thread para NO bloquear UI
        import threading
        t = threading.Thread(
            target=launch_play_for_accounts,
            args=(selected, self.bus),
            daemon=True
        )
        t.start()
        
        # state_listener escucha automaticamente
        # on_state_update actualiza tabla
```

---

## Ejemplo Completo (app.py)

```python
#!/usr/bin/env python3
import customtkinter as ctk
import threading
from runtime.state_bus import make_state_bus
from ui.play_launcher import launch_play_for_accounts
from ui.state_listener import start_state_listener


class AppUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Nike Bot Pro")
        
        # NUEVA: State bus para multiprocessing
        self.bus = make_state_bus()
        start_state_listener(self.bus, self.on_state_update)
        
        # Crear tabla
        self.table = AccountTable(self.window)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear botones
        self.setup_buttons()
    
    def setup_buttons(self):
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # LOGIN button
        login_btn = ctk.CTkButton(
            master=button_frame,
            text="LOGIN",
            command=self.on_login_button
        )
        login_btn.pack(side="left", padx=5)
        
        # PLAY button (NUEVO)
        play_btn = ctk.CTkButton(
            master=button_frame,
            text="PLAY",
            command=self.on_play_button,
            fg_color="green"
        )
        play_btn.pack(side="left", padx=5)
    
    def on_login_button(self):
        """TODO: Login logic"""
        pass
    
    def on_play_button(self):
        """PLAY presionado"""
        selected = self.table.get_selected_accounts()
        if not selected:
            print("[UI] Sin cuentas seleccionadas")
            return
        
        print(f"[UI] Lanzando PLAY para: {selected}")
        
        # Lanzar en thread (no bloquea)
        t = threading.Thread(
            target=launch_play_for_accounts,
            args=(selected, self.bus),
            daemon=True
        )
        t.start()
    
    def on_state_update(self, user: str, state: str, msg: str = ""):
        """
        Callback cuando hay cambio de estado
        
        Aqui actualizas la tabla
        """
        print(f"[STATE] {user}: {state} ({msg})")
        
        # TODO: actualizar tabla
        # self.table.update_row(user, state)
        # self.table.set_row_color(user, self.state_to_color(state))
    
    def state_to_color(self, state: str):
        """Mapea estado a color"""
        colors = {
            "STARTING": "#FFE5B4",
            "CLONING": "#87CEEB",
            "PREFLIGHT": "#87CEEB",
            "BACKEND": "#FFC0CB",
            "HANDOVER": "#FFD700",
            "WAITING_HUMAN": "#FF6347",
            "DONE": "#90EE90",
            "ERROR": "#FF4444",
        }
        return colors.get(state, "#FFFFFF")
    
    def run(self):
        self.window.mainloop()


class AccountTable:
    """Tabla de cuentas (dummy)"""
    def __init__(self, master):
        self.master = master
        self.frame = ctk.CTkFrame(master)
        self.frame.pack(fill="both", expand=True)
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def get_selected_accounts(self):
        # TODO: obtener seleccionadas de la tabla
        return ["cuenta2", "cuenta3"]


if __name__ == "__main__":
    app = AppUI()
    app.run()
```

---

## Paso a Paso (Integracion)

### 1. Agregar imports (3 lineas)

```python
from runtime.state_bus import make_state_bus
from ui.play_launcher import launch_play_for_accounts
from ui.state_listener import start_state_listener
```

### 2. Crear bus en __init__ (2 lineas)

```python
self.bus = make_state_bus()
start_state_listener(self.bus, self.on_state_update)
```

### 3. Agregar callback (5 lineas)

```python
def on_state_update(self, user: str, state: str, msg: str = ""):
    print(f"[STATE] {user}: {state} ({msg})")
    # self.table.update_row(user, state)
```

### 4. Reemplazar boton PLAY (10 lineas)

```python
def on_play_button(self):
    selected = self.table.get_selected_accounts()
    if not selected:
        return
    
    t = threading.Thread(
        target=launch_play_for_accounts,
        args=(selected, self.bus),
        daemon=True
    )
    t.start()
```

---

## Total: 20 lineas de codigo

Eso es todo lo que necesitas para conectar el flujo.

---

## Flujo Resultante (UI)

```
Click PLAY
  ↓
on_play_button()
  ↓
launch_play_for_accounts(selected, bus)
  ↓
run_accounts_mp(selected, bus)
  ↓
  ├─ Process 1: run_account("cuenta1", bus)
  │   └─ emit(bus, "cuenta1", STARTING)
  │   └─ emit(bus, "cuenta1", CLONING)
  │   └─ ... DONE/ERROR
  │
  └─ Process 2: run_account("cuenta2", bus)
      └─ ... mismo
  ↓
state_listener escucha bus (background thread)
  ↓
on_state_update(user, state, msg)
  ↓
self.table.update_row(user, state)
  ↓
UI actualiza en tiempo real
```

---

## Checklist

- [ ] Agregar imports (3 lineas)
- [ ] Crear bus en __init__ (2 lineas)
- [ ] Agregar on_state_update (5 lineas)
- [ ] Reemplazar on_play_button (10 lineas)
- [ ] Implementar table.update_row (UI specific)
- [ ] Implementar table.get_selected_accounts (UI specific)
- [ ] Test: Click PLAY → ver estados en tabla
- [ ] Test: Multi-account simultáneo
- [ ] Test: Estados en tiempo real (no lag)

---

**Tiempo de integracion:** 5 minutos  
**Lineas de codigo:** 20 (minimas)  
**Complejidad:** CERO (solo glue)
