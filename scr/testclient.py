import mysocketmodule

client = mysocketmodule.Client()

client.connect_to('localhost',25565)


while client.ouvert:

    msg=client.receive()

    if len(msg)>0:
        print("[PRINTLOCAL]",msg)

    a = str(input(">"))

    if a=="quit()":
        client.close()
    else:
        client.send_all(a)



client.close()