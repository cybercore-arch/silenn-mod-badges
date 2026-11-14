"""Применяет одобренную заявку. Использование: apply_issue.py <файл с JSON issue>. Печатает ответ для комментария."""
import json, re, sys, urllib.request
from common import ROOT, ID_RE, ACC_RE, CODE_RE, load, save, png_problem

def fields(body):
    parts = re.split(r"^### +(.+)$", body or "", flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}

def image_url(text):
    m = re.search(r"https://(?:github\.com/user-attachments/[^\s)\"']+|user-images\.githubusercontent\.com/[^\s)\"']+)", text)
    return m.group(0) if m else None

def main():
    issue = json.load(open(sys.argv[1], encoding="utf-8"))
    labels = {l["name"] for l in issue["labels"]}
    f = fields(issue["body"])
    if "new-badge" in labels:
        if "approved" not in labels: return "Нужно одобрение модератора (метка approved)."
        bid = f.get("Id значка", "")
        if not ID_RE.match(bid): return "Плохой id."
        cat = load("catalog.json")
        if any(b["id"] == bid for b in cat["badges"]): return "Такой id уже есть."
        url = image_url(f.get("Картинка", ""))
        if not url: return "Не нашёл картинку."
        raw = urllib.request.urlopen(url, timeout=30).read(200_000)
        pr = png_problem(raw)
        if pr: return "Картинка не подходит: " + pr
        (ROOT / "images" / f"{bid}.png").write_bytes(raw)
        cat["badges"].append({"id": bid, "title": f.get("Название", "")[:40], "author": f.get("Автор (ник)", "")[:40],
                              "description": f.get("Описание", "").replace("_No response_", "")[:200]})
        save("catalog.json", cat)
        return f"Значок `{bid}` добавлен в каталог."
    login = (issue.get("user") or {}).get("login", "")
    if "bind-account" in labels:
        if "approved" not in labels: return "Нужно одобрение модератора (метка approved)."
        acc, code = f.get("Id аккаунта TikTok", ""), f.get("Код из мода", "")
        if not ACC_RE.match(acc): return "Плохой id аккаунта."
        if not CODE_RE.match(code): return "Код не похож на код из мода."
        o = load("owners.json")
        if o["owners"].get(acc, login) != login: return "Аккаунт уже привязан к другому GitHub. Если GitHub потерян, напишите @silennwav в Telegram."
        o["owners"][acc] = login; save("owners.json", o)
        return f"Аккаунт {acc} привязан к @{login}. Теперь можно подавать «Надеть значок»."
    if "wear-badge" in labels:
        acc, bid = f.get("Id аккаунта TikTok", ""), f.get("Id значка из каталога", "")
        if not ACC_RE.match(acc): return "Плохой id аккаунта."
        owner = load("owners.json")["owners"].get(acc)
        if owner is None: return "Аккаунт не привязан. Сначала подайте заявку «Привязать аккаунт». Нет GitHub — напишите @silennwav в Telegram."
        if owner != login: return "Этот аккаунт привязан к другому GitHub. Потеряли свой — напишите @silennwav в Telegram."
        if not any(b["id"] == bid for b in load("catalog.json")["badges"]): return "Значка нет в каталоге."
        w = load("wearers.json"); w["users"][acc] = bid; save("wearers.json", w)
        return f"Аккаунт {acc} теперь носит `{bid}`."
    return "Этот тип заявок вручную: жалобы разбирает модератор."

print(main())
