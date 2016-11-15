# -*- coding: utf-8 -*-
# Copyright 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import equal_to
from hamcrest import raises
from StringIO import StringIO
from unittest import TestCase

from ..storage import _MessageInfoParser


class TestMessageInfoParser(TestCase):

    def setUp(self):
        self.result = {}
        self.parser = _MessageInfoParser()

    def test_parse(self):
        content = '''
;
; Message Information file
;
[message]
origmailbox=1001
context=user
macrocontext=
exten=voicemail
rdnis=1001
priority=7
callerchan=SIP/xivo64-00000000
callerid="Etienne" <101>
origdate=Thu Nov  3 07:11:59 PM UTC 2016
origtime=1478200319
category=
msg_id=1478200319-00000000
flag=
duration=12
'''
        result = self._parse(content)
        expected = {
            u'id': u'1478200319-00000000',
            u'caller_id_name': u'Etienne',
            u'caller_id_num': u'101',
            u'timestamp': 1478200319,
            u'duration': 12,
        }
        assert_that(result, equal_to(expected))

    def test_parse_missing_field(self):
        content = '''
callerid="Etienne" <101>
origtime=1478200319
msg_id=1478200319-00000000
'''
        assert_that(calling(self._parse).with_args(content), raises(Exception))

    def test_parse_callerid_unknown(self):
        # happens when app_voicemail write a message with no caller ID information
        self.parser._parse_callerid('Unknown', self.result)

        assert_that(self.result, equal_to({u'caller_id_name': None, u'caller_id_num': None}))

    def test_parse_callerid_incomplete(self):
        self.parser._parse_callerid('1234', self.result)

        assert_that(self.result, equal_to({u'caller_id_name': None, u'caller_id_num': u'1234'}))

    def _parse(self, content):
        return self.parser.parse(StringIO(content))