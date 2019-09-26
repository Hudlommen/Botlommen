import xml.etree.ElementTree as ET
import time
import socket

HOST = "irc.twitch.tv"
PORT = 6667
PASS = "[hidden]"
NICK = "botlommen"
CHANNEL = "#spammiej"

readbuffer =""


class set_xml:
    def data():
        tree = ET.parse('data.xml')
        root = tree.getroot()
        return tree, root
    def players():
        tree = ET.parse('players.xml')
        root = tree.getroot()
        return tree, root
    def lottery():
        tree = ET.parse('lottery.xml')
        root = tree.getroot()
        return tree, root
    def tournament():
        tree = ET.parse('tournament.xml')
        root = tree.getroot()
        return tree, root
    def delta():
        tree = ET.parse('delta.xml')
        root = tree.getroot()
        return tree, root




class openSocket:
    def caller():
        s = socket.socket()
        s.connect((HOST, PORT))
        s.setblocking(0)
        s.settimeout(3)
        s.send(("PASS " + PASS + "\r\n").encode())
        s.send(("NICK " + PASS + "\r\n").encode())
        s.send(("JOIN " + CHANNEL + "\r\n").encode())
        return s


class joinRoom:
    def __init__(self,s):
        readbuffer = ""
        Loading = True
        while Loading:
            readbuffer = readbuffer.encode() + s.recv(1024)
            temp = str.split(readbuffer.decode(), "\n")
            readbuffer = temp.pop()

            for line in temp:
                print(line)
                if "End of /NAMES list" in line:
                    Loading = False
        sendMessage(s, "Joined room")


class holder:
    def __init__(self):
        self.readbuffer = ""
        self.person = ""
        self.locked = False
        self.score = ""
        self.timer = 0
        self.messagesAllowed = True
        self.spamTimer = 0
        self.spamAllowed = True
        self.infoSpam = 0
        self.tournamentTimer = 0
        self.tournamentLongTimer = 0
        self.tournamentAllowed = True
        self.listof = "Alluring Amazing Aphrodisiac Arousing Attractive Bosomy Breathtaking Curvy Delicious Desirable Dirty Enchanting Enticing Erotic Exquisite Fascinating Fetching Foxy Frisky Full-bosomed Glamorous Good-looking Gorgeous Heart-stopping Horny Hot Juicy Kinky Lovely Lustful Lusty Naughty Petite Playful Pretty Promiscuous Provocative Rousing Seductive Sexed up Sexy Shameless Stylish Suggestive Tantalizing Teasing Tempting Wicked Wild Voluptuous"
        self.listof2 = "angel babe beast beauty bunny chick cupcake cutie doll fox honey peach"

class call_xml_data:
    def __init__(self):
        [tree, root] = set_xml.data()
        for child in root.findall("data"):
            self.count = int(child.attrib["count"])
            self.avg = int(child.attrib["avg"])
            self.total = int(child.attrib["total"])


class call_xml_score:
    def __init__(self,choice):
        [tree, root] = set_xml.data()
        if choice == "H":
            choice_ = "highest"
        else:
            choice_ = "lowest"

        for child in root.findall(choice_):
            self.count = int(child.attrib["count"])
            self.date = str(child.attrib["date"])
            self.name = str(child.attrib["name"])
            self.score = int(child.attrib["score"])


class call_xml_player:
    def __init__(self, username):
        [tree, root] = set_xml.players()
        self.found = False
        self.message = ""
        print(username)
        for child in root.findall("player"):
            if str(username) == str(child.attrib["name"]).lower():
                try:
                    self.name = str(child.attrib["name"])
                    self.count = str(child.attrib["count"])
                    self.Hscore = str(child.attrib["Highscore"])
                    self.Hdate = str(child.attrib["Highdate"])
                    self.Hcount = str(child.attrib["Highcount"])
                    self.Lscore = str(child.attrib["Lowscore"])
                    self.Ldate = str(child.attrib["Lowdate"])
                    self.Lcount = str(child.attrib["Lowcount"])
                    self.Dscore = str(child.attrib["Deltascore"])
                    self.Dcount = str(child.attrib["Deltacount"])
                    self.Ddate = str(child.attrib["Deltadate"])
                    self.found = True
                    self.message = "@{} has a HIGH score of {:,} set on {} after {:,} tries --- a LOW score of {:,} set on {} after {:,} tries. - Total tries: {:,} --- Best Delta: {:,} set on {}. Total delta tries: {:,} ".format(str(self.name), int(self.Hscore), self.Hdate, int(self.Hcount), int(self.Lscore), self.Ldate, int(self.Lcount), int(self.count), int(self.Dscore), self.Ddate, int(self.Dcount))
                except:
                    print("############################ --- INCOMPLETE PLAYER DATA!!! --- ############################")
        if not self.found:
            self.message = "Player not found"


