from .utils import TestCase, TESTDATA_DIR
from packages_metadata.generic_metadata import use_info
import os.path


class TestUseInfo(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.use_desc = os.path.join(TESTDATA_DIR, 'use.desc')
        cls.use_local_desc = os.path.join(TESTDATA_DIR, 'use.local.desc')
        cls.profiles_desc = os.path.join(TESTDATA_DIR, 'profiles_desc')

    def test_global_use_info(self):
        uses = use_info.get_uses_info(self.use_desc)
        self.assertIn('pda', uses)
        self.assertIn('bootstrap', uses)
        self.assertEqual(uses['avahi'].strip(), "Add avahi/Zeroconf support")

    def test_local_use_info(self):
        luses = use_info.get_local_uses_info(self.use_local_desc)
        self.assertIn('coding', luses)
        self.assertIn('ssh', luses)
        self.assertListEqual(list(luses['ssh'].keys()), ['www-plugins/gnash'])
        msg = luses['ssh']['www-plugins/gnash']
        self.assertEqual(
            msg.strip(),
            "Enable using SSH for network authentication in libnet"
        )

    def test_profiles_desc(self):
        suses = use_info.get_use_special_info(self.profiles_desc)
        self.assertIn('kernel_linux', suses)
        self.assertIn('linguas_ru', suses)
        self.assertIn('linguas_en_us', suses)
