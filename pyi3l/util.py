def pcre_quote(s: str):
    return "".join(map(
        lambda c: f"\\{c}" if c in ".^$*+?()[{\\|" else c,
        s
    ))

def only_nonnone(d: dict):
    return dict(filter(lambda kv: kv[1] is not None, d.items()))

def remove_keys(d, exclude):
    return {
        k: v
        for k, v in d.items()
        if k not in exclude
    }

def noneize_defaults(o, default):
    if o == default:
        return None
    else:
        return o
