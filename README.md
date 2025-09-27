This project contains the `ZTL` library enabling light-weight and widely compatible **remote task execution** using [ZeroMQ](https://zeromq.org/).


# System requirements:

 * ZTL is compatible with all major operating systems running Python and is independent of any specific hardware.
 * ZTL has been tested on Ubuntu versions 16.04, 18.04, 20.04, 22.04, 24.04.
 * ZTL has the following dependencies:
   * [pyzmq](https://pypi.org/project/pyzmq/)
   * [oyaml](https://pypi.org/project/oyaml/)
   * pytest, pytest-xprocess (for testing only)


# Installation guide:

You can easily install ZTL in a Python virtual environment.
To create such an environment in your home directory on a modern Ubuntu (using Python version 3), follow the below steps.
You can install into any existing virtual environment or change the installation folder from ~/ztl to any other folder you prefer.

```bash
 apt install python3-pip python3-venv
 python3 -m venv ~/ztl
 source ~/ztl/bin/activate
 pip3 install ztl
```

For older operating systems using Python version 2, please use the following process:

```bash
 apt install python-pip python-virtualenv
 virtualenv ~/ztl
 source ~/ztl/bin/activate
 pip install git+https://gitlab.com/robothouse/rh-user/ztl
```

You can also clone this repository and use the sources directly:

```bash
git clone https://gitlab.com/robothouse/rh-user/ztl ~/ztl-src
```

# Demo:

To test the correct installation of ZTL, you can use the following steps.

First, spawn a server listening on port 12345 and the scope `/test`:

```bash
> ztl_task_server 12345 /test
INFO:remote-task:Task Server listening at 'tcp://*:12345'
INFO:remote-task:Registering controller for scope '/test'.
```
The output confirms that the server component is listening at the specified port and spawns a controller to handle tasks on scope `/test`.
Then, call the server at the same port (on the local machine) under the same scope `/test` using a client (in a different terminal) to see how it replies:

```bash
> ztl_task_client localhost 12345 /test some-handler:executing-component:goal-state
Connecting to host 'localhost:12345' at scope '/test'...
INFO:remote-task:Remote task interface initialised at 'tcp://localhost:12345'.
Triggering task with request 'c29tZS1oYW5kbGVywqxleGVjdXRpbmctY29tcG9uZW50wqxnb2FsLXN0YXRl'...
Initialised task with ID '1' for 5s. Reply is 'Initiated task '1' with request: c29tZS1oYW5kbGVywqxleGVjdXRpbmctY29tcG9uZW50wqxnb2FsLXN0YXRl'.
Task with ID '1' finished in state 'COMPLETED' while waiting. Result is 'finished'.
```

The output shows successful connection with the server, the creation of a remote task as an interface to the server, whic then gets triggered.
The reply that the client receives indicates that the server has successfully initialised a task and given it the ID 1.
After completion of the task, the client receives a completion message with the result "finished".
If we now look back at the server side, we find that the server also provided some insights about the communication.

```bash
Initialising Task ID '1' (c29tZS1oYW5kbGVywqxleGVjdXRpbmctY29tcG9uZW50wqxnb2FsLXN0YXRl)...
handler: some-handler
component: executing-component
goal: goal-state
Status Task ID '1' (waiting poll)...
Status Task ID '1' (waiting poll)...
Status Task ID '1' (waiting poll)...
...
```
We find that the client first initialises a task (with the specification of handler, component, and goal) and then polls the server periodically about the status of the task it has provided.

# Instructions for use:

To implement your own server in Python, you can use the following as an example. This code, however, will reject any task and never execute the `status()` or `abort()` functions since the task is never initialised correctly. For a slightly longer working example including an executable task, refer to [task_server.py](src/ztl/example/task_server.py) in the examples.

```python
from ztl.core.task import TaskController
from ztl.core.protocol import State
from ztl.core.server import TaskServer

class NoneController(TaskController):

    def init(self, request):
        return -1, "Not implemented"


    def status(self, mid, request):
        return State.FAILED, "Not implemented"


    def abort(self, mid, request):    
        return State.REJECTED, "Not implemented"

server = TaskServer(12345)
server.register("/test", NoneController())
server.listen()
```

A client to trigger the above server can be implemented as follows:

```python
from ztl.core.client import RemoteTask
from ztl.core.protocol import State, Task

task = RemoteTask("localhost", 12545, "/test")
request = Task.encode("some-handler", "executing-component", "goal-state")
task_id, reply = task.trigger(request)
```

# Architecture overview

The basic communication principle is as follows:

![communication overview](res/overview.png)

Thereby, each task has the following lifecycle:

![task lifecycle](res/task%20lifecycle.png)

An example communication could look like this:

Request:

![communication overview](res/protocol.png)

Reply:

![communication overview](res/protocol%20reply.png)