import sys
import os
"""
https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
"""
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(
        os.path.join(
            os.getcwd(), os.path.expanduser(__file__)
        )
    )
)

sys.path.append(
    os.path.normpath(
        os.path.join(
            SCRIPT_DIR, PACKAGE_PARENT
        )
    )
)