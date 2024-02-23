import pytest

from unittest import TestCase
from ztl.core.protocol import Message, Request, State, Task

@pytest.mark.usefixtures("ztl_data")
class TestDataTypes(TestCase):

    def test_message_codec(self):

      encoded = Message.encode(self.msg["scope"], self.msg["state"], self.msg["id"], self.msg["payload"])
      assert type(encoded) is bytes

      decoded = Message.decode(encoded)
      assert type(decoded) is dict

      for field in self.msg.keys():
        assert type(decoded[field]) is str
        assert decoded[field] == self.msg[field]

    def test_task_codec(self):

      encoded = Task.encode(self.task["handler"], self.task["component"], self.task["goal"])
      assert type(encoded) is str

      decoded = Task.decode(encoded)
      assert type(decoded) is dict

      for field in self.task.keys():
        assert type(decoded[field]) is str
        assert decoded[field] == self.task[field]
