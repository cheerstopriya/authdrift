from authdrift import Scenario, checkpoint


def build_scenario(safe=False):
    state = {"session_valid": True, "sent": []}
    def workflow():
        cached_access = state["session_valid"]
        checkpoint("authority_observed")
        if state["session_valid"] if safe else cached_access:
            state["sent"].append("protected-action")
    return Scenario("session-revocation", workflow,
                    lambda: state.update(session_valid=False),
                    lambda: not state["session_valid"], lambda: bool(state["sent"]))
