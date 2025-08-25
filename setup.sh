#!/bin/bash

clr_def="\033[0m"
clr_grn="\033[0;32m"

if [ "$0" == "$BASH_SOURCE" ]; then
    echo -e "Please source this script via: ${clr_grn}source start.sh${clr_def}."
    exit 1
fi

script_dir=$(cd "$(dirname "$BASH_SOURCE")" && pwd)

if [ "$(pwd)" != "$script_dir" ]; then
    echo "Please run the script from its directory."
    return 1
fi

if ! command -v python3 &>/dev/null; then
    echo "Python is not installed."
    return 1
fi

userPyVer=$(python3 --version | awk '{print $2}')
reqPyVer="3.11.0"

if [[ $userPyVer < $reqPyVer ]]; then
    echo -e "Your Python version (${clr_grn}$userPyVer${clr_def}) is not supported." \
            "Please install Python ${clr_grn}$reqPyVer${clr_def} or greater to continue."
    return 1
fi

if ! python3 -c "import venv" &>/dev/null; then
    echo -e "Python module ${clr_grn}venv${clr_def} is not installed."
    return 1
fi

if ! command -v pip3 &>/dev/null; then
    echo -e "Python package manager ${clr_grn}pip3${clr_def} is not installed."
    return 1
fi

venvActivationScript="venv/bin/activate"

if [ -e "$venvActivationScript" ]; then
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Activating virtual environment..."
        source $venvActivationScript
    fi
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Activating virtual environment..."
    source "$venvActivationScript"
fi

if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "Python virtual environment (${clr_grn}venv${clr_def}) could not" \
            "be activated. Please try activating it manually via:" \
            "${clr_grn}source venv/bin/activate${clr_def}."
    return 1
fi

export PIP_DISABLE_PIP_VERSION_CHECK=1

get_missing_pip_packages() {
    local installed_packages=$(pip3 list --format=freeze)
    local required_packages=$(cat "$1")
    local missing_packages=()

    for package in $required_packages; do
        local installed=""
        for installed_package in $installed_packages; do
            if [[ "$installed_package" =~ ^$package ]]; then
                installed="$installed_package"
            fi
        done

        if [ -z "$installed" ]; then
            missing_packages+=("$package")
        fi
    done

    echo "${missing_packages[@]}"
}

missing_packages=($(get_missing_pip_packages "requirements.txt"))

if [ ${#missing_packages[@]} -gt 0 ]; then
    for package in "${missing_packages[@]}"; do
        pip3 install "$package"
    done
fi

mkdir -p logs
