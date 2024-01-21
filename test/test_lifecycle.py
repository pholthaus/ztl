import pytest

from unittest import TestCase

from ztl.core.client import RemoteTask
from ztl.core.server import TaskServer
from ztl.core.protocol import State

@pytest.mark.usefixtures("ztl_server")
class TestLocalLife(TestCase):

  def test_no_controller(self):
    host = "localhost"
    scope = "/no"
    payload = "does not matter"

    task = RemoteTask("localhost", 7777, scope)
    mid = task.trigger(payload)

    assert mid < 0

  def test_none_controller(self):
    host = "localhost"
    scope = "/none"
    payload = "does not matter"

    task = RemoteTask("localhost", 7777, scope)
    mid = task.trigger(payload)

    assert mid < 0

@pytest.mark.usefixtures("ztl_simple_server")
class TestLifeCycle(TestCase):

  def test_reject(self):
    host = "localhost"
    scope = "/test"
    payload = "illegal payload"

    task = RemoteTask("localhost", 5555, scope)
    mid = task.trigger(payload)

    assert mid < 0

  def test_abort(self):
    host = "localhost"
    scope = "/test"
    payload = 5

    task = RemoteTask("localhost", 5555, scope)
    mid = task.trigger(payload)

    assert mid > 0

    state = task.wait(mid, .1)
    assert state == State.ACCEPTED

    state = task.abort(mid)
    assert state == State.ABORTED

  def test_completion(self):
    host = "localhost"
    scope = "/test"
    payload = 5

    task = RemoteTask("localhost", 5555, scope)
    mid = task.trigger(payload)

    assert mid > 0

    state = task.wait(mid, .1)
    assert state == State.ACCEPTED

    state = task.wait(mid, 3.1)
    assert state == State.COMPLETED
