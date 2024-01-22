import pytest
import threading
from xprocess import ProcessStarter

from ztl.core.server import TaskServer

@pytest.fixture(scope="class")
def ztl_simple_server(xprocess):

    class Starter(ProcessStarter):
        pattern = "Task Server listening"
        args = ['ztl_simple_server', 7777, "/test"]

    logfile = xprocess.ensure("ztl_simple_server", Starter)

    yield

    xprocess.getinfo("ztl_simple_server").terminate()

@pytest.fixture(scope="class")
def ztl_server():

    server = TaskServer(7778)
    server.register("/none", None)

    thread = threading.Thread(target=server.listen)
    thread.daemon = True
    thread.start()

    yield server
