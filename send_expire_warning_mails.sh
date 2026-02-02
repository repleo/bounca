#!/usr/bin/env -S bash -e

WORKDIR=`dirname "$0"`

cd "$WORKDIR"
. env/bin/activate

python manage.py send_expire_email

