"""Parser for the Exp 5 'edits' DSL. Only the LAST ```edits block of a reply is read."""
import ast, re
import numpy as np

SHAPES = {"W1": (600, 32), "b1": (32,), "W2": (32, 32), "b2": (32,), "W3": (32, 6), "b3": (6,)}
NPZ_KEYS = {"W1": "actor/dense1/kernel", "b1": "actor/dense1/bias", "W2": "actor/dense2/kernel",
            "b2": "actor/dense2/bias", "W3": "actor/logits/kernel", "b3": "actor/logits/bias"}
STMT = re.compile(r"^(W1|b1|W2|b2|W3|b3)\s*\[([^\]]*)\]\s*(=|\*=|\+=|-=)\s*(.+)$", re.S)
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def zero_net():
    return {k: np.zeros(s, np.float32) for k, s in SHAPES.items()}


def find_last_block(text):
    """Return (block_text, cut_off) for the last ```edits block, or (None, False)."""
    opens = [m for m in re.finditer(r"^[ \t]*```[ \t]*edits[ \t]*$", text, re.M)]
    if not opens:
        return None, False
    start = opens[-1].end()
    close = re.search(r"^[ \t]*```[ \t]*$", text[start:], re.M)
    if close is None:
        return text[start:], True
    return text[start:start + close.start()], False


def _index(spec, shape):
    parts = [p.strip() for p in spec.split(",")]
    if len(parts) != len(shape):
        raise ValueError(f"index has {len(parts)} axes, tensor has {len(shape)}")
    idx = []
    for p, n in zip(parts, shape):
        if ":" in p:
            f = p.split(":")
            if len(f) > 3:
                raise ValueError(f"bad slice {p!r}")
            vals = []
            for x in f:
                x = x.strip()
                if x == "":
                    vals.append(None)
                elif re.fullmatch(r"-?\d+", x):
                    vals.append(int(x))
                else:
                    raise ValueError(f"bad slice {p!r}")
            if len(vals) == 3 and vals[2] == 0:
                raise ValueError("zero step")
            sl = slice(*vals)
            if len(range(*sl.indices(n))) == 0:
                raise ValueError(f"empty slice {p!r}")
            idx.append(sl)
        else:
            if not re.fullmatch(r"-?\d+", p):
                raise ValueError(f"bad index {p!r}")
            i = int(p)
            if not -n <= i < n:
                raise ValueError(f"index {i} out of range {n}")
            idx.append(i)
    return tuple(idx)


def _value(s):
    s = s.strip()
    if re.fullmatch(NUM, s):
        return float(s)
    if not re.fullmatch(r"[\[\]\s,0-9eE.+\-]*", s):
        raise ValueError(f"bad value {s[:40]!r}")
    v = ast.literal_eval(s)
    a = np.array(v, dtype=np.float64)  # raises on ragged lists
    if a.dtype == object:
        raise ValueError("ragged list")
    return a


def statements(block):
    """Split block into logical statements (joining lines while brackets are open)."""
    out, buf, depth, start = [], [], 0, None
    for ln, raw in enumerate(block.splitlines(), 1):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not buf:
            start = ln
        buf.append(line.strip())
        depth += line.count("[") - line.count("]")
        if depth <= 0:
            out.append((start, " ".join(buf)))
            buf, depth = [], 0
    if buf:
        out.append((start, " ".join(buf)))
    return out


def apply_edits(text, net=None):
    net = zero_net() if net is None else net
    block, cut = find_last_block(text)
    rep = {"block": block is not None, "statements": 0, "applied": 0, "entries_written": 0,
           "errors": [], "cut_off": cut}
    if block is None:
        return net, rep
    stmts = statements(block)
    rep["statements"] = len(stmts)
    for ln, st in stmts:
        try:
            m = STMT.match(st)
            if not m:
                raise ValueError("unrecognised statement")
            name, spec, op, val = m.groups()
            t = net[name]
            idx = _index(spec, t.shape)
            tgt = t[idx]
            v = _value(val)
            tshape = np.shape(tgt)
            if isinstance(v, np.ndarray):
                if v.shape != tshape:
                    if v.size == int(np.prod(tshape)) and np.squeeze(v).shape == tuple(d for d in tshape if d != 1):
                        v = v.reshape(tshape)
                    else:
                        raise ValueError(f"value shape {v.shape} != target shape {tshape}")
            if not np.all(np.isfinite(v)) or np.any(np.abs(v) > 1e6):
                raise ValueError("value out of range")
            if op == "=":
                new = np.broadcast_to(v, tshape)
            elif op == "*=":
                new = tgt * v
            elif op == "+=":
                new = tgt + v
            else:
                new = tgt - v
            t[idx] = new
            rep["applied"] += 1
            rep["entries_written"] += int(np.prod(tshape))
        except Exception as e:  # skip unreadable statement
            rep["errors"].append({"line": ln, "stmt": st[:120], "error": str(e)})
    return net, rep


def net_stats(net):
    nz = {k: int(np.count_nonzero(v)) for k, v in net.items()}
    return {"nonzero": nz, "nonzero_total": sum(nz.values()),
            "max_abs": {k: float(np.abs(v).max()) for k, v in net.items()}}


def save_npz(net, path):
    np.savez(path, **{NPZ_KEYS[k]: v.astype(np.float32) for k, v in net.items()})


def load_npz(path):
    d = np.load(path)
    return {k: d[NPZ_KEYS[k]].astype(np.float32) for k in SHAPES}
