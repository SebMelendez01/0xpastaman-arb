using Sockets

clientside = connect(8080)

println(clientside,"Hello World from the Echo Server")
line = readline(clientside)
print(line);

close(clientside)