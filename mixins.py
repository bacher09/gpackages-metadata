from generic import ToStrMixin, file_sha1, file_mtime, cached_property, \
                    file_get_content, iter_over_gen

from use_info import get_uses_info, get_local_uses_info
# Repo info
from repo_info import TreeMetadata
import os.path

def _file_path(file_name):
    return lambda self: os.path.join(self.package_path, file_name)

def _file_hash(attr):
    return lambda self: file_sha1(getattr(self, attr))

def _file_mtime(attr):
    return lambda self: file_mtime(getattr(self, attr))


def gen_generator_over_gen(gen_name, name):
    return lambda self: iter_over_gen(getattr(self, gen_name)(), name)

class IteratorAddMetaclass(type):
    
    def __init__(cls, name, bases, dct):
        super(IteratorAddMetaclass, cls).__init__(name, bases, dct)
        for name in cls.generator_names:
            setattr(cls, name, gen_generator_over_gen(cls.main_iterator, name))

class AutoGeneratorMixin(object):

    __metaclass__ = IteratorAddMetaclass
    generator_names = ()
    #main_iterator = 'generator_name'


class PortageBaseMixin(ToStrMixin):
    def iter_use_desc(self):
        for tree in self.iter_trees():
            yield tree.use_desc

    def iter_use_local_desc(self):
        for tree in self.iter_trees():
            yield tree.use_local_desc

    def get_all_use_desc(self):
        return _gen_all_use(lambda x,y: x.update(y), self.iter_use_desc())

    def get_all_use_local_desc(self):
        def action(all_dict, use_dict):
            for key, value in use_dict.iteritems():
                all_dict[key].update(value)

        return _gen_all_use(action, self.iter_use_local_desc())

    def __unicode__(self):
        return u'portage'

class PortageIteratorMixin(AutoGeneratorMixin):
    main_iterator = 'iter_trees'
    generator_names = ('iter_categories', 'iter_packages', 'iter_ebuilds')

class PortTreeBaseMixin(ToStrMixin):

    @cached_property
    def metadata(self):
        return TreeMetadata(self.name)

    @cached_property
    def use_desc(self):
        return _get_info_by_func(get_uses_info,
                                 self.porttree_path,
                                 'profiles/use.desc')

    @cached_property
    def use_local_desc(self):
        return _get_info_by_func(get_local_uses_info,
                                 self.porttree_path,
                                 'profiles/use.local.desc')

    def __unicode__(self):
        return self.name

class PortTreeIteratorMixin(AutoGeneratorMixin):
    main_iterator = 'iter_categories'
    generator_names = ('iter_packages', 'iter_ebuilds')
    
class MetaDataPath(object):

    @property
    def metadata_path(self):
        raise NotImplementedError

class CategoryBaseMixin(ToStrMixin):

    @property
    def metadata_path(self):
        return os.path.join(self.category_path, 'metadata.xml')

    @cached_property
    def metadata_sha1(self):
        return file_sha1(self.metadata_path)

    @cached_property
    def metadata(self):
        return CategoryMetadata(self.metadata_path)

    def __unicode__(self):
        return self.name

class CategoryIteratorMixin(AutoGeneratorMixin):
    main_iterator = 'iter_packages'
    generator_names = ('iter_ebuilds', )
    
class PackageBaseMixin(ToStrMixin, MetaDataPath):

    @cached_property
    def metadata(self):
        "Return `MetaData` object that represent package metadata.xml file"
        try:
            return MetaData( self.metadata_path)
        except IOError:
            return FakeMetaData()

    @cached_property
    def descriptions(self):
        return self.metadata.descriptions()

    @property
    def description(self):
        "Return first description in package metadata.xml"
        if len(self.descriptions)>0:
            return self.descriptions[0]
        else:
            return None
    @property
    def cp(self):
        raise NotImplementedError

    def __unicode__(self):
        return unicode(self.cp)

class PackageFilesMixin(object):
    #Paths 
    manifest_path = property(_file_path('Manifest'))
    changelog_path = property(_file_path('ChangeLog'))
    metadata_path = property(_file_path('metadata.xml'))

    #Hashes
    manifest_sha1 = cached_property(_file_hash('manifest_path'),
                                    name = 'manifest_sha1')
    changelog_sha1 = cached_property(_file_hash('changelog_path'),
                                     name = 'changelog_sha1')
    metadata_sha1 = cached_property(_file_hash('metadata_path'),
                                    name = 'metadata_sha1')

    # Modify times
    manifest_mtime = property(_file_mtime("manifest_path"))
    changelog_mtime = property(_file_mtime("changelog_path"))
    metadata_mtime = property(_file_mtime("metadata_path"))

    mtime = property(_file_mtime("package_path"))

    @cached_property
    def changelog(self):
        "Return ChangeLog content"
        return file_get_content(self.changelog_path)

class EbuildBaseMixin(ToStrMixin):

    sha1 = cached_property(_file_hash("ebuild_path"), name = 'sha1')
    mtime = cached_property(_file_mtime("ebuild_path"), name = 'mtime')
    
    @property
    def cpv(self):
        raise NotImplementedError

    def __unicode__(self):
        return unicode(self.cpv)

#Main mixins
class PortageMixin(PortageBaseMixin, PortageIteratorMixin):
    pass

class PortTreeMixin(PortTreeBaseMixin, PortTreeIteratorMixin):
    pass

class CategoryMixin(CategoryBaseMixin, CategoryIteratorMixin):
    pass

class PackageMixin(PackageBaseMixin, PackageFilesMixin):
    pass

class EbuildMixin(EbuildBaseMixin):
    pass
