#!/bin/sh

TPD_KEYS_PATH="$1"
cd "$TPD_KEYS_PATH" || exit
ACTIVATE_FILE="$TPD_KEYS_PATH/.venv/bin/activate"
. "$ACTIVATE_FILE"
python3 tpd-keys.py --udemy <&0
