from ztl.core.client import RemoteTask
from ztl.core.protocol import State

def test_reject(ztl_simple_server):
  host = "localhost"
  scope = "/test"
  payload = "illegal payload"

  task = RemoteTask("localhost", 5555, scope)
  mid = task.trigger(payload)

  assert mid < 0

def test_abort(ztl_simple_server):
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

def test_completion(ztl_simple_server):
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
