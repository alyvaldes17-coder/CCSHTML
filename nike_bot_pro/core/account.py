from dataclasses import dataclass, field
from threading import Event, Thread
from datetime import datetime
from typing import Optional

from core.states import AccountState


@dataclass
class Account:
    name: str
    sku: Optional[str] = None
    seller: Optional[str] = None

    state: AccountState = AccountState.OFF

    # Runtime
    thread: Optional[Thread] = None
    start_time: Optional[datetime] = None
    last_heartbeat: Optional[float] = None
    
    # 4️⃣ MEJORA: Flag para prevenir doble PLAY (race condition)
    worker_running: bool = False

    # Path to account folder on disk (auth/<account>)
    account_path: Optional[str] = None

    # Control
    pause_event: Event = field(default_factory=Event)
    kill_event: Event = field(default_factory=Event)

    # Flags de comportamiento
    auto_checkout: bool = False
    payment_mode: str = "manual"  # por ejecución, no persistente

    # Retry / diagnóstico
    retries: int = 0
    max_retries: int = 3
    backoff_base: float = 3.0
    next_retry_at: Optional[float] = None
    last_error: Optional[str] = None
    last_error_ts: Optional[float] = None

    # last observed price after add_to_cart (in cents)
    last_price: Optional[int] = None

    # lifecycle
    completed: bool = False

    # Human-facing status for diagnostics/UI
    last_status: Optional[str] = None

    # Sesión (Fix: check_manual() accede acc.session)
    session: dict = field(default_factory=dict)
    session_valid: bool = False

    def is_active(self) -> bool:
        return self.state in (AccountState.RUNNING, AccountState.PAUSED)
