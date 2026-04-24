import os
import json
import random
import copy
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Any, Tuple

from state_logic import (
    ActionState,
    get_legal_action_candidates,
    update_state_after_action,
)
from dps_runner import evaluate_individual_dps


def distribute_tokens(total_tokens: int, party: List[str], main_dps_idx: int) -> Dict[str, int]:
    n = len(party)
    split = {ch: 1 for ch in party}

    remaining = total_tokens - n
    if remaining <= 0:
        return split

    max_per_char = total_tokens // 2
    main_char = party[main_dps_idx]

    main_extra = remaining // 2
    addable = max_per_char - split[main_char]
    actual_main_extra = min(main_extra, addable)

    split[main_char] += actual_main_extra
    remaining -= actual_main_extra

    others = [ch for i, ch in enumerate(party) if i != main_dps_idx]

    while remaining > 0:
        progressed = False

        for ch in others:
            if remaining <= 0:
                break
            if split[ch] < max_per_char:
                split[ch] += 1
                remaining -= 1
                progressed = True

        if remaining > 0 and split[main_char] < max_per_char:
            split[main_char] += 1
            remaining -= 1
            progressed = True

        if not progressed:
            break

    return split


def generate_character_sequence(
    character_name: str,
    token_count: int,
    legal_actions_data: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]]
) -> List[str]:
    char_action_table = legal_actions_data[character_name]
    state = ActionState()
    sequence = []

    for _ in range(token_count):
        candidates = get_legal_action_candidates(
            character_name=character_name,
            char_action_table=char_action_table,
            note_condition_map=note_condition_map,
            state=state
        )

        if not candidates:
            break

        chosen = random.choice(candidates)
        sequence.append(chosen)

        state = update_state_after_action(
            state=state,
            action=chosen,
            note_condition_map=note_condition_map,
            char_action_table=char_action_table
        )

    return sequence


def create_random_individual(
    party: List[str],
    token_split: Dict[str, int],
    legal_actions_data: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]]
) -> Dict[str, List[str]]:
    individual = {}

    for ch in party:
        individual[ch] = generate_character_sequence(
            character_name=ch,
            token_count=token_split[ch],
            legal_actions_data=legal_actions_data,
            note_condition_map=note_condition_map
        )

    return individual


def serialize_individual(individual: Dict[str, List[str]]) -> str:
    normalized = {k: individual[k] for k in sorted(individual.keys())}
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True)


def save_generation_snapshot(
    generation_idx: int,
    total_tokens: int,
    scored_population: List[Tuple[Dict[str, List[str]], float]],
    token_split: Dict[str, int],
    save_dir: str = "ga_logs"
) -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, save_dir)
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    for rank, (ind, dps) in enumerate(scored_population, start=1):
        rows.append({
            "rank": rank,
            "dps": dps,
            "token_split": token_split,
            "individual": ind
        })

    out_path = os.path.join(out_dir, f"T{total_tokens}_gen{generation_idx + 1}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def select_parents_weighted(
    scored_population: List[Tuple[Dict[str, List[str]], float]]
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    individuals = [x[0] for x in scored_population]
    scores = [max(x[1], 1.0) for x in scored_population]

    p1 = random.choices(individuals, weights=scores, k=1)[0]
    p2 = random.choices(individuals, weights=scores, k=1)[0]

    return copy.deepcopy(p1), copy.deepcopy(p2)


def crossover_individuals(
    parent1: Dict[str, List[str]],
    parent2: Dict[str, List[str]],
    token_split: Dict[str, int]
) -> Dict[str, List[str]]:
    child = {}

    for ch in parent1.keys():
        seq1 = parent1[ch]
        seq2 = parent2[ch]
        target_len = token_split[ch]

        if not seq1 and not seq2:
            child[ch] = []
            continue

        mode = random.choice(["by_character", "split"])

        if mode == "by_character":
            picked = seq1 if random.random() < 0.5 else seq2
            child[ch] = picked[:target_len]
        else:
            cut1 = random.randint(0, len(seq1)) if seq1 else 0
            cut2 = random.randint(0, len(seq2)) if seq2 else 0
            new_seq = seq1[:cut1] + seq2[cut2:]
            child[ch] = new_seq[:target_len]

    return child


def mutate_individual(
    individual: Dict[str, List[str]],
    mutation_prob: float,
    legal_actions_data: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]]
) -> Dict[str, List[str]]:
    new_ind = copy.deepcopy(individual)

    if random.random() >= mutation_prob:
        return new_ind

    target_char = random.choice(list(new_ind.keys()))
    old_seq = new_ind[target_char]

    if not old_seq:
        return new_ind

    idx = random.randrange(len(old_seq))
    state = ActionState()
    char_action_table = legal_actions_data[target_char]

    for act in old_seq[:idx]:
        state = update_state_after_action(
            state=state,
            action=act,
            note_condition_map=note_condition_map,
            char_action_table=char_action_table
        )

    candidates = get_legal_action_candidates(
        character_name=target_char,
        char_action_table=char_action_table,
        note_condition_map=note_condition_map,
        state=state
    )

    if candidates:
        old_seq[idx] = random.choice(candidates)

    new_ind[target_char] = old_seq
    return new_ind


