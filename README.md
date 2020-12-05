# OwnTunnel

As Server, you can run: 

```shell script
python server.py -p 8080 -t 8081
```

And then, start the client in the same machine:

```shell script
python client.py -ts <ServerIp> -tp 8080 -ds <DstIp> -dp <DstPort>
```

Now, the tunnel between the client and server started.

you can send data to `<ServerIP>:8081` to access the `DstIP:DstPort` you specified.
