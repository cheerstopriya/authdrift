from contextvars import ContextVar

_hook = ContextVar("authdrift_checkpoint", default=None)


def checkpoint(name: str):
    """Pause this synchronous workflow for the active experiment's injection.

    Outside an experiment this is a no-op. Thread/process propagation is not
    automatic; a workflow must join all consequential work before returning.
    """
    hook = _hook.get()
    if hook is not None:
        hook(name)
