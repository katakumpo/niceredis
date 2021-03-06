import datetime
import pytest
import niceredis

from distutils.version import StrictVersion


_REDIS_VERSIONS = {}


def get_version(**kwargs):
    params = {'host': 'localhost', 'port': 6379, 'db': 9}
    params.update(kwargs)
    key = '%s:%s' % (params['host'], params['port'])
    if key not in _REDIS_VERSIONS:
        client = niceredis.Redis(**params)
        _REDIS_VERSIONS[key] = client.info()['redis_version']
        client.connection_pool.disconnect()
    return _REDIS_VERSIONS[key]


def _get_client(cls, request=None, **kwargs):
    params = {'host': 'localhost', 'port': 6379, 'db': 9}
    params.update(kwargs)
    client = cls(**params)
    client.flushdb()
    if request:
        def teardown():
            client.flushdb()
            client.connection_pool.disconnect()
        request.addfinalizer(teardown)
    return client


def redis_server_time(client):
    seconds, milliseconds = client.time()
    timestamp = float('%s.%s' % (seconds, milliseconds))
    return datetime.datetime.fromtimestamp(timestamp)


def skip_if_server_version_lt(min_version):
    check = StrictVersion(get_version()) < StrictVersion(min_version)
    return pytest.mark.skipif(check, reason="")


@pytest.fixture()
def r(request, **kwargs):
    return _get_client(niceredis.Redis, request, **kwargs)


@pytest.fixture()
def sr(request, **kwargs):
    return _get_client(niceredis.StrictRedis, request, **kwargs)