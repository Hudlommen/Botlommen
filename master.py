import pandas as pd
import module as md
import time
import select
import random


HOST = "irc.twitch.tv"
PORT = 6667
PASS = ""
NICK = "botlommen"
CHANNEL = "#spammiej"

whitelist = ["hudlommen_", "spammiej"]

messagelist = []

tournament = md.tournament()
timer = md.timers()
delta = md.deltaholder()
df = md.loadDataFrame()
# 0 Name, 1 Count, 2 Highscore, 3 HighscoreDate, 4 HighscoreCount, 5 Lowscore, 6 LowscoreDate, 7 Lowscore
# 8 Count, 9 Deltascore, 10 DeltascoreDate , 11 DeltascoreCount

def sendMessage(s,message):
    messageTemp = "PRIVMSG " + CHANNEL + " :" + message
    data = messageTemp + "\r\n"
    s.send(data.encode())
    print("sent: " + messageTemp)

try:
    s = md.openSocket(HOST, PORT, PASS, NICK, CHANNEL)
    md.joinRoom(s)
    # sendMessage(s,"Joined the channel")
except:
    print("Failed to join channel")


while True:
    time_ = int(time.time())
    if len(messagelist) > 0 and time_ > timer.spam+1:
        if timer.chatallowed:
            sendMessage(s, messagelist[0])
        messagelist.pop(0)
        timer.spam = time_

    if time_ > timer.info+3600:
        messagelist.append("All: !news !tournament -> !t 0-100.000 - !skill [10-90k]- !mystats - !highscore - !lowscore - !deltascore !tourneywins - !info --- Whitelist: !set_dnf - !set_finalist - !set_cooldown !reset")
        timer.info = time_

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
            [username, message] = md.getUserMessage(line)
            print(time.strftime("%H:%M:%S"), username + ": " + message)

            if username == "nightbot" and "LP" in message:
                [score, playername] = md.split_lp(message)

                highlow_score_message = md.check_highlow(df,score,playername)
                if highlow_score_message != "":
                    messagelist.append(highlow_score_message)
                deltascore_ = -1
                if delta.deltanames:
                    return_message, deltascore_ = md.checkdelta(df,score, playername, delta.deltanames,delta.deltascores)
                    delta.deltascores = []
                    delta.deltanames = []
                    if return_message != "":
                        messagelist.append(return_message)
                df = md.updatePlayerData(df, score, playername, deltascore_)

                if len(tournament.names) == 4:
                    [tournament, tournament_message, winner_found, winner_name] = md.updateTournament(tournament,score)
                    if tournament_message != "":
                        messagelist.append(tournament_message)
                    if winner_found:
                        timer.tournament = time_
                        df.loc[(df.Name == winner_name), 'TournamentWins'] += 1
                        tournament = md.tournament()

                md.saveDataFrame(df)

            message = message.lower()
            if "!tournament" in message:
                tournament_cooldown_ = timer.tournament_cooldown * 60
                if time_ > timer.tournament+tournament_cooldown_:
                    try:
                        test = df.loc[df["Name"] == username].index[0]
                    except:
                        messagelist.append("You have to have called !skill succesfully, at least once, to enter the tournament {}.".format(username))
                        continue

                    if len(tournament.names) < 4 and username not in tournament.names:
                        tournament.names.append(username)
                        messagelist.append("You are now in the tournament {}".format(str(username)))
                        if len(tournament.names) == 4:
                            messagelist.append("Tournament started with the following players: {}, {}, {}, {} --- Finalist > {} | DNF > {} --- Use !t # to set a score. GLHF. If you have not called skill before, your tournament win will not be recorded.".format(str(tournament.names[0]),str(tournament.names[1]),str(tournament.names[2]),str(tournament.names[3]), str(tournament.finalist_score), str(tournament.DNF_score)))

                    else:
                        messagelist.append("Tournament is full {}".format(str(username)))
                else:
                    timeleft_ = int(int((timer.tournament+tournament_cooldown_) - time_)/60)
                    messagelist.append("Next tournament starts in {} minutes".format(timeleft_))

            call_accepted = False
            if "!t" in message and "!tournament" not in message and len(tournament.names) == 4:
                output_message = ""
                if username in tournament.names:
                    int_input_holder_ = ""
                    for i in range(0, len(message)):
                        if message[i].isdigit():
                            int_input_holder_ += message[i]
                    if int(int_input_holder_) < 100001 and int(int_input_holder_) > -1:
                        call_accepted = True
                        n = -1
                        for each in tournament.guess:
                            n += 1

                            if each > -1 and abs(int(int_input_holder_) - int(each)) < 2500:
                                call_accepted = False
                                if output_message == "":
                                    output_message += "Your score is too close to {}'s score of: {}".format(str(tournament.names[n]),str(each))
                                else:
                                    output_message += " and {}'s score of: {}".format(str(tournament.names[n]), str(each))

                    if call_accepted:
                        tournament.guess[tournament.names.index(username)] = int(int_input_holder_)
                        output_message = "Score of {} set by {}".format(str(int_input_holder_), str(username))

                    if output_message != "":
                        messagelist.append(output_message)

                    output_message = ""
                    if -1 not in tournament.guess:
                        output_message = "All scores set, call skill"

                    if output_message != "":
                        messagelist.append(output_message)

            if "!set_finalist" in message and username in whitelist:
                if len(tournament.names) < 4:
                    int_input_holder_ = ""
                    for i in range(0, len(message)):
                        if message[i].isdigit():
                            int_input_holder_ += message[i]
                    tournament.finalist_score = int(int_input_holder_)
                    if tournament.finalist_score > 120:
                        tournament.finalist_score = 120
                    messagelist.append("Finalist score set to {}".format(tournament.finalist_score))
                else:
                    messagelist.append("Tournament already started, finalist score cannot be changed")

            if "!set_dnf" in message and username in whitelist:
                if len(tournament.names) < 4:
                    int_input_holder_ = ""
                    for i in range(0, len(message)):
                        if message[i].isdigit():
                            int_input_holder_ += message[i]
                    tournament.DNF_score = int(int_input_holder_)
                    messagelist.append("DNF score set to {}".format(tournament.DNF_score))
                else:
                    messagelist.append("Tournament already started, DNF score cannot be changed")

            if "!set_cooldown" in message and username in whitelist:
                int_input_holder_ = ""
                for i in range(0, len(message)):
                    if message[i].isdigit():
                        int_input_holder_ += message[i]
                timer.tournament_cooldown = int(int_input_holder_)
                messagelist.append("Tournament cooldown set to {} minutes".format(timer.tournament_cooldown))

            if "!reset" in message and username in whitelist:
                tournament = md.tournament()
                timer.tournament = 0
                messagelist.append("Tournament reset")

            if "!mystats" in message:
                message = md.playerStats(df,username)
                if message != "":
                    messagelist.append(message)

            if "!highscore" in message:
                message = md.Highscore(df)
                if message != "":
                    messagelist.append(message)

            if "!lowscore" in message:
                message = md.Lowscore(df)
                if message != "":
                    messagelist.append(message)

            if "!deltascore" in message:
                message = md.Deltascore(df)
                if message != "":
                    messagelist.append(message)

            if "!tourneywins" in message:
                message = md.Tourneywins(df)
                if message != "":
                    messagelist.append(message)

            if "!skill" in message:
                x = message.find("[")
                y = message.find("]")
                if x > -1 and y > -1:
                    try:
                        z = int(message[x + 1:y])
                        if z > 9999 and z < 90001:
                            delta.deltanames.append(username)
                            delta.deltascores.append(z)
                        else:
                            messagelist.append("{} was not accpeted @{} - number has to be between 10k and 90k".format(
                                str(z), username))
                    except:
                        fail = str(message[x + 1:y])
                        messagelist.append("{} is not an accpeted input @{}".format(fail, username))

            if "!botlommen" in message:
                messagelist.append(
                    "All: !tournament -> !t 0-100.000 - !mystats - !skill [10-90k] - !highscore - !lowscore - !deltascore !tourneywins --- Whitelist: !set_dnf - !set_finalist - !set_cooldown !reset")


            if "!chatoff" in message and username in whitelist:
                sendMessage(s,"Chat disabled")
                timer.chatallowed = False

            if "!chaton" in message and username in whitelist:
                sendMessage(s,"Chat enabled")
                timer.chatallowed = True

            if "!info" in message:
                messagelist.append("Bot project by Hudlommen. Made to make the hunt for 100k LP more fun. github.com/Hudlommen/Botlommen")

            if "!news" in message:
                messagelist.append("Tournament reworked: Times show the distance to the winner 10k = 1s, wins now get saved, only subs can enter and whitelisted ppl can set the frame of the next tournament. Mystats reworked: more useful data presented, and overall ranking added shown as (#n). Other features added, try them.")
