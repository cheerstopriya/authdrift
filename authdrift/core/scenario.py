from dataclasses import dataclass
from typing import Callable
import math


@dataclass
class Scenario:
    name: str
    run: Callable[[], None]
    revoke: Callable[[], None]
    revoked: Callable[[], bool]
    committed: Callable[[], bool]
    trigger: str = "authority_observed"
    reset: Callable[[], None] | None = None
    confirmation_timeout: float = 1.0
    poll_interval: float = 0.001

    def __post_init__(self):
        if not self.name or not self.trigger:
            raise ValueError("name and trigger must be nonempty")
        for value in (self.confirmation_timeout, self.poll_interval):
            if not math.isfinite(value) or value <= 0:
                raise ValueError("timeouts and polling intervals must be finite and positive")
