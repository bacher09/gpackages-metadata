import os.path
try:
    from unittest import TestCase, skip, skipIf, skipUnless
except ImportError:
    from unittest2 import TestCase, skip, skipIf, skipUnless


TESTS_DIR = os.path.dirname(__file__)
TESTDATA_DIR = os.path.join(TESTS_DIR, "data")
