class File(object):

    def __init__(self, stream, content_length):
        self.stream = stream
        self.read = stream.read
        self.content_length = int(content_length)
        self.len = self.content_length

    def __len__(self):
        return self.content_length
