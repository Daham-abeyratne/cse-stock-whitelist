from ..domain.types import Status
from ..util.timeutils import iso

def apply_transition(record, eval_result, d, settings):
    hard_pass, beta_ok, score, avg_turn = eval_result
    state = record.state
    day_iso = iso(d)

    # 1. Update Failure Counter
    if hard_pass:
        state.fail_hard_rules_consecutive = 0
    else:
        state.fail_hard_rules_consecutive += 1

    # 2. RESURRECTION: CHURNED -> CANDIDATE
    # If the stock was dead, but just appeared in Top 10 and passed rules
    if state.status == Status.CHURNED:
        if hard_pass and score >= settings.candidate_min_score:
            state.status = Status.CANDIDATE
            state.candidated_on = day_iso
            state.churned_on = None  # Clear the "death date"
            # Note: We don't return here so it can be promoted to Whitelist same-day if score is 8+

    # 3. INITIAL TRACKING: TRACK -> CANDIDATE
    if state.status == Status.TRACK:
        if hard_pass and score >= settings.candidate_min_score:
            state.status = Status.CANDIDATE
            state.candidated_on = day_iso

    # 4. PROMOTION: CANDIDATE -> WHITELIST
    if state.status == Status.CANDIDATE:
        if hard_pass and beta_ok and score >= settings.whitelist_min_score:
            state.status = Status.WHITELIST
            state.whitelisted_on = day_iso

    # 5. THE EXIT: Any active state -> CHURNED
    # If it fails hard rules too many times, it goes to the "waiting room"
    if state.fail_hard_rules_consecutive >= settings.churn_fail_hard_n:
        # Only set status to churned if it wasn't already (prevents resetting churned_on date)
        if state.status != Status.CHURNED:
            state.status = Status.CHURNED
            state.churned_on = day_iso