class updatePlayer:
    def __init__(self,username,score,delta):
        [tree, root] = set_xml.players()
        player = call_xml_player(username)
        print(player.found)
        if player.found:
            for child in root.iter("player"):
                if username == str(child.attrib["name"]):
                    if delta == -1:
                        count = int(player.count)+1
                        child.set('count', str(int(count)))
                    if delta > -1:
                        delta_count = int(player.Dcount)+1
                        child.set('Deltacount', str(delta_count))
                    if score > int(player.Hscore):
                        child.set('Highscore', str(score))
                        child.set('Highdate', time.strftime("%d.%m.%y %H:%M"))
                        child.set('Highcount', str(count))
                    if score < int(player.Lscore):
                        child.set('Lowscore', str(score))
                        child.set('Lowdate', time.strftime("%d.%m.%y %H:%M"))
                        child.set('Lowcount', str(count))
                    if delta > -1 and delta < int(player.Dscore):
                        child.set('Deltascore', str(delta))
                        child.set('Deltadate', time.strftime("%d.%m.%y %H:%M"))
                        child.set('Deltacount', str(delta_count))
                    tree.write('players.xml')
        else:
            new_player = ET.SubElement(root,'player Highcount="1" Highdate="{0}" Highscore="{1}" Lowcount="1" Lowdate="{0}" Lowscore="{1}" count="1" name="{2}"'.format(str(time.strftime("%d.%m.%y %H:%M")), str(score),str(username)))
            tree.write('players.xml')


class updateData:
    def __init__(self,score):
        [tree, root] = set_xml.data()
        data = call_xml_data()
        data.count += 1
        data.total += score
        data.avg = int(data.total/data.count)

        for all in root.iter("data"):
            all.set('count', str(data.count))
            all.set('total', str(data.total))
            all.set('avg', str(data.avg))
            tree.write('data.xml')


class check_score:
    #Todo: add delta score
    def __init__(self,s,username,score):
        [tree, root] = set_xml.data()
        updateData(score)
        data = call_xml_data()
        H = call_xml_score("H")
        L = call_xml_score("L")
        checker = ""
        self.message = ""
        if score > H.score:
            checker = "highest"
            self.message = "new HIGH score of {} set by {}".format(str(score), str(username))
        if score < L.score:
            checker = "lowest"
            self.message = "new LOW score of {} set by {}".format(str(score), str(username))
        if checker != "":
            #sendMessage(s,self.message)
            for all in root.iter(checker):
                all.set('score', str(score))
                all.set('date', time.strftime("%d.%m.%y %H:%M"))
                all.set('count', str(data.count))
                all.set('name', username)
                tree.write('data.xml')

        if self.message != "":
            sendMessage(s, self.message)


class getUserMessage:
    def __init__(self, line):
        self.username = ""
        self.message = ""
        try:
            sep = line.split(":", 2)
            self.username = sep[1].split("!", 1)[0]
            self.message = sep[2]
        except:
            pass


class sendMessage:
    def __init__(self,s,message):
        messageTemp = "PRIVMSG " + CHANNEL + " :" + message
        data = messageTemp + "\r\n"
        s.send(data.encode())
        print("sent: " + messageTemp)


class stats:
    #Todo: Add delta score
    def __init__(self,s):
        H = call_xml_score("H")
        L = call_xml_score("L")
        message = "current HIGH score is: {:,} set by {} on the {} after {:,} tries --- current LOW score is: {:,} set by {} on the {} after {:,} tries".format(H.score,H.name,H.date,H.count, L.score,L.name,L.date,L.count)
        sendMessage(s, message)


class count:
    def __init__(self,s):
        data = call_xml_data()
        message = "skill has been called {:,} times, with an average score of {:,} and a total of {:,} LP given out".format(data.count,data.avg,data.total)
        sendMessage(s, message)


class botlommen:
    def __init__(self,s):
        message = "All: !tournament -> !t[0-100.000] - !stats - !count - !myStats - !skill [10-90k] - !info !news --- Whitelist: !rs - !ShutTheFucky - !ItsOkToSpam"
        sendMessage(s,message)


