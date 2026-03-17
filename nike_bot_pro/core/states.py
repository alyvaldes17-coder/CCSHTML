"""
core/states.py — Re-export desde account_state unificado.
Todos los imports existentes tipo `from core.states import AccountState` siguen funcionando.
"""
from core.account_state import AccountState, GlobalState, STATES_LOGIN_BLOCKED, STATES_PLAY_BLOCKED

__all__ = ["AccountState", "GlobalState", "STATES_LOGIN_BLOCKED", "STATES_PLAY_BLOCKED"]
