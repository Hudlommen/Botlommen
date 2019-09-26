import select
import time
from classes import *
import random

s = openSocket.caller()
joinRoom(s)
h = holder()
h.infoSpam = int(time.time())

whitelist = ["spammiej", "hudlommen_"]

listof = h.listof.split(" ")
listof2 = h.listof2.split(" ")


while True:
    time_ = int(time.time())
    if h.timer > 0 and time_ > h.timer+30:
        print("***** skill unlocked *****")
        h.timer = 0
        h.person = ""
        h.score = 0

    if h.spamTimer > 0 and time_ > h.spamTimer+1:
        print("***** spam unlocked *****")
        h.spamAllowed = True
        h.spamTimer = 0

    if h.infoSpam > 0 and time_ > h.infoSpam + 3600:
        botlommen(s)
        h.infoSpam = time_

    if h.tournamentTimer > 0 and time_ > h.tournamentTimer + 300:
        reset_tournament(s)
        h.tournamentTimer = 0


    ready = select.select([s], [], [], 1)
    #print(ready)
    if ready[0]:
        time_ = int(time.time())
        for line in str(s.recv(1024)).split('\\r\\n'):
            if "PING :tmi.twitch.tv" in line:
                print("PONG :tmi.twitch.tv")
                s.send(bytes("PONG :tmi.twitch.tv \r\n", "UTF-8"))
            if len(line) < 3:
                continue
            user = getUserMessage(line)
            print(time.strftime("%H:%M:%S"), user.username + ": " + user.message)


            if user.username == "nightbot" and "LP" in user.message:
                has = user.message.find("has")+4
                LP = user.message.find("LP")-1
                h.score = int(user.message[has:LP])
                h.timer = time_
                h.person = str(user.message[0:has-5]).lower()
                check_score(s, h.person, h.score)
                updatePlayer(h.person, h.score, -1)
                check_delta(s, h.person, h.score)
                check_tournament(s, h.score)

            user.message = user.message.lower()

            if "!stats" in user.message and h.messagesAllowed and h.spamAllowed:
                stats(s)
                h.spamAllowed = False
                h.spamTimer = time_

            if "!count" in user.message and h.messagesAllowed and h.spamAllowed:
                count(s)
                h.spamAllowed = False
                h.spamTimer = time_

            if "!botlommen" in user.message and h.spamAllowed:
                botlommen(s)
                h.spamAllowed = False
                h.spamTimer = time_

            if "!shutthefucky" in user.message and user.username in whitelist:
                sendMessage(s, "is shutting up but still recording scores")
                h.messagesAllowed = False

            if "!itsoktospam" in user.message and user.username in whitelist:
                sendMessage(s, "is allowed to talk")
                h.messagesAllowed = True

            if "!rs" in user.message and user.username in whitelist:
                reset_tournament(s)
                h.tournamentAllowed = True

            if "!mystats" in user.message and h.messagesAllowed and h.spamAllowed:
                player = call_xml_player(user.username)
                sendMessage(s, player.message)
                h.spamAllowed = False
                h.spamTimer = time_

            if "!info" in user.message and h.messagesAllowed and h.spamAllowed:
                info(s)
                h.spamAllowed = False
                h.spamTimer = time_

            if "!skill" in user.message and h.messagesAllowed and h.spamAllowed:
                delta(s,user.username,user.message)
                h.spamAllowed = False
                h.spamTimer = time_

            if "!news" in user.message and h.messagesAllowed and h.spamAllowed:
                news(s)
                h.spamAllowed = False
                h.spamTimer = time_

            if "!flirt" in user.message and h.messagesAllowed and h.spamAllowed:
                x = random.randint(1, len(listof) - 1)
                y = random.randint(1, len(listof2) -1)
                sendMessage(s, "{} thinks @spammiej has a {} penis".format(user.username, str(listof[x]).lower()))
                h.spamAllowed = False
                h.spamTimer = time_

            if "!tournament" in user.message and h.messagesAllowed and h.spamAllowed:
                [tree, root] = set_xml.tournament()
                for child in root.findall("data"):
                    if time_ > int(child.attrib["nextTournament"]):
                        h.tournamentAllowed = True
                    else:
                        h.tournamentAllowed = False
                if h.tournamentAllowed:
                    tournament(s, user.username)
                    h.spamAllowed = False
                    h.spamTimer = time_
                    h.tournamentTimer = time_
                if not h.tournamentAllowed:
                    x = int((int(child.attrib["nextTournament"]) - time_)/60)
                    sendMessage(s, "Tournament is locked for another {} minutes".format(str(x)))

            if "!t" in user.message and h.messagesAllowed and h.spamAllowed and h.tournamentAllowed:
                set_tournament(s,user.username,user.message)
                h.spamAllowed = False
                h.spamTimer = time_
                h.tournamentTimer = time_