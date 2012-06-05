import portage
from portage.util.listdir import listdir
from portage.dep import Atom
from portage.exception import PortageException, FileNotFound, InvalidAtom, \
                              InvalidDependString, InvalidPackageName

from gentoolkit.package import Package as PackageInfo
from gentoolkit.metadata import MetaData
from generic import ToStrMixin
from datetime import datetime
import hashlib
import os

BINDB = portage.db[portage.root]["bintree"].dbapi
PORTDB = portage.db[portage.root]["porttree"].dbapi
VARDB = portage.db[portage.root]["vartree"].dbapi

ARCHES = PORTDB.settings["PORTAGE_ARCHLIST"].split()

_license_filter = lambda x: False if x.startswith('|') or x.startswith('(') or \
                                     x.endswith('?') or x.startswith(')') \
                                  else True

def _file_path(file_name):
    return lambda self: os.path.join(self.package_path, file_name)


def _file_hash(attr):
    return lambda self: file_sha1(getattr(self, attr))

def _file_mtime(attr):
    return lambda self: file_mtime(getattr(self, attr))

def _ebuild_environment(name):
    return lambda self: self.package_object.environment(name)

def file_sha1(file_path):
    sha1 = 'NULL'
    if os.path.exists(file_path):
        f = open(file_path, 'r')
        sha1 = hashlib.sha1(f.read()).hexdigest()
        f.close()
    return sha1

def file_mtime(file_path):
    if os.path.exists(file_path):
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    else:
        return None

class cached_property(object):
    def __init__(self, func, name = None):
        self.func = func
        if name is None:
            name = func.__name__
        self.__name__ = name
        self.__module__ = func.__module__

    def __get__(self, inst, owner):
        try:
            value = inst._cache[self.__name__]
        except (KeyError, AttributeError):
            value = self.func(inst)
            if not hasattr(inst, '_cache'):
                inst._cache = {}
            inst._cache[self.__name__] = value
        return value

class Use(ToStrMixin):
    "Represend Use flag as object"
    __slots__ = ('name',)

    def __init__(self, name):
        """Args:
            name -- name of use flag, may start with + or -
        """
        if name.startswith('+') or name.startswith('-'):
            name = name[1:]
        self.name = name

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        self.name == other.name

    def __ne__(self, other):
        self.name != other.name

    def __hash__(self):
        return hash(self.name)
        

class Keyword(ToStrMixin):
    __slots__ = ('name', 'status')
    status_repr = ['','~','-']
    
    def __init__(self, name, status = 0):
        """Args:
            name -- name of keyword, it may start with ~ or -, if so than 
                    status will be auto seting.
            status -- status of keyword: 0 - stable, 
                                         1 - utested '~',
                                         2 - unstable '-'
                    Also may get by name parameter.
        """
        if name.startswith('~'):
            name = name[1:]
            status = 1
        elif name.startswith('-'):
            name = name[1:]
            status = 2
        self.name = name
        self.status = status

    def __unicode__(self):
        return self.status_repr[self.status] + self.name

    @property
    def arch(self):
        "Return arch name"
        return self.name


class Portage(object):
    
    def iter_trees(self):
        for tree in PORTDB.porttrees:
            yield PortTree(tree)

    def iter_ebuilds():
        for tree in self.iter_trees():
            for ebuild in tree.iter_ebuilds():
                yield ebuild
    

class PortTree(ToStrMixin):
    
    def __init__(self, porttree = '/usr/portage'):
        self.porttree = porttree # TODO: it should be read-only

    def iter_categories(self):
        for category in sorted(PORTDB.settings.categories):
            if os.path.isdir(os.path.join(self.porttree_path, category)):
                    yield Category(self, category)

    def iter_packages(self):
        for category in self.iter_categories():
            for package in category.iter_packages():
                yield package
    
    def iter_ebuilds(self):
        for package in self.iter_packages():
            for ebuild in package.iter_ebuilds():
                yield ebuild

    def __unicode__(self):
        return self.porttree
    
    @property
    def porttree_path(self):
        return self.porttree


