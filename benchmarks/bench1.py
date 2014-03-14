from functools import partial
from packages_metadata.package_backends import portage
from packages_metadata.package_backends import pkgcore
import time


def bench_all_data(gentoo_tree):
    for category in gentoo_tree.iter_categories():
        cat_descr = category.metadata.default_descr
        cat_name = category.name
        for package in category.iter_packages():
            package_name = package.name
            package_descr = package.description
            p_herds = package.metadata.herds
            p_maintainers = package.metadata.maintainers
            for ebuild in package.iter_ebuilds():
                masked = ebuild.is_hard_masked
                version = ebuild.fullversion
                dependes = ebuild.depends
                pdependes = ebuild.pdepends
                rdependes = ebuild.rdepends
                eapi = ebuild.eapi
                description =ebuild.description
                #homepages = ebuild.homepages
                slot = ebuild.slot
                iuse = ebuild.iuse
                licenses = ebuild.licenses
                keywords = ebuild.keywords


def measure_time(func):
    start_t = time.time()
    func()
    end_t = time.time()
    print("Time: {0}".format(end_t - start_t))


def build_gentoo_tree(module):
    return module.Portage().get_tree_by_name('gentoo')


def benchmark_module(module):
    tree = build_gentoo_tree(portage)
    func = partial(bench_all_data, tree)
    measure_time(func)


def bench1():
    print("Benchmark portage")
    benchmark_module(portage)
    print("\nBenchmark pkgcore")
    benchmark_module(pkgcore)


if __name__ == "__main__":
    bench1()
