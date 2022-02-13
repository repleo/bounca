#!/usr/bin/env bash -x

PYTHON_FOLDERS='api bounca certificate_engine vuetifyforms x509_pki superuser_signup'
BASEDIR=`dirname "$0"`
cd $BASEDIR

BLUE='\033[1;34m'
BRIGHT_RED='\033[1;31m'
DARK_GRAY='\033[0;37m'
RESET='\033[m'
INFO="${BLUE}[INFO]${RESET}"

function task() {
  if [ "$3" != "" ]; then
    printf "$2\n"

    $1 $3 &
    pid=$!
    wait $pid

    if [ $? == 0 ]; then
      echo -ne "\033[0K\r"
    else
      printf "${BRIGHT_RED}Please fix the above errors ${RESET}\n"
      exit 1
    fi
  fi
}

py_files=$(find $PYTHON_FOLDERS -path '**/migrations' -prune -o -name '*.py' -print)
PY_MESSAGE="${INFO} Check import order on python files ${DARK_GRAY}[*.py]${RESET}"
task "isort --check-only" "$PY_MESSAGE" "$py_files"
PY_MESSAGE="${INFO} Linting python files ${DARK_GRAY}[*.py]${RESET}"
task flake8 "$PY_MESSAGE" .
PY_MESSAGE="${INFO} Black python files ${DARK_GRAY}[*.py]${RESET}"
task "black --check" "$PY_MESSAGE" .
