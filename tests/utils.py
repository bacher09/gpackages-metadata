try:
    from unittest import TestCase, skip, skipIf, skipUnless
except ImportError:
    from unittest2 import TestCase, skip, skipIf, skipUnless
