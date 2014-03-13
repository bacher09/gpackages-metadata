from .utils import TestCase, TESTDATA_DIR
from packages_metadata.generic_metadata import news
import os.path


class TestNews(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.news_dir = os.path.join(TESTDATA_DIR, 'news')
        cls.news_titles = [
            'ia64-java-removal', 'glib-228', 'gnustep-new-layout', 'gnome-232'
        ]

    def test_news(self):
        test_news = news.News(repo_path=self.news_dir, news_path=self.news_dir)
        news_list = list(test_news)
        news_titles = [item.title for item in news_list]
        self.assertSetEqual(set(news_titles), set(self.news_titles))

        glib_news = None
        for item in news_list:
            if item.title == "glib-228":
                glib_news = item.default_news
                break

        self.assertEqual(glib_news.title.strip(), "Upgrade to GLIB 2.28")
        self.assertEqual(glib_news.revision, 1)
        authors = glib_news.authors
        self.assertEqual(len(authors), 1)
        self.assertEqual(authors[0].email, "freedesktop-bugs@gentoo.org")
        self.assertTupleEqual(glib_news.if_installed, ("<dev-libs/glib-2.28",))
