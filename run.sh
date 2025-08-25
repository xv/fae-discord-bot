#!/bin/bash

venvActivationScript="venv/bin/activate"

if [ -e "$venvActivationScript" ]; then
    source "$venvActivationScript"
else
    echo -e "Cannot find '$venvActivationScript'!"
    return 1
fi

echo "Starting bot..."
python3 "src/bot.py"
