import sys
from common import problems
errs = problems()
for e in errs: print("ОШИБКА:", e)
print("ок" if not errs else f"ошибок: {len(errs)}")
sys.exit(1 if errs else 0)
