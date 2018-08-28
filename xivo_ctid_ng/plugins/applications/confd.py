# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from requests import HTTPError
from requests import RequestException

from xivo_ctid_ng.exceptions import XiVOConfdUnreachable
from xivo_ctid_ng.helpers.confd import not_found


class Application(object):

    def __init__(self, uuid, confd_client):
        self.uuid = uuid
        self._confd = confd_client

    def exists(self):
        try:
            self._confd.applications.get(self.uuid)
        except HTTPError as e:
            if not_found(e):
                return False
            raise
        except RequestException as e:
            raise XiVOConfdUnreachable(self._confd, e)
        else:
            return True
