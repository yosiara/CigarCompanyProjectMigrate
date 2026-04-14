# -*- coding: utf-8 -*-

from odoo.models import AbstractModel


class DownloadFileBaseClass(AbstractModel):
    _name = 'download_file_base_class'
    _description = 'download_file_base_class'

    record = False

    def get_file_name(self):
        raise NotImplementedError

    def get_file(self):
        raise NotImplementedError
DownloadFileBaseClass()
