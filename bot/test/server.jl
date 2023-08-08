using Sockets

server = listen(8080)
while true
    sock = accept(server)
    @async while isopen(sock)
        line = readline(sock, keep=true)
        print(line)
        write(sock, line)
    end
end
