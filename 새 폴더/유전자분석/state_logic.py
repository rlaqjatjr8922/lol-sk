import copy
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ActionState:
    prev_action: str | None = None
    active_states: set = field(default_factory=set)
    recent_exited_states: set = field(default_factory=set)
    forced_next_actions: List[str] | None = None


def build_note_condition_map(condition_defs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    result = {}
    for item in condition_defs:
        note = item.get("note", "").strip()
        cond = item.get("condition", {})
        if note:
            result[note] = cond
    return result


def check_condition(cond: Dict[str, Any], state: ActionState, character_name: str) -> bool:
    ctype = cond.get("type")

    if ctype == "prev_action_required":
        allowed = cond.get("value", [])
        return state.prev_action in allowed

    elif ctype == "required_state":
        needed = cond.get("state", [])
        return all(s in state.active_states for s in needed)

    elif ctype == "forbidden_state":
        blocked = cond.get("state", [])
        return all(s not in state.active_states for s in blocked)

    elif ctype == "required_recent_state_exit":
        needed = cond.get("state")
        return needed in state.recent_exited_states

    elif ctype == "character_required":
        allowed = cond.get("value", [])
        return character_name in allowed

    elif ctype == "compound":
        all_conds = cond.get("all", [])
        return all(check_condition(x, state, character_name) for x in all_conds)

    elif ctype == "or":
        any_conds = cond.get("any", [])
        return any(check_condition(x, state, character_name) for x in any_conds)

    elif ctype == "action_forbidden":
        return False

    elif ctype == "not_implemented":
        return False

    elif ctype == "walk_prev_action_whitelist":
        allowed_prev = cond.get("allowed_prev_actions", [])
        return state.prev_action in allowed_prev

    elif ctype == "walk_prev_action_whitelist_inverse":
        forbidden_prev = cond.get("forbidden_prev_actions", [])
        return state.prev_action not in forbidden_prev

    elif ctype == "sequence_whitelist":
        return True

    elif ctype == "option_flag":
        return True

    elif ctype == "special_option":
        req_states = cond.get("requires_state", [])
        return all(s in state.active_states for s in req_states)

    return True


def check_sequence_whitelist(cond: Dict[str, Any], prev_action: str | None, current_action: str) -> bool:
    allowed_sequences = cond.get("allowed_sequences", [])
    if prev_action is None:
        return False
    return [prev_action, current_action] in allowed_sequences


def get_legal_action_candidates(
    character_name: str,
    char_action_table: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]],
    state: ActionState
) -> List[str]:
    candidates = []

    for action_name, action_info in char_action_table.items():
        legal_mark = action_info.get("legal", "").strip()
        notes = action_info.get("notes", "").strip()

        if legal_mark == "❌":
            continue

        if legal_mark == "✔":
            candidates.append(action_name)
            continue

        if legal_mark == "⚠":
            if notes == "-" or not notes:
                continue

            cond = note_condition_map.get(notes)
            if not cond:
                continue

            ctype = cond.get("type")
            ok = False

            if ctype == "sequence_whitelist":
                ok = check_sequence_whitelist(cond, state.prev_action, action_name)
            else:
                ok = check_condition(cond, state, character_name)

            if ok:
                if ctype == "option_flag":
                    candidates.append(f"{action_name}[{cond['name']}={cond.get('default', 0)}]")
                    for v in cond.get("allowed_values", []):
                        candidates.append(f"{action_name}[{cond['name']}={v}]")
                elif ctype == "special_option":
                    candidates.append(action_name)
                    for v in cond.get("allowed_values", []):
                        candidates.append(f"{action_name}[{cond['name']}={v}]")
                else:
                    candidates.append(action_name)

    if state.forced_next_actions:
        candidates = [x for x in candidates if x.split("[")[0] in state.forced_next_actions]

    return candidates


def update_state_after_action(
    state: ActionState,
    action: str,
    note_condition_map: Dict[str, Dict[str, Any]],
    char_action_table: Dict[str, Any]
) -> ActionState:
    new_state = copy.deepcopy(state)
    new_state.recent_exited_states = set()
    new_state.forced_next_actions = None

    base_action = action.split("[")[0]
    new_state.prev_action = base_action

    info = char_action_table.get(base_action, {})
    notes = info.get("notes", "").strip()

    if notes and notes != "-":
        cond = note_condition_map.get(notes)
        if cond:
            ctype = cond.get("type")
            if ctype == "special_option":
                next_required = cond.get("next_action_required")
                if next_required:
                    new_state.forced_next_actions = next_required

    return new_state


def is_individual_fully_legal(
    individual: Dict[str, List[str]],
    legal_actions_data: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]]
) -> bool:
    for ch, seq in individual.items():
        char_action_table = legal_actions_data[ch]
        state = ActionState()

        for act in seq:
            candidates = get_legal_action_candidates(
                character_name=ch,
                char_action_table=char_action_table,
                note_condition_map=note_condition_map,
                state=state
            )

            if act not in candidates:
                base = act.split("[")[0]
                cand_bases = [x.split("[")[0] for x in candidates]
                if base not in cand_bases:
                    return False

            state = update_state_after_action(
                state=state,
                action=act,
                note_condition_map=note_condition_map,
                char_action_table=char_action_table
            )

    return True