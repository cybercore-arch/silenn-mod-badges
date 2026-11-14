import json, re, struct, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
ID_RE = re.compile(r"^[a-z0-9-]{3,32}$")
ACC_RE = re.compile(r"^[0-9]{1,24}$")
CODE_RE = re.compile(r"^eq-[a-z0-9]{8}$")
MAX_BYTES, MAX_SIDE = 100 * 1024, 256

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def save(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def png_problem(raw):
    if len(raw) > MAX_BYTES: return "файл больше 100 КБ"
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR": return "это не PNG"
    w, h = struct.unpack(">II", raw[16:24])
    if w < 1 or h < 1 or w > MAX_SIDE or h > MAX_SIDE: return f"размер {w}x{h}, нужно до {MAX_SIDE}x{MAX_SIDE}"
    return None

def problems():
    out, ids = [], set()
    cat, wear = load("catalog.json"), load("wearers.json")
    for acc, login in load("owners.json").get("owners", {}).items():
        if not ACC_RE.match(acc) or not login: out.append(f"плохая привязка: {acc!r}")
    for b in cat.get("badges", []):
        i = b.get("id", "")
        if not ID_RE.match(i): out.append(f"плохой id: {i!r}"); continue
        if i in ids: out.append(f"повтор id: {i}")
        ids.add(i)
        if not b.get("title"): out.append(f"{i}: нет названия")
        p = ROOT / "images" / f"{i}.png"
        if not p.exists(): out.append(f"{i}: нет images/{i}.png"); continue
        pr = png_problem(p.read_bytes())
        if pr: out.append(f"{i}: {pr}")
    for acc, i in wear.get("users", {}).items():
        if not ACC_RE.match(acc): out.append(f"плохой id аккаунта: {acc!r}")
        if i not in ids: out.append(f"{acc}: значка {i!r} нет в каталоге")
    return out
