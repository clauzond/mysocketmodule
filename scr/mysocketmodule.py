
"""
1. **SERVEUR**

2. **CLIENT**

"""

import socket

# == SERVER ==
class Server:

    # == __init__ ==
    def __init__(self,port):
        """
        Initialise le socket serveur 'self.mySocket'
        Initialise la liste vide 'self.clientlist'
        Initialise le booléen 'self.ouvert' à False
        Initialise l'entier 'self.nextnumber' à 0
        """
        self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mySocket.bind(('',port)) # '' signifie qu'il acceptera les requêtes peu importe l'interface (localhost, 192.0. ...)

        self.clientlist = [] # liste des clients, où l'indice i est [client,addr,self]

        self.ouvert = False

        self.nextnumber = 0

    # == __repr__ ==
    def __repr__(self):
        """
        Renvoie un string de la forme :
        [0] ip:port
        [1] ip:port
        ...

        """

        output = ""

        for liste in self.clientlist:
            client,addr,n = liste
            ip,port = addr


            output += "[%s] "%n + str(ip) + ":" + str(port) + "\n"

        return(output)

    # == listen ==
    def listen(self,timeout):
        """
        Le socket s'ouvre pour recevoir des connexions extérieurs, cela va FREEZE le déroulement des opérations jusqu'à obtiention d'un signal

        :timeout = float (temps d'attente en seconde avant expiration)
        """

        try:
            self.mySocket.settimeout(timeout)
            self.mySocket.listen(10)
            client, addr = self.mySocket.accept() # conn_avec_client est un socket
            self.clientlist.append([client,addr,self.nextnumber])

            print ("[PRINT] Connexion de : ",addr,self.nextnumber)
            self.send_to(self.nextnumber,"SERVER&&NUMBER&&%s&&end|"%self.nextnumber)
            self.send_everyone_except(self.nextnumber,"SERVER&&PRINT&&Connexion du client n°%s"%self.nextnumber)

            self.ouvert = True

            self.nextnumber += 1

        except:
            print("Client introuvable (%s s timeout)"%timeout)

    # == send_all ==
    def send_all(self,message):
        """
        Envoie un message à tous les clients

        exemple : je veux print partout "message_content" --> server.send(numberfrom+"&&"+pattern+"&&"+message_content)
        numberfrom est un string qui identifie l'envoyeur (peut être "abc123" par exemple)
        pattern est un string, motif à utiliser
        message_content est un string, argument du motif

        WARNING : si le symbole '&' est utilisé pour autre chose, il y a des risques d'erreur de syntaxe
        :message : string [format du message : numberfrom&&pattern&&message_content]
        """

        message = message.replace("&&end|","")

        if message == "":
            pass
        elif "|" in message:
            print("[PRINT] Erreur : il ne doit pas y avoir '|' dans votre message")
        else:
            for client,addr,number in self.clientlist:
                try:
                    client.send((message+"&&end|").encode())
                except:
                    print("[PRINT] Erreur d'envoie avec",addr,number)

    # == send_everyone_except ==
    def send_everyone_except(self,number,message):
        """
        Envoie un message à tous les clients, excepté le n°(number)

        exemple : je veux print partout "message_content" --> server.send_everyone_except(numberfrom+"&&"+pattern+"&&"+message_content)
        numberfrom est un string qui identifie l'envoyeur (peut être "abc123" par exemple)
        pattern est un string, motif à utiliser
        message_content est un string, argument du motif


        WARNING : si le symbole '&' est utilisé pour autre chose, il y a des risques d'erreur de syntaxe
        :number : int (numéro du client à ne pas envoyer le message)
        :message : string [format du message : numberfrom&&pattern&&message_content]
        """
        message = message.replace("&&end|","")

        if message == "":
            pass

        elif "|" in message:
            print("[PRINT] Erreur : il ne doit pas y avoir '|' dans votre message")

        else:
            for client,addr,n in self.clientlist:
                if n!=number:
                    try:
                        client.send((message+"&&end|").encode())
                    except:
                        print("[PRINT] Erreur d'envoie avec",addr,n)

    # == send_to ==
    def send_to(self,number,message):
        """
        Envoie un message à un client en particulier

        exemple : je veux print partout "message_content" --> server.send_to(number,numberfrom+"&&"+pattern+"&&"+message_content)
        numberfrom est un string qui identifie l'envoyeur (peut être "abc123" par exemple)
        pattern est un string, motif à utiliser
        message_content est un string, argument du motif

        WARNING : si le symbole '&' est utilisé pour autre chose, il y a des risques d'erreur de syntaxe
        :number : int (numéro du client auquel on envoie le message)
        :message : string (contenu du message à envoyer)
        """
        message = message.replace("&&end|","")

        if message == "":
            pass
        elif "|" in message:
            print("[PRINT] Erreur : il ne doit pas y avoir '|' dans votre message")
        else:
            client,addr,n = self.clientlist[number]
            try:
                client.send((message+"&&end|").encode())
            except:
                print("[PRINT] Erreur d'envoie avec",addr,n)

    # == receive ==
    def receive(self):
        """
        Tente de recevoir un message, d'un ou plusieurs clients
        message = string [format : numberfrom&&pattern&&message_content]

        return: liste_de_liste_data dont l'indice i représente la liste d'informations reçus par le client n°i (potentiellement [])
        """
        liste_de_liste_data = []

        for client,addr,n in self.clientlist :
            try:
                client.settimeout(0.1)
                message=client.recv(4096).decode()
            except:
                message=""
            liste_de_liste_data.append( self.treat_received_message(n,message) )

        return(liste_de_liste_data)

    def treat_received_message(self,number,message):
        """
        Traite les messages reçus
        Déroulement :
        1) Détecte si plusieurs messages ont été reçus en même temps (un client a envoyé plusieurs msg d'un coup par exemple) avec la méthode check_for_multiple_messages
        2) Traite chacun de ces messages individuellement avec la méthode check_for_multiple_messages
        3)  Message vide : Renvoie une liste vide
            Message non vide : Les motifs "TREATDATA" seront ajoutés à une liste dans un tupple (pattern,message_content)
                               Les autres motifs seront traités par la fonction pattern_recognition()

        Les motifs sont entièrement modifiables !


        :number = int
        :message = string [format : numberfrom&&pattern&&message_content]
        """

        if message == "":
            return([])
        else:
            return(self.check_for_multiple_messages(number,message))

    def check_for_multiple_messages(self,number,message):
        """
        Détecte si un ou plusieurs messages ont été envoyés, puis les envoie vers pattern_recognition

        message_content ne doit pas contenir le string '|'

        :number = int
        :message = string [format : numberfrom&&pattern&&message_content]
        return: liste_data de doublons (p,m) créés par pattern_recognition
        """

        # pme pour "pattern message end"
        # Le message sera composé de la forme p1&&m1&&e|p2&&m2&&e|p3....
        # "a&&b&&c.split("&&") -> ['a','b','c']

        liste_triplestring = message.split('|')
        del liste_triplestring[-1]
        liste_data = []

        for triplestring in liste_triplestring:

            if triplestring.count('|')>1 :
                print("[BUG] Le message reçu contient plusieurs occurences de '|'")

            infolist = triplestring.split('&&')

            numberfrom = infolist[0]

            pattern = infolist[1] # pattern

            message_content = "&&".join(infolist[2:-1]) # le contenu du message sera compris entre le premier '&&' et le dernier '&&'

            p,m = self.pattern_recognition(number,pattern,message_content)

            if (p,m)!=("",""):
                liste_data.append( (p,m) )

        return(liste_data)


    def check_for_one_message(self,number,message):
        """
        Version de 'check_for_multiple_messages' mais pour un seul message (typiquement dans un sendall)

        message_content ne doit pas contenir le string '|'

        :number = int
        :message = string [format : numberfrom&&pattern&&message_content]
        return: liste_data de doublons (p,m) créés par pattern_recognition
        """

        liste_triplestring = message.split('|')
        del liste_triplestring[-1]
        liste_data = []

        # Ici, liste_triplestring ne contient qu'un élément
        for triplestring in liste_triplestring:

            if triplestring.count('|')>1 :
                print("[BUG] Le message reçu contient plusieurs occurences de '|'")

            infolist = triplestring.split('&&')

            numberfrom = infolist[0]

            pattern = infolist[1] # pattern

            message_content = "&&".join(infolist[2:-1]) # le contenu du message sera compris entre le premier '&&' et le dernier '&&'

            p,m = self.pattern_recognition(number,pattern,message_content)

            return(p,m)

    # == patter_recognition ==
    def pattern_recognition(self,number,pattern,message_content):
        """
        Reconnaît les motifs d'un seul message

        Motifs actuels : SENDTOALL; LISTEN; PRINT;

        :number = int
        :message_content = string [c'est la partie message du format : numberfrom&&pattern&&message_content&&end| et qui ne contient pas '&&end|' ]
        return: (pattern, message_content) ou ('','')
        """

        if pattern == "TREATDATA":
            return(pattern,message_content)
        elif pattern == "PATTERN2":
            return(pattern,message_content)
        elif pattern == "PATTERN3":
            return(pattern,message_content)
        elif pattern == "PATTERN4":
            return(pattern,message_content)
        elif pattern == "PATTERN5":
            return(pattern,message_content)
        elif pattern == "SENDTOALL":
            # message_content est du format message, avec ou sans le &&end|
            # envoie la commande que voulait envoyer à la base le client n°number
            self.send_everyone_except(number,message_content)
            print("envoyé a tout le monde",message_content)

            msg = message_content.replace("&&end|","")
            return(self.check_for_one_message(number,msg+"&&end|"))
        elif pattern == "LISTEN":
            # message_content correspond au timeout
            try:
                self.listen(int(message_content))
                return('','')
            except:
                msg = "PRINT&&"+"[BUG] Erreur de syntaxe :"+pattern+message_content+"&&end|"
                self.send_to(number,msg)
                return('','')
        elif pattern == "PRINT":
            print("[%s]"%number,message_content)
            return('','')
        elif pattern == "CLIENTHASCLOSED":
            print("[PRINT] Le client numéro "+str(message_content)+" s'est déconnecté")
            self.client_has_closed(number)
            return('','')
        elif pattern == "STATUS":
            self.send_to(number,"SERVER&&PRINT&&"+str(self))
            return('','')
        else:
            msg = "SERVER&&PRINT&&"+"[BUG] Erreur de syntaxe :"+pattern+message_content+"&&end|"
            self.send_to(number,msg)
            return('','')

    # == close_client ==
    def close_client(self,number):
        """
        Ferme "manuellement" le client n°number, en réactualisant clientlist, nextnumber
        Envoie un message aux autres de leur réactualisation et de la déconnexion

        Cela ferme le client de son côté également (force sa déconnexion)

        :number = int (du client à fermer)
        """
        self.nextnumber -= 1

        client = self.clientlist[number][0]

        for i in range(0,len(self.clientlist)):
            if i!=number:
                self.send_to(i,"SERVER&&CLIENTHASCLOSED&&%s"%number)
            if i>number:
                self.send_to(i,"SERVER&&NUMBER&&%s"%(i-1))
                self.clientlist[i][2] = i-1

        self.send_to(number,"SERVER&&SERVERCLOSED&&mdr")

        client.close()

        del self.clientlist[number]

    def client_has_closed(self,number):
        """
        Ferme le client n°number qui s'est déconnecté (lui-même), en réactualisant clientlist, nextnumber
        Envoie un message aux autres de leur réactualisation et de la déconnexion

        WARNING : cela ne ferme pas le client de son côté, on suppose qu'il l'a déjà fait lui-même

        :number = int (le client qui s'est déconnecté)
        """

        self.nextnumber -= 1

        client = self.clientlist[number][0]

        for i in range(0,len(self.clientlist)):
            if i!=number:
                self.send_to(i,"SERVER&&CLIENTHASCLOSED&&%s"%number)
            if i>number:
                self.send_to(i,"SERVER&&NUMBER&&%s"%(i-1))
                self.clientlist[i][2] = i-1
        client.close()

        del self.clientlist[number]





    # == close ==
    def close(self):
        """
        Ferme le serveur, et ferme les clients avec.
        """
        print("[PRINT] mySocket fermé")
        self.send_all("SERVER&&SERVERCLOSED&&_&&end|")
        self.ouvert = False
        self.mySocket.close()



