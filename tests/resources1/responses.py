from __future__ import absolute_import
import hammock
import six
import xml.etree.ElementTree as ElementTree


class Responses(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get(path='none')
    def none(self):
        return None

    @hammock.get(path='string')
    def string(self):
        return 'string'

    @hammock.get(path='string-io')
    def string_io(self):
        return six.moves.StringIO('string')

    @hammock.get(path='bytes')
    def bytes(self):
        return b'bytes'

    @hammock.get(path='bytes-io')
    def bytes_io(self):
        return six.BytesIO(b'bytes')

    @hammock.get(path='list')
    def list(self):
        return [1, 2, 3]

    @hammock.get(path='xml', response_content_type='application/xml')
    def xml(self):
        top = ElementTree.Element('topElem')
        sub = ElementTree.SubElement(top, 'SubElem1')
        sub.text = 'text1'
        sub = ElementTree.SubElement(top, 'SubElem2')
        sub.text = 'text2'
        return {'_content': top}
