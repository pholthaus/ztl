This project contains the `ZTL` library enabling light-weight and widely compatible **remote task execution** using [ZeroMQ](https://zeromq.org/).

The basic communication principle is as follows:

![communication overview](res/overview.png)

Thereby, each task has the following lifecycle:

![task lifecycle](res/task%20lifecycle.png)

An example communication could look like this:

Request:

![communication overview](res/protocol.png)

Reply:

![communication overview](res/protocol%20reply.png)