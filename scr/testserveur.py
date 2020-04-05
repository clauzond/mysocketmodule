import mysocketmodule

try:
    server.close()
except:
    pass
server = mysocketmodule.Server(25565)

print("En écoute pour 5s")
try:
    server.listen(5)
except:
    server.close()

while server.ouvert:

    msg = server.receive()

    bool=False
    for liste in msg:
        if len(liste)>0:
            bool=True
    if bool:
        print("[PRINTLOCAL]",msg)

    a = str(input(">"))

    if a=="quit()":
        break
    elif a=="listen()":
        server.listen(5)
    elif a=="list()":
        print(server.clientlist)
    elif "close(" in a:
        server.close_client(int(a[6:-1]))
    else:
        server.send_all(a)



server.close()