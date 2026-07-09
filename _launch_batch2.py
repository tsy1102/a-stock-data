import subprocess, time, sys, os

env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

base = [sys.executable, "get_lng_report.py", "000100", "-o", "reports", "--no-upload"]
ful = [sys.executable, "_ful_with_timer.py"]

p1 = subprocess.Popen(base, env=env, stdout=open("_lng4.log","w",encoding="utf-8"), stderr=subprocess.STDOUT)
p2 = subprocess.Popen(ful, env=env, stdout=open("_ful4.log","w",encoding="utf-8"), stderr=subprocess.STDOUT)
print("launched lng + ful(with faulthandler timer), waiting 75s...", flush=True)
time.sleep(75)
for name, p in [("lng", p1), ("ful", p2)]:
    if p.poll() is None:
        print(f"  >> {name} STILL RUNNING (hung)", flush=True)
    else:
        print(f"  >> {name} exited code={p.returncode}", flush=True)
print("=== FUL tail (utf-8) ===", flush=True)
try:
    lines = open("_ful4.log", encoding="utf-8").read().splitlines()
    # 打印最后 25 行 + 含 Traceback/File/line 的行
    dump = [l for l in lines if any(k in l for k in ["Traceback","File \"","line ","Thread","get_history","get_strategic","requests","socket","connect","layer","tdx_"])]
    print("\n".join(dump[-40:]), flush=True)
except Exception as e:
    print(f"  read err {e}", flush=True)
for p in (p1, p2):
    if p.poll() is None:
        p.kill()
