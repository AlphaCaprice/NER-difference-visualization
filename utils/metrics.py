from collections import namedtuple
from typing import Dict, List


MetricRecord = namedtuple("TableRecord",
                          ['text',
                           'machine_tagging_tp_amount',
                           'model_fp_amount',
                           'model_fn_amount',
                           'model_fp_entities',
                           'model_fn_entities'])


def collect_metrics(machine_record: Dict[str, List[Dict]],
                    model_record: Dict[str, List[Dict]]) -> MetricRecord:
    """Collects information about fp (false positives), fn (false negatives) entities
    based on difference in machine tagging and model predictions assuming that machine
    tagging is absolute true.

    Args:
        machine_record: spacy format dict {text: ..., ents: ...}
        model_record: spacy format dict {text: ..., ents: ...}

    Returns:
        namedtuple with collected information
    """

    text = machine_record["text"]
    machine_ents = machine_record["ents"]
    model_ents = model_record["ents"]

    machine_tp = [x["entity"] for x in machine_ents]

    fn_amount, fn_ents = find_entities_intersections(machine_ents, model_ents)
    fp_amount, fp_ents = find_entities_intersections(model_ents, machine_ents)

    return MetricRecord(text, len(machine_tp), fp_amount, fn_amount, fp_ents, fn_ents)


def find_entities_intersections(outer: List[Dict], inner: List[Dict]) -> tuple:
    """Finds entities intersections based on double looping through all entities.
    If finds any intersections, then everything ok, else that means it is false positive
    or false negative.

    Args:
        outer: entities that are searched in inner
        inner: where to search

    Returns:
        amount and names of entities
    """
    amount = 0
    ents = []
    for outer_ent in outer:
        for inner_ent in inner:
            # any entity intersections
            if (inner_ent["start"] <= outer_ent["start"] <= inner_ent["end"] or
                    inner_ent["start"] <= outer_ent["end"] <= inner_ent["end"]):
                break
        else:
            amount += 1
            ents.append(outer_ent["entity"])
    return amount, ents
