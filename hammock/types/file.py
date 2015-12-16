class File(object):

    def __init__(self, stream, content_length):
        self.stream = stream
        self.content_length = content_length
        self.len = content_length

    def __len__(self):
        return self.content_length
