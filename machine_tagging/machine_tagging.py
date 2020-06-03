import re
from typing import Dict, List


def find_entities(text: str, entities: Dict[str, List[str]]) -> Dict:
    """Find entities in text.

    Args:
        text: original text where to find entities
        entities: names of entities
    Returns:
        dictionary in spacy format
    """

    # flat_entities should be in lowercase and sorted by len
    text_lower = text.lower()

    tagged_ents = {"text": text, "ents": []}
    index_ranges = []

    for label, entities in entities.items():
        for entity in entities:
            entity_ranges = [(m.start(), m.end()) for m in
                             re.finditer(entity, text_lower)]
            if entity_ranges:
                ent_dicts = form_entity_dicts(text, label, entity,
                                              entity_ranges, index_ranges)
                index_ranges.extend(entity_ranges)

                tagged_ents["ents"].extend(ent_dicts)

    tagged_ents["ents"] = sorted(tagged_ents["ents"], key=lambda i: i['start'])
    return tagged_ents


def check_for_word(start: int, end: int, sentence: str) -> bool:
    """Check if given ranges is a word in sentence"""
    start_ok = bool(start - 1 < 0 or not sentence[start - 1].isalpha())
    end_ok = bool(end == len(sentence) or not sentence[end].isalpha())
    return start_ok and end_ok


def check_for_subentity(start: int, end: int, index_ranges: List[tuple]) -> bool:
    """Check if given ranges have intersection with list of index ranges"""
    for existed_start, existed_end in index_ranges:
        if (existed_start <= start <= existed_end or
                existed_start <= end <= existed_end):
            return True
    return False


def form_entity_dicts(text: str,
                      label: str,
                      entity: str,
                      entity_ranges: List[tuple],
                      index_ranges: List[tuple]) -> List[dict]:
    """Creates list with dictionaries of entities based on given entity ranges.
    Also check if there are some subentities in given ranges.

    Args:
        text:
        label: label for current entity
        entity: name of entity
        entity_ranges: current entity index ranges for whole text
            in format[(start, end), ...]
        index_ranges: index ranges for all previous entities
            in the same format as entity_ranges

    Returns:
        List of dictionaries of entities ranges and label
    """
    entities = []

    for start, end in entity_ranges:
        is_subentity = check_for_subentity(start, end, index_ranges)
        is_word = check_for_word(start, end, text)
        if not is_subentity and is_word:
            entities.append({"start": start,
                             "end": end,
                             "label": label,
                             "entity": entity})
    return entities
