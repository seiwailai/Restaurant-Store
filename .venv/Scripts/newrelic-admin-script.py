#!d:\programmingprojects\djangoprojects\restaurant\.venv\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'newrelic==5.24.0.153','console_scripts','newrelic-admin'
__requires__ = 'newrelic==5.24.0.153'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('newrelic==5.24.0.153', 'console_scripts', 'newrelic-admin')()
    )
