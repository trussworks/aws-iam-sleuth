from freezegun import freeze_time

import datetime
import pytest

from sleuth.auditor import Key


@freeze_time("2019-01-16")
class TestKey():
    def test_normal(self):
        """Normal happy path, key is good"""
        created = datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
        k = Key('username', 'keyid', 'Active', created)
        k.audit(60, 80)

        assert k.age == 15
        assert k.audit_state == 'good'

    def test_rotate(self):
        """Key is past rotate age, key is marked as old"""
        created = datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
        k = Key('username', 'keyid', 'Active', created)
        k.audit(10, 80)

        assert k.audit_state == 'old'

    def test_old(self):
        """Key is past max threshold, key is marked as expired"""
        created = datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
        k = Key('username', 'keyid', 'Active', created)
        k.audit(10, 11)

        assert k.audit_state == 'expire'

    def test_no_disable(self, monkeypatch):
        """Key is disabled AWS status of Inactive, but disabling is turned off so key remains audit state expire"""
        monkeypatch.setenv('ENABLE_AUTO_EXPIRE', 'false')
        created = datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
        k = Key('username', 'keyid', 'Inactive', created)

        k.audit(10, 11)
        assert k.audit_state == 'expire'

    def test_inactive(self, monkeypatch):
        """Key is disabled AWS status of Inactive, key marked is disabled"""
        monkeypatch.setenv('ENABLE_AUTO_EXPIRE', 'true')
        created = datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
        k = Key('username', 'keyid', 'Inactive', created)

        k.audit(10, 11)
        assert k.audit_state == 'disabled'
        k.audit(60, 80)
        assert k.audit_state == 'disabled'


    def test_invalid(self):
        """Key is disabled AWS status of Inactive, key marked is disabled"""
        created = datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)
        k = Key('username', 'keyid', 'Inactive', created)

        with pytest.raises(AssertionError):
            k.audit(5, 1)