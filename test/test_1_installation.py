from unittest import TestCase

class TestUnitTests(TestCase):

    def test_unit_testing(self):
        self.assertTrue(True)

class TestImports(TestCase):

    def test_zmq_import(self):
        import zmq

    def test_ztl_protocol_imports(self):
        from ztl.core.protocol import Message, Request, State, Task

    def test_ztl_server_imports(self):
        from ztl.core.server import TaskServer

    def test_ztl_client_imports(self):
        from ztl.core.client import RemoteTask

    def test_ztl_task_imports(self):
        from ztl.core.task import ExecutableTask, TaskController, TaskExecutor
