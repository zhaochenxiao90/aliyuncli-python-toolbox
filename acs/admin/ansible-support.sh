#/bin/sh
set -euox pipefail
apk add ansible
pip install paramiko PyYAML Jinja2 httplib2 six