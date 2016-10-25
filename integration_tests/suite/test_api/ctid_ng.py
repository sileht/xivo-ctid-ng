# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import json
import requests
import time

from contextlib import contextmanager
from hamcrest import assert_that, equal_to

from .constants import VALID_TOKEN


class CtidNgClient(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port

    def url(self, *parts):
        return 'https://{host}:{port}/1.0/{path}'.format(host=self._host,
                                                         port=self._port,
                                                         path='/'.join(unicode(part) for part in parts))

    def is_up(self):
        url = self.url()
        try:
            response = requests.get(url, verify=False)
            return response.status_code == 404
        except requests.RequestException:
            return False

    def get_calls_result(self, application=None, application_instance=None, token=None):
        url = self.url('calls')
        params = {}
        if application:
            params['application'] = application
            if application_instance:
                params['application_instance'] = application_instance
        result = requests.get(url,
                              params=params,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def list_calls(self, application=None, application_instance=None, token=VALID_TOKEN):
        response = self.get_calls_result(application, application_instance, token)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    def get_users_me_calls_result(self, application=None, application_instance=None, token=None):
        url = self.url('users', 'me', 'calls')
        params = {}
        if application:
            params['application'] = application
            if application_instance:
                params['application_instance'] = application_instance
        result = requests.get(url,
                              params=params,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def list_my_calls(self, application=None, application_instance=None, token=VALID_TOKEN):
        response = self.get_users_me_calls_result(application, application_instance, token)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    def get_call_result(self, call_id, token=None):
        url = self.url('calls', call_id)
        result = requests.get(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def get_call(self, call_id, token=VALID_TOKEN):
        response = self.get_call_result(call_id, token=token)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    def post_call_result(self, source, priority, extension, context, variables=None, line_id=None, token=None):
        body = {
            'source': {
                'user': source,
            },
            'destination': {
                'priority': priority,
                'extension': extension,
                'context': context,
            },
        }
        if variables:
            body['variables'] = variables
        if line_id:
            body['source']['line_id'] = line_id

        return self.post_call_raw(body, token)

    def post_call_raw(self, body, token=None):
        url = self.url('calls')
        result = requests.post(url,
                               json=body,
                               headers={'X-Auth-Token': token},
                               verify=False)
        return result

    def originate(self, source, priority, extension, context, variables=None, line_id=None, token=VALID_TOKEN):
        response = self.post_call_result(source, priority, extension, context, variables, line_id, token=token)
        assert_that(response.status_code, equal_to(201))
        return response.json()

    def post_user_me_call_result(self, body, token=None):
        url = self.url('users', 'me', 'calls')
        result = requests.post(url,
                               json=body,
                               headers={'X-Auth-Token': token},
                               verify=False)
        return result

    def originate_me(self, extension, variables=None, line_id=None, token=VALID_TOKEN):
        body = {
            'extension': extension
        }
        if variables:
            body['variables'] = variables
        if line_id:
            body['line_id'] = line_id
        response = self.post_user_me_call_result(body, token=token)
        assert_that(response.status_code, equal_to(201))
        return response.json()

    def delete_call_result(self, call_id, token=None):
        url = self.url('calls', call_id)
        result = requests.delete(url,
                                 headers={'X-Auth-Token': token},
                                 verify=False)
        return result

    def hangup_call(self, call_id, token=VALID_TOKEN):
        response = self.delete_call_result(call_id, token=token)
        assert_that(response.status_code, equal_to(204))

    def delete_user_me_call_result(self, call_id, token=None):
        url = self.url('users', 'me', 'calls', call_id)
        result = requests.delete(url,
                                 headers={'X-Auth-Token': token},
                                 verify=False)
        return result

    def hangup_my_call(self, call_id, token=VALID_TOKEN):
        response = self.delete_user_me_call_result(call_id, token=token)
        assert_that(response.status_code, equal_to(204))

    def get_plugins_result(self, token=None):
        url = self.url('plugins')
        result = requests.get(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def put_call_user_result(self, call_id, user_uuid, token):
        url = self.url('calls', call_id, 'user', user_uuid)
        result = requests.put(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def connect_user(self, call_id, user_uuid):
        response = self.put_call_user_result(call_id, user_uuid, token=VALID_TOKEN)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    def get_users_me_transfers_result(self, token=None):
        url = self.url('users', 'me', 'transfers')
        result = requests.get(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def list_my_transfers(self, token=VALID_TOKEN):
        response = self.get_users_me_transfers_result(token)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    def post_transfer_result(self, body, token=None):
        url = self.url('transfers')
        result = requests.post(url,
                               json=body,
                               headers={'X-Auth-Token': token},
                               verify=False)
        return result

    def create_transfer(self, transferred_call, initiator_call, context, exten, variables=None, timeout=None):
        body = {
            'transferred_call': transferred_call,
            'initiator_call': initiator_call,
            'context': context,
            'exten': exten,
            'flow': 'attended',
        }
        if variables:
            body['variables'] = variables
        if timeout:
            body['timeout'] = timeout
        response = self.post_transfer_result(body, token=VALID_TOKEN)
        assert_that(response.status_code, equal_to(201))
        return response.json()

    def create_blind_transfer(self, transferred_call, initiator_call, context, exten):
        body = {
            'transferred_call': transferred_call,
            'initiator_call': initiator_call,
            'context': context,
            'exten': exten,
            'flow': 'blind',
        }
        response = self.post_transfer_result(body, token=VALID_TOKEN)
        assert_that(response.status_code, equal_to(201))
        return response.json()

    def post_user_transfer_result(self, body, token=None):
        url = self.url('users', 'me', 'transfers')
        result = requests.post(url,
                               json=body,
                               headers={'X-Auth-Token': token},
                               verify=False)
        return result

    def create_user_transfer(self, initiator_call, exten, token=VALID_TOKEN):
        body = {
            'initiator_call': initiator_call,
            'exten': exten,
            'flow': 'attended',
        }
        response = self.post_user_transfer_result(body, token=token)
        assert_that(response.status_code, equal_to(201))
        return response.json()

    def put_complete_transfer_result(self, transfer_id, token=None):
        url = self.url('transfers', transfer_id, 'complete')
        result = requests.put(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def complete_transfer(self, transfer_id):
        response = self.put_complete_transfer_result(transfer_id, token=VALID_TOKEN)
        assert_that(response.status_code, equal_to(204))

    def put_users_me_complete_transfer_result(self, transfer_id, token=None):
        url = self.url('users', 'me', 'transfers', transfer_id, 'complete')
        result = requests.put(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def complete_my_transfer(self, transfer_id, token=VALID_TOKEN):
        response = self.put_users_me_complete_transfer_result(transfer_id, token=token)
        assert_that(response.status_code, equal_to(204))

    def delete_transfer_result(self, transfer_id, token=None):
        url = self.url('transfers', transfer_id)
        result = requests.delete(url,
                                 headers={'X-Auth-Token': token},
                                 verify=False)
        return result

    def cancel_transfer(self, transfer_id):
        response = self.delete_transfer_result(transfer_id,
                                               token=VALID_TOKEN)
        assert_that(response.status_code, equal_to(204))

    def delete_users_me_transfer_result(self, transfer_id, token=None):
        url = self.url('users', 'me', 'transfers', transfer_id)
        result = requests.delete(url,
                                 headers={'X-Auth-Token': token},
                                 verify=False)
        return result

    def cancel_my_transfer(self, transfer_id, token=VALID_TOKEN):
        response = self.delete_users_me_transfer_result(transfer_id,
                                                        token=token)
        assert_that(response.status_code, equal_to(204))

    def get_transfer_result(self, transfer_id, token=None):
        url = self.url('transfers', transfer_id)
        result = requests.get(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def get_transfer(self, transfer_id, token=VALID_TOKEN):
        response = self.get_transfer_result(transfer_id, token=token)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    def post_chat_result(self, chat_msg, token=None):
        url = self.url('chats')
        result = requests.post(url,
                               json=chat_msg.as_chat_body(),
                               headers={'X-Auth-Token': token},
                               verify=False)
        return result

    def post_user_chat_result(self, chat_msg, token=None):
        url = self.url('users', 'me', 'chats')
        result = requests.post(url,
                               json=chat_msg.as_user_chat_body(),
                               headers={'X-Auth-Token': token},
                               verify=False)
        return result

    def get_user_me_presence_result(self, token=None):
        url = self.url('users', 'me', 'presences')
        result = requests.get(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def get_user_presence_result(self, user_uuid, token=None):
        url = self.url('users', user_uuid, 'presences')
        result = requests.get(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def put_user_presence_result(self, presence_msg, user_uuid, token=None):
        url = self.url('users', user_uuid, 'presences')
        result = requests.put(url,
                              json=presence_msg.as_presence_body(),
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def put_user_me_presence_result(self, presence_msg, token=None):
        url = self.url('users', 'me', 'presences')
        result = requests.put(url,
                              json=presence_msg.as_presence_body(),
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def get_line_presence_result(self, line_id, token=None):
        url = self.url('lines', line_id, 'presences')
        result = requests.get(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def get_status_result(self, token=None):
        url = self.url('status')
        result = requests.get(url,
                              headers={'X-Auth-Token': token},
                              verify=False)
        return result

    def status(self, token=VALID_TOKEN):
        response = self.get_status_result(token)
        assert_that(response.status_code, equal_to(200))
        return response.json()

    @contextmanager
    def send_no_content_type(self):
        def no_json(decorated):
            def decorator(*args, **kwargs):
                kwargs['data'] = json.dumps(kwargs.pop('json'))
                return decorated(*args, **kwargs)
            return decorator

        old_post = requests.post
        old_put = requests.put
        requests.post = no_json(requests.post)
        requests.put = no_json(requests.put)
        yield
        requests.post = old_post
        requests.put = old_put


def new_call_id():
    return format(time.time(), '.2f')