# == CLIENT ==
class Client:
    # == init ==
    def __init__(self):
        """
        Initialise le socket 'self.mySocket'
        Initialise le booléen 'self.ouvert'
        Initialise l'entier 'self.number'

        """
        self.mySocket = socket_du_client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ouvert = False
        self.number = "-1"

    # == connect_to ==
    def connect_to(self,ip,port):
        """
        Tente de se connecter à l'hôte 'ip:port'

        """
        try:
            self.mySocket.connect((ip,port))
            self.ip , self.port = ip,port
            self.ouvert = True
            print("[PRINT] En attente de listen de la part du serveur...")
        except:
            print("[PRINT] Serveur non ouvert !")


    # == send_all ==
    def send_all(self,message):
        """
        Envoie un message à tout le monde : le serveur et les autres clients
        exemple : je veux print partout "message_content" --> client.send_all(numberfrom+"&&"+pattern+"&&"+message_content)
        numberfrom est

        On peut mettre '&&end|' dedans ou non, il sera de toute façon remplacé

        Attention : si le symbole '&' est utilisé pour autre chose, il y a des risques d'erreur de syntaxe

        :message = string du format numberfrom&&pattern&&message_content(optionnel : &&end|)
        return: None
        """
        message = message.replace("&&end|","")
        if message == "":
            pass
        elif "|" in message:
            print("[PRINT] Erreur : il ne doit pas y avoir '|' dans votre message")
        else:
            try:
                self.mySocket.send(("%s&&SENDTOALL&&"%self.number+message+"&&end|").encode())
            except:
                print("[PRINT] Erreur d'envoie vers all")

    # == send_server ==
    def send_server(self,message):
        """
        Envoie un message au serveur

        exemple : je veux print au serveur "message_content" --> client.send_server(numberfrom+"&&"+pattern+"&&"+message_content)
        On peut mettre '&&end|' dedans ou non, il sera de toute façon remplacé

        Attention : si le symbole '&' est utilisé pour autre chose, il y a des risques d'erreur de syntaxe

        :message = string du format numberfrom&&pattern&&message_content(optionnel : &&end|)
        return: None
        """
        message = message.replace("&&end|","")

        if message =="":
            pass
        elif "|" in message:
            print("[PRINT] Erreur : il ne doit pas y avoir '|' dans votre message")
        else:
            try:
                self.mySocket.send((message+"&&end|").encode())
            except:
                print("[PRINT] Erreur d'envoie vers server")

    # == receive ==
    def receive(self):
        """
        A mettre dans une **LOOP**

        Tente de recevoir un message du serveur (potentiellement plusieurs messages en même temps)
        message = string [format : numberfrom&&pattern&&message_content&&end|]

        return: liste_data (la liste d'informations reçus par le serveur, chaque information est un tupple (pattern,message_content))
        """

        try:
            self.mySocket.settimeout(0.1)
            message=self.mySocket.recv(4096).decode()
        except:
            message=""

        liste_data =self.treat_received_message(message)
        return(liste_data)

    def treat_received_message(self,message):
        """
        Traite les messages reçus
        Déroulement :
        1) Détecte si plusieurs messages ont été reçus en même temps (le serveur a envoyé plusieurs msg d'un coup par exemple) avec la méthode check_for_multiple_messages
        2) Traite chacun de ces messages individuellement avec la méthode check_for_multiple_messages
        3)  Message vide : Renvoie une liste vide
            Message non vide : Les motifs "TREATDATA" seront ajoutés à une liste dans un tupple (pattern,message_content)
                               Les autres motifs seront traités par la fonction pattern_recognition()

        Les motifs sont entièrement modifiables !


        :number = int
        :message = string [format : numberfrom&&pattern&&message_content&&end|]
        """

        if message == "":
            return([])
        else:
            return(self.check_for_multiple_messages(message))

    def check_for_multiple_messages(self,message):
        """
        Détecte si un ou plusieurs messages ont été envoyés, puis les envoie vers pattern_recognition

        message_content ne doit pas contenir le string '|'
        message_content peut être comme le format de message, mais sans le &&end| à la fin
        message_content peut être un simple string non formatté, tant qu'il n'y a pas '|' à l'intérieur

        :number = int
        :message = string [format : numberfrom&&pattern&&message_content&&end|]
        return: liste_data de doublons (p,m) créés par pattern_recognition
        """


        liste_triplestring = message.split('|')
        del liste_triplestring[-1]
        liste_data = []

        for triplestring in liste_triplestring:

            if triplestring.count('|')>1 :
                print("[BUG] Le message reçu contient plusieurs occurences de '|'")


            infolist = triplestring.split('&&')


            numberfrom = infolist[0]

            pattern = infolist[1] # pattern


            message_content = "&&".join(infolist[2:-1]) # le contenu du message sera compris entre le premier '&&' et le dernier '&&'


            p,m = self.pattern_recognition(numberfrom,pattern,message_content)

            if (p,m)!=("",""):
                liste_data.append( (p,m) )

        return(liste_data)

    # == pattern_recognition ==
    def pattern_recognition(self,numberfrom,pattern,message_content):
        """
        Reconnaît les motifs d'un seul message

        Motifs actuels : TREATDATA; NUMBER; PRINT; CLIENTHASCLOSED; SERVERCLOSED; STATUS

        :number = int
        :message_content = string [c'est la partie message du format : numberfrom&&pattern&&message_content&&end| et qui ne contient pas '&&end|' ]
        return: (pattern, message_content) ou ('','')
        """

        if pattern == "TREATDATA":
            return(pattern,message_content)
        elif pattern == "PATTERN2":
            return(pattern,message_content)
        elif pattern == "PATTERN3":
            return(pattern,message_content)
        elif pattern == "PATTERN4":
            return(pattern,message_content)
        elif pattern == "PATTERN5":
            return(pattern,message_content)
        elif pattern == "NUMBER":
            # message_content est le nombre attribué au client
            if self.number=="-1":
                self.number = str(message_content)
                print("[PRINT] Connexion effectuée ! Je suis le client n°%s"%self.number)
                return('','')
            elif self.number != str(message_content):
                self.number = str(message_content)
                print("[PRINT] J'ai changé de numéro ! Je suis maintenant le client n°%s"%self.number)
                return('','')
        elif pattern == "CLIENTHASCLOSED":
            # message_content est le numéro du client qui a fermé
            print("[PRINT] Le client numéro "+str(message_content)+" s'est déconnecté")
            return('','')
        elif pattern == "PRINT":
            print("[%s]"%numberfrom,message_content)
            return('','')
        elif pattern == "SERVERCLOSED":
            # message_content ne contient rien d'intéressant
            print("[PRINT] Vous avez été déconnecté par le serveur !")
            self.ouvert = False
            self.close()
            return('','')

        elif pattern == "STATUS":
            # ce message n'était pas destiné au client
            return('','')
        else:
            msg = "%s&&PRINT&&"%self.number+"[BUG] Erreur de syntaxe :"+numberfrom+" "+pattern+" "+message_content
            self.send_server(msg)
            return('','')


    # == close ==
    def close(self):
        """
        Ferme le client, et envoie un message au serveur (si ce n'est pas déjà fait)

        Si self.ouvert == True, alors c'est une fermeture manuelle
        Sinon, c'est que le serveur a shutdown manuellement ce client
        """
        if self.ouvert:
            self.send_server("%s&&CLIENTHASCLOSED&&%s"%(self.number,self.number))
        self.mySocket.close()
        self.ouvert = False
        print("[PRINT] mySocket fermé")