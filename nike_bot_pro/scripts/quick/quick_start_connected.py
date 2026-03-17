#!/usr/bin/env python3
"""
quick_start_connected.py - Quick start para flujo conectado

Muestra comandos exactos para:
1. Setup LOGIN (una sola vez)
2. Ejecutar PLAY (single account)
3. Ejecutar PLAY (multi account)
4. Con UI (PlayIntegration)
"""

QUICK_START = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                        QUICK START - FLUJO CONECTADO                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

CONTRATO FINAL:
═════════════════════════════════════════════════════════════════════════════

[1] LOGIN crea .login_ok (marker de integridad)
[2] PLAY clona solo si .login_ok existe (no locks)
[3] PREFLIGHT valida sesion antes de drop
[4] Estados emitidos en tiempo real (UI actualiza)


PASO 1: SETUP LOGIN (una sola vez por cuenta)
═════════════════════════════════════════════════════════════════════════════

$ python login_runner.py cuenta2

Que pasa:
  1. Chrome abre profile_login
  2. Tu logueas manualmente en Nike
  3. Cierras Chrome
  4. Script verifica sesion (GET /mi-cuenta)
  5. Si OK -> crea .login_ok
  6. Si ERROR -> NO crea marca, PLAY bloqueado

Resultado:
  auth/cuenta2/.login_ok      (existe = sesion verificada)


PASO 2a: PLAY SINGLE ACCOUNT
═════════════════════════════════════════════════════════════════════════════

$ python play_runner.py cuenta2

Que pasa:
  1. clone_auth_to_run("cuenta2")
     - verifica .login_ok
     - clona profile_login -> profile_run
  2. preflight(profile_run)
     - verifica Nike reconoce sesion (headless)
     - si NO -> error + return
  3. handover humano
     - Chrome abierto visible
     - esperando input

Resultado:
  auth/cuenta2/profile_run/   (perfil limpio, listo para usar)


PASO 2b: PLAY MULTI ACCOUNT (PARALELO)
═════════════════════════════════════════════════════════════════════════════

$ python -c "from runtime.multiprocessing_runner import run_accounts_mp; run_accounts_mp(['cuenta1', 'cuenta2', 'cuenta3'])"

O desde Python:

from runtime.multiprocessing_runner import run_accounts_mp

accounts = ["cuenta1", "cuenta2", "cuenta3"]
run_accounts_mp(accounts)

Que pasa:
  Lanza 3 procesos en paralelo
  Cada uno:
    1. clone -> preflight -> backend (TODO) -> handover -> done
  Estados emitidos via print (o bus si integras UI)


PASO 3: INTEGRAR CON UI (CustomTkinter)
═════════════════════════════════════════════════════════════════════════════

En app.py:

from ui.app_integration_example import PlayIntegration

class AppUI:
    def __init__(self):
        self.play = PlayIntegration()  # Crea bus + listener
    
    def setup_play_button(self):
        play_button = CTkButton(
            text="PLAY",
            command=self.on_play_clicked
        )
        play_button.pack()
    
    def on_play_clicked(self):
        selected = self.table.get_selected_accounts()
        # Lanza en thread, no bloquea UI
        self.play.on_play_clicked(selected)
        # listener escucha estados en background
        # on_state_update actualiza tabla

Que pasa:
  1. Click PLAY
  2. launch_play_for_accounts(selected, bus)
  3. run_accounts_mp(selected, bus)
  4. Cada proceso emite: STARTING -> CLONING -> PREFLIGHT -> ...
  5. state_listener recibe estados
  6. on_state_update(user, state, msg)
  7. Tabla actualiza en tiempo real


MAPEO DE ARCHIVOS
═════════════════════════════════════════════════════════════════════════════

[LOGIN MASTER]
  └─ login_runner.py
     └─ .login_ok (marca)

[CLONE]
  └─ profile_manager_v2.py
     └─ clone_auth_to_run()

[PLAY SINGLE]
  └─ play_runner.py
     └─ preflight()

[PLAY MULTI]
  └─ runtime/multiprocessing_runner.py
     ├─ run_account()
     └─ run_accounts_mp()

[ESTADOS]
  ├─ runtime/process_states.py
  │  └─ ProcState (Enum)
  └─ runtime/state_bus.py
     └─ make_state_bus()

[UI]
  ├─ ui/state_listener.py
  │  └─ start_state_listener()
  ├─ ui/play_launcher.py
  │  └─ launch_play_for_accounts()
  └─ ui/app_integration_example.py
     └─ PlayIntegration


TESTING
═════════════════════════════════════════════════════════════════════════════

# Validar imports
python test_connected_flow.py

# Validar flujo
python login_runner.py test_user
python play_runner.py test_user

# Validar multiprocessing
python -c "from runtime.multiprocessing_runner import run_accounts_mp; run_accounts_mp(['cuenta2', 'cuenta3'])"


REGLAS (CRÍTICAS)
═════════════════════════════════════════════════════════════════════════════

1. Sin .login_ok -> no hay clone
2. Sin clone -> no hay preflight
3. Sin preflight OK -> no hay drop
4. profile_login nunca se toca por el bot
5. profile_run es descartable
6. Cada cuenta = 1 proceso independiente
7. Estados viven en Queue (multiprocessing safe)


SIGUIENTE PASO
═════════════════════════════════════════════════════════════════════════════

Agregar backend logic (tu codigo de ataque):

En runtime/multiprocessing_runner.py, replace:

    # BACKEND (TODO: aqui va tu logica)
    emit(bus, user, ProcState.BACKEND)
    # backend_run(user, profile_run)

Con:

    # BACKEND
    emit(bus, user, ProcState.BACKEND)
    backend_run(user, profile_run)  # tu funcion

Donde backend_run:
  - Abre profile_run con visible=True
  - Ejecuta magic link ATC (add to cart)
  - Monitorea precio
  - Lock cuando precio es correcto
  - Entrega a handover humano


═════════════════════════════════════════════════════════════════════════════
[✓] FLUJO CONECTADO - LISTO PARA PRODUCCION
═════════════════════════════════════════════════════════════════════════════
"""

print(QUICK_START)

if __name__ == "__main__":
    import sys
    
    # Mostrar comandos por argument
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        commands = {
            "login": "python login_runner.py cuenta2",
            "play-single": "python play_runner.py cuenta2",
            "play-multi": "python -c 'from runtime.multiprocessing_runner import run_accounts_mp; run_accounts_mp([\"cuenta1\", \"cuenta2\", \"cuenta3\"])'",
            "test": "python test_connected_flow.py",
        }
        
        if cmd in commands:
            print(f"Ejecuta: {commands[cmd]}")
        else:
            print(f"Comando desconocido: {cmd}")
            print(f"Disponibles: {', '.join(commands.keys())}")
