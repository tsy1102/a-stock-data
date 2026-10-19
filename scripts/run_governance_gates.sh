#!/bin/sh
# run_governance_gates.sh — a-stock-data 治理套件闸门运行器
#
# 用途：本地 pre-commit 与 CI 共用，校验「field_registry.json 单一真相源 ↔ field_dict.md」
#       契约不被破坏。所有闸门均为只读（不改动工作树），除 --with-a7 的 A7 会重写审计报告。
#
# 默认运行 3 个只读闸门：
#   G1  scripts/registry_parity.py         原生 token + §零·B 投影；接受清单外差异仍失败
#   G3  scripts/gen_field_dict.py --check   markdown 幂等（与 field_dict.md 无差异）
#   P1  scripts/archive_field_preflight.py  归档契约预检（SECTION_MAP / 断链 / MAPPING 覆盖）
#
# --with-a7  额外运行 A7（scripts/verify_sync_check.py，会重写审计报告文件，
#            故默认不放入 pre-commit，仅用于 CI / 周期性全量核查）。
# --force    跳过「相关文件未改动则跳过」的短路逻辑，强制跑闸门（用于验证 / CI）。
#
# 当本次暂存改动未触及字典、注册表、接受差异清单或 docs/verify/ 时自动跳过，避免无关提交被拦。
#
# 如需指定 Python 解释器（项目要求系统 Python 3.12），设置环境变量 PYTHON，例如：
#   PYTHON=python3.12 scripts/run_governance_gates.sh

set -eu

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PY="${PYTHON:-python3}"

WITH_A7=0
FORCE=0
for _a in "$@"; do
  case "$_a" in
    --with-a7) WITH_A7=1 ;;
    --force)   FORCE=1 ;;
  esac
done

# 仅按暂存区内容判断是否需要运行，避免未暂存文件触发一个不会进入提交的结果。
RELEVANT="$(git diff --cached --name-only -- \
  docs/field_dict.md \
  docs/field_verification/field_registry.json \
  docs/field_verification/registry_parity_scope.json \
  docs/field_verification/registry_parity_accepted_debt.json \
  docs/verify 2>/dev/null || true)"

if [ "$FORCE" -eq 0 ] && [ -z "$RELEVANT" ]; then
  echo "[governance-gates] 未检测到 field_dict.md / field_registry.json / docs/verify 改动，跳过闸门。"
  exit 0
fi

if [ "$FORCE" -eq 1 ]; then
  echo "[governance-gates] --force：忽略改动检测，强制运行闸门。"
else
  echo "[governance-gates] 检测到暂存区相关改动，运行闸门："
  echo "$RELEVANT" | sed 's/^/  - /'
fi

# 所有检查器读取工作树文件；暂存相关文件若仍有未暂存差异，当前工作树就不等于提交快照。
# 直接失败并要求先 stage，防止用未提交内容误判 index。
if [ -n "$RELEVANT" ] && ! git diff --quiet -- \
  docs/field_dict.md \
  docs/field_verification/field_registry.json \
  docs/field_verification/registry_parity_scope.json \
  docs/field_verification/registry_parity_accepted_debt.json \
  docs/verify; then
  echo "[governance-gates] 相关文件存在未暂存改动；请先 git add，使工作树与提交快照一致。" >&2
  exit 1
fi

UNTRACKED_RELEVANT="$(git ls-files --others --exclude-standard -- \
  docs/field_dict.md \
  docs/field_verification/field_registry.json \
  docs/field_verification/registry_parity_scope.json \
  docs/field_verification/registry_parity_accepted_debt.json \
  docs/verify 2>/dev/null || true)"
if [ -n "$RELEVANT" ] && [ -n "$UNTRACKED_RELEVANT" ]; then
  echo "[governance-gates] 相关路径存在未跟踪文件，检查器无法代表提交快照；请先审阅并 git add。" >&2
  exit 1
fi

fail=0

run_gate() {
  _name="$1"; shift
  echo "==> [$_name] $*"
  if "$PY" "$@"; then
    echo "[$_name] PASS"
  else
    _code=$?
    echo "[$_name] FAIL (exit $_code)"
    fail=1
  fi
}

run_gate G1 scripts/registry_parity.py \
  --accepted-debt-manifest docs/field_verification/registry_parity_accepted_debt.json
run_gate G3 scripts/gen_field_dict.py --check
run_gate P1 scripts/archive_field_preflight.py

if [ "$WITH_A7" -eq 1 ]; then
  run_gate A7 scripts/verify_sync_check.py
fi

if [ "$fail" -ne 0 ]; then
  echo "[governance-gates] 未通过，提交/CI 中止。请先修复上述 FAIL 再提交。"
  exit 1
fi

echo "[governance-gates] 全部通过 ✅"
exit 0
