from authdrift import Scenario, checkpoint


def build_scenario(safe=False):
    state = {"eligible": True, "effects": []}
    def worker(ticket):
        checkpoint("authority_observed")
        if state["eligible"] if safe else ticket:
            state["effects"].append("worker-result")
    def coordinator():
        ticket = state["eligible"]
        worker(ticket)
    return Scenario("delegation-revocation", coordinator,
                    lambda: state.update(eligible=False),
                    lambda: not state["eligible"], lambda: bool(state["effects"]))
