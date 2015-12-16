# -*- coding: utf-8 -*-
# Copyright 2015 by Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from flask import request

from xivo_ctid_ng.core.rest_api import AuthResource

from . import validator

logger = logging.getLogger(__name__)


class CallsResource(AuthResource):

    def __init__(self, calls_service):
        self.calls_service = calls_service

    def get(self):
        token = request.headers['X-Auth-Token']
        self.calls_service.set_confd_token(token)
        application_filter = request.args.get('application')
        application_instance_filter = request.args.get('application_instance')

        calls = self.calls_service.list_calls(application_filter, application_instance_filter)

        return {
            'items': [call.to_dict() for call in calls],
        }, 200

    def post(self):
        token = request.headers['X-Auth-Token']
        self.calls_service.set_confd_token(token)
        request_body = request.json

        validator.validate_originate_body(request_body)

        call_id = self.calls_service.originate(request_body)

        return {'call_id': call_id}, 201


class CallResource(AuthResource):

    def __init__(self, calls_service):
        self.calls_service = calls_service

    def get(self, call_id):
        token = request.headers['X-Auth-Token']
        self.calls_service.set_confd_token(token)

        call = self.calls_service.get(call_id)

        return call.to_dict()

    def delete(self, call_id):
        self.calls_service.hangup(call_id)

        return None, 204
