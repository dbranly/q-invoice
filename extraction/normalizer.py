def enforce_object(data: dict, key: str):
    if key not in data or data[key] is None:
        data[key] = {}
    return data


def normalize_document(raw: dict) -> dict:
    # Document type
    raw.setdefault("document_type", "invoice")

    # Enforce object structure
    for field in ["dates", "parties", "amounts"]:
        raw = enforce_object(raw, field)

    # Parties
    raw["parties"].setdefault("vendor", {})
    raw["parties"].setdefault("customer", {})

    # Items
    raw.setdefault("items", [])

    return raw
