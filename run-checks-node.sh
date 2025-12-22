#!/usr/bin/env bash -x

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

PY_MESSAGE="${INFO} Linting javascript files ${DARK_GRAY}[*.js]${RESET}"
cd front
npm install --legacy-peer-deps
task "npm run lint" "$PY_MESSAGE" .
