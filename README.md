This project contains the `ZTL` library enabling light-weight and widely compatible **remote task execution** using [ZeroMQ](https://zeromq.org/).


# System requirements:

 * ZTL is compatible with all major operating systems running Python and is independent of any specific hardware.
 * ZTL has been tested on Ubuntu versions 16.04, 18.04, 20.04, 22.04, 24.04.
 * ZTL has the following dependencies:
   * [pyzmq](https://pypi.org/project/pyzmq/)
   * [oyaml](https://pypi.org/project/oyaml/)
   * pytest, pytest-xprocess (for testing only)


# Quick usage (modern Ubuntu)

If you know what you are doing and operate a modern Ubuntu using Python 3, follow these simple steps for installing ZTL in a virtual environment. You can then skip the detailled Installation Guide and try the Demo directly.

```bash
> sudo apt install python3-pip python3-venv
> python3 -m venv ~/ztl
> source ~/ztl/bin/activate
> pip install ztl
```

# Detailled installation guide

You can easily install and use ZTL in a Python virtual environment in a two-step process. First, we need to setup the virtual environment and then install the library depending on your preferences. The process described covers various Ubuntu versions but the library can also be installed and used in Windows using  using slightly different commands.

## Preparing the virtual environment

To create such an environment in your home directory, follow the below steps.
You can install into any existing virtual environment or change the installation folder from ~/ztl to any other folder you prefer.

For modern Ubuntu-based systems using Python 3, the first step is to install the necessary packages and then to create and activate a virtual environment.
Package installation will need administrator rights and might fail. Installation on other operating systems might also vary, but you should make sure to have `pip` and `venv` modules for python ready. 

```bash
> sudo apt install python3-pip python3-venv
> python3 -m venv ~/ztl
```

For older Ubuntu systems using Python version 2, please use the following steps instead:

```bash
> sudo apt install python-pip python-virtualenv
> virtualenv ~/ztl
```

No matter which python version, next you need to load this environment.
You have to repeat this step for every terminal you want to use the library in:

```bash
> source ~/ztl/bin/activate
```

## Installing the library

There are multiple possibilities to install the library on your system. All are valid alternatives, however, some are restricted to specific Python versions.

### Option 1 (pip)

On modern systems with Python 3, you can simply use pip for installation. Add the option `--upgrade` to update to the latest version.

```bash
> pip install ztl
```

### Option 2 (zip file)

Alternatively, you can download and unpack the source code, independent of your Python version. Please check the `.zip` file for any subfolders containing the actual files (e.g. when you download from the gitlab repository, it will create a subfolder called `ztl-main`).

```bash
> unzip /path/to/ztl.zip -d ~/ztl-src
> pip install ~/ztl-src
```

### Option 3 (repository)

You can also clone the repository directly and install the latest sources, independent of your Python version. If you replace `main` with a branch or tag, you can install specific versions.

```bash
> pip install git+https://gitlab.com/robothouse/rh-user/ztl@main
```

# Demo

To test the correct installation of ZTL, you can use the following steps. Please remember to activate the virtual environment for each terminal.

```bash
> source ~/ztl/bin/activate
```

## Simple client-server communication

First, spawn a server listening on port 12345 and the scope `/test`:

```bash
> ztl_task_server -p 12345 -s /test
INFO:remote-task:Task Server listening at 'tcp://*:12345'
INFO:remote-task:Registering controller for scope '/test'.
```
The output confirms that the server component is listening at the specified port and spawns a controller to handle tasks on scope `/test`.
Then, call the server at the same port (on the local machine) under the same scope `/test` using a client (in a different terminal) to see how it replies:

```bash
> ztl_task_client -r localhost -p 12345 -s /test some-handler:executing-component:goal-state
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
Status Task ID '1' (waiting poll): ACCEPTED.
Status Task ID '1' (waiting poll): ACCEPTED.
...
Status Task ID '1' (waiting poll): COMPLETED.
```
We find that the client first initialises a task (with the specification of handler, component, and goal) and then polls the server periodically about the status of the task it has provided.

## Scripting example

To test the scripting interface, you can use the configurations provided in the [example](src/ztl/example/) folder (Note: these are not installed using `pip` but are part of the source code package). First, we need to start a task server, for which one of the example servers is sufficient as it provides all the necessary communication with the scripting engine. Please remember to activate the virtual environment for each terminal.

```bash
> ztl_task_server -p 7779 -s /test
```

Next, download the configuration files if you do not have them yet.

```bash
> git clone https://gitlab.com/robothouse/rh-user/ztl ~/ztl-src
```

Run the sample scripts:

```bash
> cd ~/ztl-src/src/ztl/example/
> ztl_run_script -s sample_script_short.yaml -c sample_conf.yaml
INFO:script-exec:Initialising remote task interface 'testhandler'...
INFO:remote-task:Remote task interface initialised at 'tcp://localhost:7779'.

----------------------------
ABOUT TO EXECUTE SCENE 'scene'
STEP: first step
        testhandler [print]: -> test me
STEP: second step
        testhandler [print]: -> another test
PRESS <ENTER> TO CONFIRM or ANY OTHER KEY TO SKIP
```

You can now trigger the example scene by pressing `ENTER`, which will execute a single scene consisting of two steps in sequence, both calling the `testhandler` we started above. You can also skip the scene to finish the script immediately. Again, the server will output the triggering, acceptance, and completion of both calls. You can modify the script to call multiple handlers in each step but you have to configure them in the file `sample_conf.yaml` and start another `ztl_task_server` to match this configuration.

# Instructions for use

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
