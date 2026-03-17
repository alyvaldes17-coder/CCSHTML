"""
🔒 AccountState UNIFICADO (Fix v10.1)

Fusiona core/account_state.py (6 estados) + core/states.py (18 estados)
en un SOLO enum canónico. Ambos archivos ahora apuntan al mismo objeto.
"""
from enum import Enum


class AccountState(str, Enum):
    # ── Estados básicos (usados por UI y bot_controller) ──
    NO_AUTH           = "NO_AUTH"
    LOGIN_IN_PROGRESS = "LOGIN_IN_PROGRESS"
    READY             = "READY"
    MONITORING        = "MONITORING"
    PRICE_LOCKED      = "PRICE_LOCKED"
    EXECUTING         = "EXECUTING"

    # ── Estados extendidos (usados por worker y manager) ──
    OFF               = "OFF"
    RUNNING           = "RUNNING"
    PAUSED            = "PAUSED"
    ERROR             = "ERROR"
    CART_LOCKED       = "CART_LOCKED"
    BANNED            = "BANNED"
    DISCOUNT_BLOCKED  = "DISCOUNT_BLOCKED"

    # ── Estados legacy (compatibilidad con manager/worker) ──
    WAITING_STABILITY         = "WAITING_STABILITY"
    PAYMENT_READY             = "PAYMENT_READY"
    MODE_B_LAUNCHING          = "MODE_B_LAUNCHING"
    MODE_B_RETRY              = "MODE_B_RETRY"
    WAITING_HUMAN_READY       = "WAITING_HUMAN_READY"
    PRICING_WAIT              = "PRICING_WAIT"
    PRICING_FROZEN            = "PRICING_FROZEN"
    PAYMENT_BANK_SELECTED     = "PAYMENT_BANK_SELECTED"
    BANK_MODAL_OPEN           = "BANK_MODAL_OPEN"
    AWAITING_BANK_CONFIRMATION = "AWAITING_BANK_CONFIRMATION"


# Estados donde botones están bloqueados
STATES_LOGIN_BLOCKED = {
    AccountState.LOGIN_IN_PROGRESS,
    AccountState.EXECUTING,
    AccountState.RUNNING,
}

STATES_PLAY_BLOCKED = {
    AccountState.NO_AUTH,
    AccountState.LOGIN_IN_PROGRESS,
    AccountState.MONITORING,
    AccountState.EXECUTING,
}


class GlobalState(str, Enum):
    IDLE     = "IDLE"
    RUNNING  = "RUNNING"
    PARTIAL  = "PARTIAL"
    STOPPING = "STOPPING"
    ERROR_GLOBAL = "ERROR_GLOBAL"