def repair_individual(
    individual: Dict[str, List[str]],
    token_split: Dict[str, int],
    legal_actions_data: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]]
) -> Dict[str, List[str]]:
    repaired = {}

    for ch, seq in individual.items():
        target_len = token_split[ch]
        char_action_table = legal_actions_data[ch]
        state = ActionState()
        new_seq = []

        for act in seq:
            candidates = get_legal_action_candidates(
                character_name=ch,
                char_action_table=char_action_table,
                note_condition_map=note_condition_map,
                state=state
            )

            if not candidates:
                break

            base = act.split("[")[0]
            matched = None

            for cand in candidates:
                if cand == act or cand.split("[")[0] == base:
                    matched = cand
                    break

            if matched is None:
                matched = random.choice(candidates)

            new_seq.append(matched)

            state = update_state_after_action(
                state=state,
                action=matched,
                note_condition_map=note_condition_map,
                char_action_table=char_action_table
            )

            if len(new_seq) >= target_len:
                break

        while len(new_seq) < target_len:
            candidates = get_legal_action_candidates(
                character_name=ch,
                char_action_table=char_action_table,
                note_condition_map=note_condition_map,
                state=state
            )

            if not candidates:
                break

            picked = random.choice(candidates)
            new_seq.append(picked)

            state = update_state_after_action(
                state=state,
                action=picked,
                note_condition_map=note_condition_map,
                char_action_table=char_action_table
            )

        repaired[ch] = new_seq[:target_len]

    return repaired


def deduplicate_population(population: List[Dict[str, List[str]]]) -> List[Dict[str, List[str]]]:
    seen = set()
    unique = []

    for ind in population:
        key = serialize_individual(ind)
        if key not in seen:
            seen.add(key)
            unique.append(ind)

    return unique


def _evaluate_one_individual(args):
    ind, legal_actions_data, note_condition_map = args
    dps = evaluate_individual_dps(
        ind,
        legal_actions_data=legal_actions_data,
        note_condition_map=note_condition_map
    )
    return ind, dps


def evaluate_population_parallel(
    population: List[Dict[str, List[str]]],
    legal_actions_data: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]],
    max_workers: int | None = None
) -> List[Tuple[Dict[str, List[str]], float]]:
    if max_workers is None:
        max_workers = max(1, multiprocessing.cpu_count() - 1)

    tasks = [
        (ind, legal_actions_data, note_condition_map)
        for ind in population
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        scored = list(executor.map(_evaluate_one_individual, tasks))

    return scored


def evolve_one_T(
    party: List[str],
    main_dps_idx: int,
    total_tokens: int,
    legal_actions_data: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]],
    pop_size: int = 32,
    generations: int = 10,
    mutation_prob: float = 0.10,
    max_workers: int | None = None
):
    token_split = distribute_tokens(total_tokens, party, main_dps_idx)

    population = [
        create_random_individual(party, token_split, legal_actions_data, note_condition_map)
        for _ in range(pop_size)
    ]

    best_individual = None
    best_dps = -1.0

    for gen_idx in range(generations):
        scored = evaluate_population_parallel(
            population=population,
            legal_actions_data=legal_actions_data,
            note_condition_map=note_condition_map,
            max_workers=max_workers
        )

        for ind, dps in scored:
            if dps > best_dps:
                best_dps = dps
                best_individual = copy.deepcopy(ind)

        scored.sort(key=lambda x: x[1], reverse=True)

        save_generation_snapshot(
            generation_idx=gen_idx,
            total_tokens=total_tokens,
            scored_population=scored,
            token_split=token_split
        )

        survivor_count = max(1, int(pop_size * 0.20))
        survivors = scored[:survivor_count]

        elite_count = min(2, len(survivors))
        elites = [copy.deepcopy(x[0]) for x in survivors[:elite_count]]

        random_injection_count = max(1, int(pop_size * 0.15))
        new_population = []
        new_population.extend(elites)

        while len(new_population) < (pop_size - random_injection_count):
            p1, p2 = select_parents_weighted(survivors)
            child = crossover_individuals(p1, p2, token_split)
            child = repair_individual(child, token_split, legal_actions_data, note_condition_map)
            child = mutate_individual(child, mutation_prob, legal_actions_data, note_condition_map)
            child = repair_individual(child, token_split, legal_actions_data, note_condition_map)
            new_population.append(child)

        for _ in range(random_injection_count):
            rand_ind = create_random_individual(
                party,
                token_split,
                legal_actions_data,
                note_condition_map
            )
            new_population.append(rand_ind)

        new_population = deduplicate_population(new_population)

        while len(new_population) < pop_size:
            new_population.append(
                create_random_individual(
                    party,
                    token_split,
                    legal_actions_data,
                    note_condition_map
                )
            )

        population = new_population[:pop_size]

    return {
        "T": total_tokens,
        "token_split": token_split,
        "best_dps": best_dps,
        "best_individual": best_individual
    }


def search_best_rotation(
    party: List[str],
    main_dps_idx: int,
    legal_actions_data: Dict[str, Any],
    note_condition_map: Dict[str, Dict[str, Any]],
    start_T: int = 4,
    drop_threshold: float = 0.05,
    drop_streak_limit: int = 3,
    max_workers: int | None = None
):
    T = start_T
    global_best_dps = -1.0
    global_best_result = None
    drop_streak = 0
    history = []

    while True:
        result = evolve_one_T(
            party=party,
            main_dps_idx=main_dps_idx,
            total_tokens=T,
            legal_actions_data=legal_actions_data,
            note_condition_map=note_condition_map,
            pop_size=32,
            generations=10,
            mutation_prob=0.10,
            max_workers=max_workers
        )

        history.append(result)
        current_best = result["best_dps"]

        if current_best > global_best_dps:
            global_best_dps = current_best
            global_best_result = copy.deepcopy(result)
            drop_streak = 0
        else:
            if current_best <= global_best_dps * (1 - drop_threshold):
                drop_streak += 1
            else:
                drop_streak = 0

        if drop_streak >= drop_streak_limit:
            break

        T += 1

    return global_best_result, history