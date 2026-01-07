#!/usr/bin/env bash
# Installs all necessary tools (uv, pre-commit), syncs the uv venv, installs the project
# itself in editable mode.

set -euo pipefail

DEV_MODE=false

for arg in "$@"; do
    case "$arg" in
        --dev)
            DEV_MODE=true
            ;;
        --help|-h)
            echo "Usage: ./install.sh [--dev]"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done


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
# 3. Development mode install (if --dev is set)
# ------------------------------------------------------------

if [ "$DEV_MODE" = true ]; then
    echo "==> Setting up pre-commit hooks"

    if ! command -v pre-commit >/dev/null 2>&1; then
        echo "==> Installing pre-commit"
        uv pip install pre-commit
    else
        echo "==> pre-commit already installed"
    fi

    uv run pre-commit install
else
    echo "==> Skipping pre-commit (not in --dev mode)"
fi


# ------------------------------------------------------------
# 4. Install project
# ------------------------------------------------------------
echo "==> Installing project in editable mode"
uv pip install -e .

# ------------------------------------------------------------
# 5. Add etui shell function
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
