XiVO CTI NG [![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=xivo-ctid-ng)](https://jenkins.wazo.community/job/xivo-ctid-ng)
===========

XiVO CTI is a [Computer telephony integration](http://en.wikipedia.org/Computer_telephony_integration) server 
that provides advanced telephony services such as automatic phone control and 
[Call center](http://en.wikipedia.org/wiki/Call_center) monitoring. CTI services are controlled by connecting to 
the server with the [XiVO CTI client](https://github.com/wazo-pbx/xivo-client-qt)

Installing XiVO CTI NG
----------------------

The server is already provided as a part of [Wazo](http://documentation.wazo.community).
Please refer to [the documentation](http://documentation.wazo.community/en/stable/installation/installsystem.html) for
further details on installing one.

Running unit tests
------------------

```
pip install tox
tox --recreate -e py27
```

Running integration tests
-------------------------

You need Docker installed on your machine.

1. ```cd integration_tests```
2. ```pip install -r test-requirements.txt```
3. ```git clone https://github.com/wazo-pbx/chan-test```
4. ```export CHAN_TEST_DIR=$PWD/chan-test   # CHAN_TEST_DIR defaults to ../../chan-test```
4. ```make test-setup```
5. ```make test```

Environment variables
---------------------

Running the integration tests is controlled by the following environment variables:

* `INTEGRATION_TEST_TIMEOUT`: controls the startup timeout of each container
* `LOCAL_GIT_REPOS`: may be used to mount development python packages inside containers
