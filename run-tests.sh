#!/usr/bin/env bash -x

PYTHON_FOLDERS='api bounca certificate_engine vuetifyforms x509_pki superuser_signup'
BASEDIR=`dirname "$0"`/
cd $BASEDIR

. ./env/bin/activate

BLUE='\033[1;34m'
BRIGHT_RED='\033[1;31m'
DARK_GRAY='\033[0;37m'
RESET='\033[m'
INFO="${BLUE}[INFO]${RESET}"

function task() {
    printf "$2\n"
    # docker-compose start
    $1 &
    pid=$!
    wait $pid

    if [ $? == 0 ]; then
      echo -ne "\033[0K\r"
      # docker-compose stop
    else
      printf "${BRIGHT_RED}Please fix the above errors ${RESET}\n"
      # docker-compose stop
      exit 1
    fi
}

mypy .

PY_MESSAGE="${INFO} Running unit tests${RESET}"
task "coverage run --include bounca/\* --omit */env/*,*/venv/*,*/migrations/*,*/tests/* manage.py test" "$PY_MESSAGE"
coverage report
coverage xml
