from .utils import TestCase, TESTDATA_DIR
from packages_metadata.generic_metadata import package_metadata
import os.path


class TestPackageMetadata(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mdata1 = os.path.join(TESTDATA_DIR, 'package_libre_metadata.xml')
        cls.mdata2 = os.path.join(TESTDATA_DIR, 'package_portage_metadata.xml')

    def test_package_metadata1(self):
        libre_mdata = package_metadata.PackageMetaData(self.mdata1)
        self.assertTupleEqual(libre_mdata.herds(), ('openoffice',))

        portage_mdata = package_metadata.PackageMetaData(self.mdata2)
        p_maintainer = portage_mdata.maintainers()[0]
        self.assertEqual(p_maintainer.email, 'dev-portage@gentoo.org')
        self.assertEqual(
            portage_mdata.upstream.bugs_to,
            'mailto:dev-portage@gentoo.org'
        )
        self.assertIn(
            'git.overlays.gentoo.org',
            portage_mdata.upstream.changelog
        )