class info:
    def __init__(self,s):
        message = "Chatbot project by Hudlommen. For no real reason other than practising python programming as a hobby. Flow:[twitch-chat > code > XML > code > twitch-chat] --- Ive never been taught programming, its all autodidact, please keep that in mind :) main script: https://paste.ofcode.org/fsT9D3Dnuns3ZA8TXiZPbi - classes: https://paste.ofcode.org/3aPqXUPnhYuNRT7xQ2CHdmK"
        sendMessage(s, message)


class news:
    def __init__(self,s):
        #message = "Lottery [#] added. Set a number and if it get called, you win and the game restarts. I dunno how long it will take, it could take 10 minutes or it could take 11 minutes.. Only scores between 10k and 90k can be set to stop gaming --- Delta score is added. use !skill [#] to guess your skill. The close the better. Again limited between 10k and 90k to stop gaming"
        message = "Tournaments are now only accesable after 1 hour, +30k DNF - Case specific commands removed, because people are caseist savages.. Tournament mode (4 player) added. Use !tournament to enter and !t [0-100k] to set a score each round, when all have set a score call !skill. Finalist mode is set at 31 points, DNF at delta +30k. Tournament resets after 5 minutes of inactivity. Delta scores are not saved in tournament mode. Spam timer set to 1 sec. instead of 5."
        sendMessage(s, message)


class delta:
    def __init__(self,s,username, score):
        [tree, root] = set_xml.delta()
        self.found = False
        self.message = ""
        for child in root.findall("player"):
            if str(username) == str(child.attrib["name"]).lower():
                self.found = True
                self.score = int(child.attrib["score"])
                self.message = "Delta number: {:,} is already set for you @{}".format(self.score, username)

        if not self.found:
            x = score.find("[")
            y = score.find("]")
            if x > -1 and y > -1:
                try:
                    z = int(score[x + 1:y])
                    if z > 9999 and z < 90001:
                        new_player = ET.SubElement(root, 'player name="{}" score="{}"'.format(username, str(z)))
                        tree.write('delta.xml')
                    else:
                        self.message = "{} was not accpeted @{} - number has to be between 10k and 90k".format(str(z), username)
                except:
                    fail = str(score[x + 1:y])
                    self.message = "{} is not an accpeted input @{}".format(fail, username)
        if self.message != "":
            sendMessage(s, self.message)


class check_delta:
    def __init__(self,s,username, score):
        [tree, root] = set_xml.delta()
        self.message = ""
        self.deltaOn = False
        for child in root.findall("player"):
            print("Delta on!")
            self.deltaOn = True

        if self.deltaOn:
            for child in root.iter("player"):
                if str(username).lower() == str(child.attrib["name"]):
                    self.score_ = int(child.attrib["score"])
                    self.delta_score = abs(int(score)-self.score_)
                    self.message = "Delta: {:,}".format(self.delta_score)
                    updatePlayer(username,score,self.delta_score)
                    for child in root.findall("player"):
                        root.remove(child)
                        tree.write('delta.xml')
        if self.message != "":
            sendMessage(s, self.message)


class tournament:
        def __init__(self, s, username):
            [tree, root] = set_xml.tournament()
            self.found = False
            self.full = False
            self.players = ""

            for child in root.findall("data"):
                if not str(child.attrib["started"]) == "1":

                    for child in root.findall("player"):
                        if str(username) == str(child.attrib["name"]).lower():
                            self.found = True
                            self.message = "You are ALREADY in the tournament @{}".format(username)

                    if not self.found and not self.full:
                        new_player = ET.SubElement(root, 'player name="{}" score="-1" points="0"'.format(username))
                        self.message = "You are now in the tournament @{}".format(username)
                        tree.write('tournament.xml')

                    [tree, root] = set_xml.tournament()
                    n = 0
                    for child in root.findall("player"):
                        n += 1
                        self.players += str(child.attrib["name"]).lower() + " "
                        if n >= 4:
                            self.full = True

                    if self.full:
                        plyrs = self.players.split(" ")
                        self.message = "Tournament is starting with the following players: @{} @{} @{} @{} - glhf".format(plyrs[0],plyrs[1],plyrs[2],plyrs[3])
                        for all in root.iter("data"):
                            all.set('started', "1")
                            tree.write('tournament.xml')
                else:
                    self.message = "Tournament is already ongoing @{}".format(username)

            if self.message != "":
                sendMessage(s, self.message)


