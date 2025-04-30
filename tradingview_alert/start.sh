#!/bin/bash

# SCRIPT 환경변수
SH_CONFIG="conf/script_config"
# python 모듈 리스트
FREEZE_MODULE_FILE="conf/requirements_freeze.txt"

# 필수 모듈
modules=()

curpath=$(dirname $(realpath $0))
cd "$curpath"

if [ ! -f "$curpath/$SH_CONFIG" ]; then
    echo "not found $SH_CONFIG"
    exit 1
fi

source $curpath/$SH_CONFIG

if [ -z "$VENV_NAME" ]; then
    echo "no VENV_NAME variable"
    exit 1
fi

if [ -z "$MAIN_SCRIPT" ]; then
    echo "no MAIN_SCRIPT variable"
    exit 1
fi

if [ ! -d "$curpath/$VENV_NAME" ]; then
    echo "not set venv"
    echo "please setting first"
    echo "install command"
    echo "python3 -m venv $VENV_NAME"
    exit 1
fi

# install
# python3 -m venv $VENV_NAME
# if not create 'activate' file
# python3 -m venv --without-pip $VENV_NAME
# curl https://bootstrap.pypa.io/get-pip.py | $VENV_NAME/bin/python3

if [ ! -f "$curpath/$VENV_NAME/bin/activate" ]; then
    echo "cannot find venv activate script"
    echo "Is it correct that venv is installed properly?"
    echo "install command"
    echo "python3 -m venv $VENV_NAME"
fi


source "$curpath/$VENV_NAME/bin/activate"


if [ "$MODULE_INTEGRITY" != "0" ]; then

    if [ -f "$curpath/$FREEZE_MODULE_FILE" ]; then
        freeze_file=$(cat "$curpath/$FREEZE_MODULE_FILE" | awk -F '==' '{ print $1 }' )
        modules=($freeze_file)  # 리스트로 변환
        # echo "./$VENV_NAME/bin/python3 -m pip freeze > ./$FREEZE_MODULE_FILE"
    fi

    for module in "${modules[@]}"; do
        is_module=$(python3 -m pip freeze 2>/dev/null | grep "${module}==")
        if [[ $is_module != "" ]]; then
            continue
        fi
        echo "$module is not found, install first"
        echo "install command"
        echo "./$VENV_NAME/bin/python3 -m pip install $module"
        deactivate
        exit 1
    done
fi


# echo "pip list"
# pip freeze
# pip install -r pip_freeze.txt
# $VENV_NAME/bin/pip3 install discord

# echo "venv activate"
$VENV_NAME/bin/python "$MAIN_SCRIPT"

# if [ $(command -v deactivate) != "" ]; then
deactivate
# echo "venv deactivate"
# fi
# echo "venv deactivate"
