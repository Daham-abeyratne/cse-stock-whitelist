from ..domain.types import Status
from ..util.timeutils import iso

def apply_transition(record, eval_result, d, settings):
    hard_pass, is_low_turnover, beta_ok, score = eval_result
    state = record.state
    day_iso = iso(d)

    # 1. Update Failure Counters
    if hard_pass:
        state.fail_hard_rules_consecutive = 0
    else:
        state.fail_hard_rules_consecutive += 1
        
    if is_low_turnover:
        state.avg_turnover_below_threshold_consecutive += 1
    else:
        state.avg_turnover_below_threshold_consecutive = 0

    # 2. RESURRECTION: CHURNED -> CANDIDATE
    if state.status == Status.CHURNED:
        candidate_eligible = (not settings.beta_required_for_candidate) or beta_ok
        if hard_pass and candidate_eligible and score >= settings.candidate_min_score:
            state.status = Status.CANDIDATE
            state.candidated_on = day_iso
            state.churned_on = None

    # 3. INITIAL TRACKING: TRACK -> CANDIDATE
    if state.status == Status.TRACK:
        candidate_eligible = (not settings.beta_required_for_candidate) or beta_ok
        if hard_pass and candidate_eligible and score >= settings.candidate_min_score:
            state.status = Status.CANDIDATE
            state.candidated_on = day_iso

    # 4. PROMOTION & DOWNGRADE: CANDIDATE <-> WHITELIST
    if state.status == Status.CANDIDATE:
        whitelist_eligible = (not settings.beta_required_for_whitelist) or beta_ok
        if hard_pass and whitelist_eligible and score >= settings.whitelist_min_score:
            state.status = Status.WHITELIST
            state.whitelisted_on = day_iso
    elif state.status == Status.WHITELIST:
        if score < settings.whitelist_min_score:
            # Downgrade to candidate
            state.status = Status.CANDIDATE
            state.whitelisted_on = None

    # 5. DOWNGRADE: CANDIDATE -> TRACK
    if state.status == Status.CANDIDATE:
        if score < settings.candidate_min_score:
            state.status = Status.TRACK
            state.candidated_on = None

    # 6. THE EXIT: Any active state -> CHURNED
    if (state.fail_hard_rules_consecutive >= settings.churn_fail_hard_n) or \
       (state.avg_turnover_below_threshold_consecutive >= settings.churn_low_turn_n):
        if state.status != Status.CHURNED:
            state.status = Status.CHURNED
            state.churned_on = day_iso