class reset_tournament:
    def __init__(self,s):
        [tree, root] = set_xml.tournament()
        self.message = "Tournament reset!"
        for all in root.iter("data"):
            all.set('started', "0")
            all.set('nextTournament', "0")
            tree.write('tournament.xml')

        for child in root.findall("player"):
            root.remove(child)
            tree.write('tournament.xml')

        if self.message != "":
            sendMessage(s, self.message)


class clear_tournament:
    def __init__(self):
        [tree, root] = set_xml.tournament()
        print("Tournament finished")
        for all in root.iter("data"):
            all.set('started', "0")
            all.set('nextTournament', str(int(time.time() + 3600)))
            tree.write('tournament.xml')

        for child in root.findall("player"):
            root.remove(child)
            tree.write('tournament.xml')




class check_tournament:
    def __init__(self,s,score):
        [tree, root] = set_xml.tournament()
        self.active = False
        self.set = True
        self.winnerFound = False
        self.message = ""
        for child in root.findall("data"):
            if str(child.attrib["started"]) == "1":
                self.active = True

        if self.active:
            for child in root.findall("player"):
                if str(child.attrib["score"]) == "-1":
                    self.set = False
                    self.message += str(child.attrib["name"]) + " "

        if self.set and self.active:
            # x = random.randint(0, 99999)
            # score = x
            print("Tournament on!")
            for child in root.findall("player"):
                delta = abs(int(child.attrib["score"]) - score)
                child.set('delta', str(delta))
            tree.write('tournament.xml')

            liste = []
            for child in root.findall("player"):
                delta = int(child.attrib["delta"])
                liste.append(delta)
                liste.sort()

            score = [10, 6, 4, 3]
            winningScore = 30
            n = -1
            message_ = ""
            self.winnerFound = False
            self.message = ""
            for each in liste:
                n += 1
                for child in root.findall("player"):
                    if int(child.attrib["delta"]) == each and each >= 30000:
                        temp_ = str(child.attrib["points"])
                        message_ += "- {}: {} (DNF) -".format(str(child.attrib["name"]), temp_, score[n])

                    if int(child.attrib["delta"]) == each and each < 30000:
                        temp_ = "finalist"
                        if n == 0 and str(child.attrib["points"]) == "finalist":
                            temp_ = "WINNER"
                            self.winnerFound = True
                        if not str(child.attrib["points"]) == "finalist":
                            temp_ = int(child.attrib["points"]) + score[n]
                            print(temp_)
                            if temp_ > winningScore:
                                temp_ = "finalist"
                        message_ += "- {}: {} (+{}) -".format(str(child.attrib["name"]), temp_, score[n])
                        child.set('points', str(temp_))
            tree.write('tournament.xml')
            self.message = message_
            if not self.winnerFound:
                for child in root.findall("player"):
                    child.set('score', str("-1"))
                    tree.write('tournament.xml')



        if not self.set:
            self.message = "Following players: " + self.message + "has not set a tournament skill guess yet"


        if self.message != "":
            sendMessage(s, self.message)

        if self.winnerFound:
            clear_tournament()


class set_tournament:
    def __init__(self,s,username,score):
        [tree, root] = set_xml.tournament()
        self.found = False
        self.message = ""
        self.set = True
        liste = []
        self.isinlist = False
        for child in root.findall("player"):
            liste.append(int(child.attrib["score"]))

        for child in root.findall("player"):
            if str(username) == str(child.attrib["name"]).lower():
                if int(child.attrib["score"]) > -1:
                    self.found = True
                    self.score = int(child.attrib["score"])
                    self.message = "Tournament: {:,} is already set for you @{}".format(self.score, username)

                if not self.found:
                    x = score.find("[")
                    y = score.find("]")
                    if x > -1 and y > -1:
                        try:
                            z = int(score[x + 1:y])
                            for each in liste:
                                if z in range(each-2500,each+2500):
                                    self.isinlist = True
                            if z > -1 and z < 100001 and not self.isinlist:
                                child.set('score', str(z))
                                tree.write('tournament.xml')
                            else:
                                self.message = "{} was not accpeted @{}".format(str(z), username)
                        except:
                            fail = str(score[x + 1:y])
                            self.message = "{} was not accpeted @{}".format(fail, username)

        for child in root.findall("player"):
            if str(child.attrib["score"]) == "-1":
                self.set = False

        if self.set:
            self.message = "Everyone has set a score, call !skill"

        if self.message != "":
            sendMessage(s, self.message)



