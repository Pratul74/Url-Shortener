DICT_METRICS = ("country", "city", "browser", "os", "device")


def parse_hash(hashes: dict) -> dict:
    result = {"total_clicks": int(hashes.get("total_clicks") or 0)}
    result.update({m: {} for m in DICT_METRICS})
    for key, value in hashes.items():
        if key == "total_clicks" or ":" not in key:
            continue
        category, name = key.split(":", 1)
        if category in DICT_METRICS:
            result[category][name] = result[category].get(name, 0) + int(value)
    return result


def merge_counts(existing: dict | None, incoming: dict | None) -> dict:
    merged = dict(existing or {})
    for key, value in (incoming or {}).items():
        merged[key] = merged.get(key, 0) + int(value)
    return merged