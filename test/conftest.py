import pytest
from xprocess import ProcessStarter

@pytest.fixture(scope="session")
def ztl_simple_server(xprocess):
    class Starter(ProcessStarter):
        # startup pattern
        pattern = "Task Server listening"

        # command to start process
        args = ['ztl_simple_server', "/test"]

    # ensure process is running and return its logfile
    logfile = xprocess.ensure("ztl_simple_server", Starter)

    yield


    # clean up whole process tree afterwards
    xprocess.getinfo("ztl_simple_server").terminate()