class Category(ToStrMixin):

    __slots__ = ('porttree', 'category')
    
    def __init__(self, porttree, category):
        self.porttree = porttree
        self.category = category
    
    def iter_packages(self):
        packages = listdir(self.porttree.porttree + '/'+ self.category,
                           EmptyOnError=1, ignorecvs=1, dirsonly=1) 
        for package in packages:
            try:
                atom = Atom(self.category + '/' + package)
            except InvalidAtom:
                continue
            if atom != atom.cp:
                continue
            yield Package(self, atom)

    def __unicode__(self):
        return self.category
    
    @property
    def category_path(self):
        return os.path.join(self.porttree.porttree_path, self.category)


class Package(ToStrMixin):

    __slots__ = ('category', 'package', '_cache')

    def __init__(self, category, package):
        self.category = category
        self.package = package
        self._cache = {}

    def iter_ebuilds(self):
        ebuilds = PORTDB.cp_list(self.package, mytree=self.category.porttree.porttree)
        for ebuild in ebuilds:
            yield Ebuild(self ,ebuild)

    def __unicode__(self):
        return '%s' % self.package

    @property
    def package_path(self):
        return os.path.join(self.category.porttree.porttree_path, self.package)

    @cached_property
    def metadata(self):
        return MetaData( self.metadata_path)

    mtime = property(_file_mtime("package_path"))

    @property
    def name(self):
        return self.package.split('/')[1]

    manifest_path = property(_file_path('Manifest'))
    changelog_path = property(_file_path('ChangeLog'))
    metadata_path = property(_file_path('metadata.xml'))

    #Hashes
    manifest_sha1 = cached_property(_file_hash('manifest_path'), name = 'manifest_sha1')
    changelog_sha1 = cached_property(_file_hash('changelog_path'), name = 'changelog_sha1')
    metadata_sha1 = cached_property(_file_hash('metadata_path'), name = 'metadata_sha1')
    # Modify times
    manifest_mtime = property(_file_mtime("manifest_path"))
    changelog_mtime = property(_file_mtime("changelog_path"))
    metadata_mtime = property(_file_mtime("metadata_path"))

    @cached_property
    def changelog(self):
        return open(self.changelog_path,'r').read()


class Ebuild(ToStrMixin):

    __slots__ = ('package', 'ebuild', 'package_object', '_cache')

    def __init__(self, package, ebuild):
        self.package = package
        self.ebuild = ebuild
        self.package_object = PackageInfo(ebuild)
        self._cache = {}

    @property
    def keywords_env(self):
        return self.package_object.environment("KEYWORDS", prefer_vdb = False)

    @property
    def keywords(self):
        return list(set(self.keywords_env.split()))
    
    def iter_keywords(self):
        keywords = self.keywords
        for keyword in keywords:
            yield Keyword(keyword)
        
    def get_keywords(self):
        l = []
        for keyword in self.iter_keywords():
            l.append(keyword)
        return l

    def get_uses_names(self):
        return self.package_object.environment("IUSE").split()
    

    def iter_uses(self):
        for use in self.get_uses_names():
            yield Use(use)

    def get_uses(self):
        l = [] # Bad code, it repeats
        for use in self.iter_uses():
            l.append(use)
        return l

    #Could be faster
    @cached_property
    def is_masked(self):
        return self.package_object.is_masked()

    @property
    def version(self):
        return self.package_object.version

    @property
    def revision(self):
        return self.package_object.revision

    @property
    def fullversion(self):
        return self.package_object.fullversion

    @property
    def ebuild_path(self):
        return self.package_object.ebuild_path()

    homepage_val = cached_property(_ebuild_environment('HOMEPAGE'), name = 'homepage_val')
    license = cached_property(_ebuild_environment('LICENSE'), name = 'license')
    description = cached_property(_ebuild_environment('DESCRIPTION'), name = 'description')
    eapi = cached_property(_ebuild_environment('EAPI'), name = 'eapi')
    slot = cached_property(_ebuild_environment('SLOT'), name = 'slot')

    @cached_property
    def homepages(self):
        return self.homepage_val.split()

    @cached_property
    def homepage(self):
        return self.homepages[0] if len(self.homepages)>=1 else ''


    @cached_property
    def licenses(self):
        return filter(_license_filter, self.license.split())

    @property
    def ebuild_path(self):
        return self.package_object.ebuild_path()

    sha1 = cached_property(_file_hash("ebuild_path"), name = 'sha1')
    mtime = cached_property(_file_mtime("ebuild_path"), name = 'mtime')

    def __unicode__(self):
        return self.ebuild
    
