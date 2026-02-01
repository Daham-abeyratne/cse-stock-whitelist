from ..domain.types import Status
from ..util.timeutils import iso

def apply_transition(record, eval_result, d, settings):
    hard_pass, beta_ok, score, avg_turn = eval_result

    if hard_pass:
        record.state.fail_hard_rules_consecutive = 0
    else:
        record.state.fail_hard_rules_consecutive += 1

    if record.state.status == Status.TRACK:
        if hard_pass and score >= settings.candidate_min_score:
            record.state.status = Status.CANDIDATE
            record.state.candidated_on = iso(d)

    if record.state.status == Status.CANDIDATE:
        if hard_pass and beta_ok and score >= settings.whitelist_min_score:
            record.state.status = Status.WHITELIST
            record.state.whitelisted_on = iso(d)


    if record.state.fail_hard_rules_consecutive >= settings.churn_fail_hard_n:
        record.state.status = Status.CHURNED
        record.state.churned_on = iso(d)
