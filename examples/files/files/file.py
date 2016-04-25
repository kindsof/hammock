import os


class File(object):

    TYPE_FILE = 'file'
    TYPE_DIRECTORY = 'directory'
    TYPE_LINK = 'link'
    TYPE_MOUNT = 'mount'

    def __init__(self, name, base_dir):
        self.name = name
        self.path = os.path.join(base_dir, self.name)

        stat = os.stat(self.path)
        self.mode = stat.st_mode
        self.user = stat.st_uid
        self.group = stat.st_gid
        self.size = stat.st_size
        self.modified = stat.st_mtime
        self.created = stat.st_ctime

    @property
    def to_dict(self):
        return {
            'name': self.name,
            'mode': self.mode,
            'user': self.user,
            'group': self.group,
            'size': self.size,
            'modified': self.modified,
            'created': self.created,
            'type': self.type,
        }

    @property
    def content(self):
        return open(self.path, 'r')

    def delete(self):
        if self.type == self.TYPE_FILE:
            os.remove(self.path)
        elif self.type == self.TYPE_DIRECTORY:
            os.removedirs(self.path)
        else:
            raise ValueError('Can only delete file or directory')

    @property
    def type(self):
        if os.path.isfile(self.path):
            return self.TYPE_FILE
        if os.path.isdir(self.path):
            return self.TYPE_DIRECTORY
        elif os.path.islink(self.path):
            return self.TYPE_LINK
        elif os.path.ismount(self.path):
            return self.TYPE_MOUNT


def list(path, type, sort, reverse):
    names = os.listdir(path)
    files = (File(name, path) for name in names)
    files = (a_file for a_file in files if type is None or a_file.type == type)
    return sorted(files, key=lambda a_file: getattr(a_file, sort), reverse=reverse)
