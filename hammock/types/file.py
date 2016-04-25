from __future__ import absolute_import
import contextlib
import os


class File(object):

    def __init__(self, stream, content_length):
        self.stream = stream
        self.read = stream.read
        self.content_length = int(content_length) if content_length is not None else 0
        self.len = self.content_length

    def __len__(self):
        return self.content_length


@contextlib.contextmanager
def from_path(path):
    file_pobject = open(path, 'rb')
    old_file_position = file_pobject.tell()
    file_pobject.seek(0, os.SEEK_END)
    size = file_pobject.tell()
    file_pobject.seek(old_file_position, os.SEEK_SET)
    file_object = File(file_pobject, size)
    yield file_object
    file_object.stream.close()
