from __future__ import absolute_import
import six
try:
    import asyncio
except ImportError:
    import munch
    asyncio = munch.Munch(StreamReader=None)


class Stream(object):

    def __init__(self, stream):
        self._stream = stream
        self.read = self._get_sync_read_method()
        self.content_length = self._get_length()
        if hasattr(self._stream, 'seek'):
            self.seek = self._stream.seek
        if hasattr(self._stream, 'tell'):
            self.tell = self._stream.tell

    def _get_sync_read_method(self):
        """
        :return: a synchronous read method of a stream
        """
        if isinstance(self._stream, asyncio.StreamReader):
            return self._stream.read_nowait
        else:
            return self._stream.read

    def _get_length(self):
        if hasattr(self._stream, 'total_bytes'):  # aiohttp.StreamReader
            return self._stream.total_bytes
        if hasattr(self._stream, 'len'):
            return self._stream.len
        if hasattr(self._stream, '__len__'):
            return len(self._stream)
        elif isinstance(self._stream, (six.BytesIO, six.moves.StringIO)):
            try:
                self._stream.seek(0, six.io.SEEK_END)
                return self._stream.tell()
            finally:
                self._stream.seek(0)
        return None
