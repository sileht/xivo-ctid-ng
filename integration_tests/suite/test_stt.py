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
from .helpers.confd import MockApplication

ENDPOINT_AUTOANSWER = 'Test/integration-caller/autoanswer'


class TestStt(RealAsteriskIntegrationTest):
    asset = 'stt'

    def test_stt(self):

        self.stt_app_uuid = 'b00857f4-cb62-4773-adf7-ca870fa65c8d'
        stt_app = MockApplication(
            uuid=self.stt_app_uuid,
            name='stt-app',
            destination=None,
        )
        self.confd.set_applications(stt_app)

        # TODO: add a way to load new apps without restarting
        self._restart_ctid_ng()

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

        def channel_set():
            assert_that(
                channel.getChannelVar(variable="X_WAZO_STT")['value'] == "crise cardiaque"
            )

        until.assert_(channel_set, tries=3)

        calls = self.ctid_ng.list_calls()
        assert_that(calls, has_entry('items', contains(
            has_entries(
                call_id=channel.id,
            )
        )))

        response = self.ctid_ng.get_application_calls(self.stt_app_uuid)
        assert_that(response.json()['items'],
                    has_items(has_entries(
                        id=channel.id,
                        variables=has_entries(STT="crise cardiaque")
                    )))

    def call_app(self, variables=None):
        kwargs = {
            'endpoint': ENDPOINT_AUTOANSWER,
            'app': 'wazo-app-%s' % self.stt_app_uuid,
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

