from .utils import TestCase, TESTDATA_DIR
from packages_metadata.generic_metadata import license_text
import os.path


class TestLicenses(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.licenses_dir = os.path.join(TESTDATA_DIR, 'test_licenses')

    def test_licenses_text(self):
        test_licenses = license_text.Licenses(self.licenses_dir,
                                              self.licenses_dir)
        self.assertIn('license1', test_licenses)
        l1_text = test_licenses.get_license('license1')
        print(test_licenses.get_license_path('license1'))
        self.assertEqual(l1_text.strip(), "License 1 for test")
        l2_text = test_licenses.get_license('license2')
        self.assertEqual(l2_text.strip(), 'License 2')
