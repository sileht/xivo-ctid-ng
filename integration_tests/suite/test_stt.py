# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    calling,
    contains,
    empty,
    equal_to,
    contains_inanyorder,
    has_entries,
    has_entry,
    has_items,
    has_properties,
)
from xivo_test_helpers import until

from .helpers.base import RealAsteriskIntegrationTest

ENDPOINT_AUTOANSWER = 'Test/integration-caller/autoanswer'


class TestStt(RealAsteriskIntegrationTest):
    asset = 'stt'

    def test_stt(self):
        event_accumulator = self.bus.accumulator('stt.event')

        channel = self.call_app()
        # self.bus.send_event({'data': {'Event': "fake_call"}}, 'ami.fake_call')

        def event_received():
            events = event_accumulator.accumulate()
            assert_that(
                events,
                has_items(
                    has_entries(
                        name="stt",
                        data=has_entries(
                            call_id="%s" % channel.id,
                            result_stt="crise cardiaque"
                        )
                    )
                )
            )

        until.assert_(event_received, tries=10)

    def call_app(self, variables=None):
        kwargs = {
            'endpoint': ENDPOINT_AUTOANSWER,
            'app': 'wazo-app-stt',
            'appArgs': 'incoming',
            'variables': {
                'variables': {
                    'WAZO_CHANNEL_DIRECTION': 'to-wazo',
                },
            }
        }

        if variables:
            for key, value in variables.items():
                kwargs['variables']['variables'][key] = value

        channel = self.ari.channels.originate(**kwargs)
        return channel

