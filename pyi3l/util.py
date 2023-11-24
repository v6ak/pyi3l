def pcre_quote(s: str):
    return "".join(map(
        lambda c: f"\\{c}" if c in ".^$*+?()[{\\|" else c,
        s
    ))

def only_nonnone(d: dict):
    return dict(filter(lambda kv: kv[1] is not None, d.items()))
