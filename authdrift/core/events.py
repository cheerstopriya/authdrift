from time import monotonic_ns


class Events:
    def __init__(self):
        self.start = monotonic_ns()
        self.items = []

    def add(self, event, **details):
        self.items.append({"sequence": len(self.items), "event": event,
                           "t_ms": (monotonic_ns() - self.start) / 1_000_000,
                           **details})
