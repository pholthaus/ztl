from unittest import TestCase

class TestUnitTest(TestCase):
  
    def test_unit_testing(self):
        self.assertTrue(True)

class TestImports(TestCase):
    
    def test_zmq_import(self):
        import zmq

    def test_ztl_protocol_imports(self):
        from ztl.core.protocol import Message, Request, State, Task
