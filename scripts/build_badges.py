from common import load, save
cat, wear = load("catalog.json"), load("wearers.json")
users = {}
for acc, i in sorted(wear.get("users", {}).items()):
    users.setdefault(i, []).append(acc)
out = []
for b in cat.get("badges", []):
    out.append({"id": b["id"], "image": f"images/{b['id']}.png", "title": b.get("title", ""),
                "text": b.get("description", ""), "users": users.get(b["id"], [])})
save("badges.json", {"badges": out})
