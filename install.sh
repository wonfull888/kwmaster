#!/usr/bin/env bash
# kwmaster install.sh
# 自动建 .venv 并安装依赖。重复执行安全（幂等）。

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SKILL_DIR/.venv"
REQ_FILE="$SKILL_DIR/requirements.txt"

echo "[kwmaster] skill dir: $SKILL_DIR"

# 1) 检查 python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "[kwmaster] ERROR: python3 not found. Please install Python >= 3.10." >&2
  exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  echo "[kwmaster] ERROR: Python $PY_VERSION too old. Need >= 3.10." >&2
  exit 1
fi
echo "[kwmaster] python: $(which python3) ($PY_VERSION)"

# 2) 建 .venv
if [ ! -d "$VENV_DIR" ]; then
  echo "[kwmaster] creating venv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  echo "[kwmaster] venv exists, skip create"
fi

# 3) 升级 pip
"$VENV_DIR/bin/pip" install --quiet --upgrade pip

# 4) 装依赖
echo "[kwmaster] installing requirements"
"$VENV_DIR/bin/pip" install --quiet -r "$REQ_FILE"

# 5) 自检
echo "[kwmaster] verifying imports"
"$VENV_DIR/bin/python" -c "import pandas; print(f'  pandas={pandas.__version__}')"

echo "[kwmaster] install OK"
