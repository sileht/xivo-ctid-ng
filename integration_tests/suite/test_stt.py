# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from ari.exceptions import ARINotFound
from hamcrest import (
    assert_that,
    calling,
    empty,
    equal_to,
    contains_inanyorder,
    has_entries,
    has_entry,
    has_properties,
)
from xivo_test_helpers import until
from xivo_test_helpers.hamcrest.raises import raises
from xivo_ctid_ng_client.exceptions import CtidNGError
from .helpers.base import RealAsteriskIntegrationTest
from .helpers.confd import MockConference

ENDPOINT_AUTOANSWER = 'Test/integration-caller/autoanswer'
CONFERENCE1_EXTENSION = '4001'
CONFERENCE1_ID = 4001


class TestStt(RealAsteriskIntegrationTest):

    asset = 'stt'

    def setUp(self):
        super().setUp()
        self.confd.reset()


class TestSttHelloWorld(TestStt):

    def test_hello_world(self):
        event_accumulator = self.bus.accumulator('ami.patate')

        self.bus.send_event({
            'data': {
            }
        }, 'ami.patate')

        def event_received():
            events = event_accumulator.accumulate()
            assert_that(
                events,
                contains(
                    has_entries(
                        name='hello_world',
                        data=has_entries(
                            hello="world"
                        )
                    )
                )
            )

        until.assert_(event_received, tries=3)
