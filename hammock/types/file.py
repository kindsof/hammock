from __future__ import absolute_import
import os


class File(object):

    def __init__(self, stream, content_length):
        self.stream = stream
        self.read = stream.read
        self.content_length = int(content_length)
        self.len = self.content_length

    def __len__(self):
        return self.content_length


def from_path(path):
    f = open(path, 'rb')
    old_file_position = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(old_file_position, os.SEEK_SET)
    file_object = File(f, size)
    yield file_object
    file_object.stream.close()
