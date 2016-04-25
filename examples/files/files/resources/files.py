from __future__ import absolute_import
import os
import shutil
import httplib

import hammock

import files.file as file


class Files(hammock.Resource):

    pwd = os.path.abspath(os.path.dirname(__file__))
    PATH = os.path.basename(pwd)

    @hammock.post(success_code=httplib.CREATED)
    def upload(self, _file, name):
        """
        Upload a new file.
        :param str name: Name for new file.
        :param str _file: Path of file to upload.
        :return dict: New file information.
        """
        with open(os.path.join(self.pwd, name), 'w') as write_stream:
            shutil.copyfileobj(_file.stream, write_stream)
        return file.File(name, self.pwd).to_dict

    @hammock.get()
    def list(self, sort='modified', reverse=False, type=None):
        """
        List files in directory.
        :param str type: Show only files of type.
        :param str sort: Sort files by attribute
        :param bool[False] reverse: Sort reverse.
        :return list: List of files.
        """
        return [a_file.to_dict for a_file in file.list(self.pwd, type, sort, reverse)]

    @hammock.get('{name}')
    def get(self, name):
        """
        Get file information.
        :param str name: Which file to get.
        :return dict: File inforamtion.
        """
        try:
            return file.File(name, self.pwd).to_dict
        except OSError as exc:
            raise hammock.exceptions.NotFound(str(exc))

    @hammock.get('{name}/download')
    def download(self, name):
        """
        Download a file.
        :param str name: Which file to download.
        :return file: File content.
        """
        try:
            return file.File(name, self.pwd).content
        except OSError as exc:
            raise hammock.exceptions.NotFound(str(exc))

    @hammock.delete('{name}')
    def delete(self, name):
        """
        Delete a file.
        :param str name: Which file to delete.
        :return None:
        """
        try:
            file.File(name, self.pwd).delete()
        except OSError:
            raise hammock.exceptions.NotFound('File {} not found'.format(name))
        except ValueError as exc:
            raise hammock.exceptions.BadRequest(str(exc))
