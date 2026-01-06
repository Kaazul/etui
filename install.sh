#!/usr/bin/env bash
# Installs all necessary tools (uv, pre-commit), syncs the uv venv, installs the project
# itself in editable mode.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing eTUI project from: $PROJECT_ROOT"

# ------------------------------------------------------------
# 1. Ensure uv is installed
# ------------------------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
    echo "==> uv not found, installing..."

    if command -v curl >/dev/null 2>&1; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        echo "ERROR: Neither curl nor wget is available."
        exit 1
    fi

    # uv installs into ~/.cargo/bin
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "==> uv already installed"
fi

# ------------------------------------------------------------
# 2. Sync dependencies
# ------------------------------------------------------------
cd "$PROJECT_ROOT"
echo "==> Syncing dependencies"
uv sync

# ------------------------------------------------------------
# 3. Ensure pre-commit is installed
# ------------------------------------------------------------
if ! command -v pre-commit >/dev/null 2>&1; then
    echo "==> Installing pre-commit"
    uv pip install pre-commit
else
    echo "==> pre-commit already installed"
fi

uv run pre-commit install

# ------------------------------------------------------------
# 4. Install project (Python-native launcher)
# ------------------------------------------------------------
echo "==> Installing project in editable mode"
uv pip install -e .

# ------------------------------------------------------------
# 5. Add etui shell function (usage convenience)
# ------------------------------------------------------------
BASHRC="$HOME/.bashrc"

ETUI_FUNCTION="
etui() (
    cd \"$PROJECT_ROOT\" || return
    uv run etui
)
"

if ! grep -q "etui() {" "$BASHRC"; then
    echo "==> Adding etui shell function to $BASHRC"
    echo "$ETUI_FUNCTION" >> "$BASHRC"
    echo "➡️  Reload your shell or run: source ~/.bashrc"
else
    echo "==> etui shell function already exists"
fi

# ------------------------------------------------------------
# 6. Final instructions
# ------------------------------------------------------------
echo
echo "✅ Installation complete."
echo
