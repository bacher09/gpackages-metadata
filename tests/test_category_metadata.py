from .utils import TestCase, TESTDATA_DIR
from packages_metadata.generic_metadata import category_metadata
import os.path


class TestCategoryMetadata(TestCase):

    def setUp(self):
        self.test_metadata = os.path \
            .join(TESTDATA_DIR, "category_metadata.xml")

    def test_category_metadata(self):
        category_mdata = category_metadata.CategoryMetadata(self.test_metadata)
        self.assertEqual(
            category_mdata.default_descr.strip(),
            "Test description"
        )

        self.assertIn('ru', category_mdata.descrs)
