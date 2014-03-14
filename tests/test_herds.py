from .utils import TestCase, TESTDATA_DIR
from packages_metadata.generic_metadata import herds
import os.path


class TestHerds(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.herds_path = os.path.join(TESTDATA_DIR, 'herds.xml')

    def test_herds(self):
        herds_object = herds.Herds(self.herds_path)
        herds_list = list(herds_object.iter_herd())
        herd1 = herds_list[0]
        self.assertEqual(herd1.name, "test")
        self.assertEqual(herd1.description, "Maintainers of test")
        self.assertEqual(herd1.email, "test@mail.com")
        herd1_maintainers = list(herd1.iter_maintainer())
        self.assertEqual(herd1_maintainers[0].name, "John Doe")
        self.assertEqual(herd1_maintainers[0].email,
                         "test-maintainer@mail.com")
        self.assertEqual(herd1_maintainers[1].email,
                         "other-maintainer@mail.com")
        herd2 = herds_list[1]
        self.assertEqual(herd2.name, "other")
