from authdrift import Scenario, checkpoint


def build_scenario(safe=False):
    state = {"approved": True, "refunds": []}
    def workflow():
        approved = state["approved"]
        checkpoint("authority_observed")
        if state["approved"] if safe else approved:
            state["refunds"].append({"order_id": 281, "amount": 50})
    return Scenario("refund-revocation", workflow,
                    lambda: state.update(approved=False),
                    lambda: not state["approved"], lambda: bool(state["refunds"]))
