import inspect
from time import monotonic, sleep


class InvalidExperiment(Exception):
    pass


def invoke(callback):
    value = callback()
    if inspect.isawaitable(value):
        if inspect.iscoroutine(value):
            value.close()
        raise InvalidExperiment("async callbacks are unsupported; supply a synchronous wrapper")
    return value


def predicate(callback):
    value = invoke(callback)
    if type(value) is not bool:
        raise InvalidExperiment("authoritative predicates must return bool")
    return value


def revoke_and_confirm(scenario, events):
    events.add("revocation_requested")
    invoke(scenario.revoke)
    deadline = monotonic() + scenario.confirmation_timeout
    while True:
        confirmed = predicate(scenario.revoked)
        if monotonic() > deadline:
            raise InvalidExperiment("revocation confirmation timed out")
        if confirmed:
            events.add("revocation_confirmed")
            return
        sleep(min(scenario.poll_interval, max(0, deadline - monotonic())))
