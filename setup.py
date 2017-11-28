#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from setuptools import setup
from setuptools import find_packages


setup(
    name='xivo-ctid-ng',
    version='2.0',
    description='Wazo CTI Server Daemon',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    packages=find_packages(),
    package_data={
        'xivo_ctid_ng.plugins': ['*/api.yml'],
    },
    scripts=['bin/xivo-ctid-ng'],
    entry_points={
        'xivo_ctid_ng.plugins': [
            'api = xivo_ctid_ng.plugins.api.plugin:Plugin',
            'calls = xivo_ctid_ng.plugins.calls.plugin:Plugin',
            'chats = xivo_ctid_ng.plugins.chats.plugin:Plugin',
            'mongooseim = xivo_ctid_ng.plugins.mongooseim.plugin:Plugin',
            'presences = xivo_ctid_ng.plugins.presences.plugin:Plugin',
            'relocates = xivo_ctid_ng.plugins.relocates.plugin:Plugin',
            'status = xivo_ctid_ng.plugins.status.plugin:Plugin',
            'switchboards = xivo_ctid_ng.plugins.switchboards.plugin:Plugin',
            'transfers = xivo_ctid_ng.plugins.transfers.plugin:Plugin',
            'voicemails = xivo_ctid_ng.plugins.voicemails.plugin:Plugin',
        ]
    }
)
