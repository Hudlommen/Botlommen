import pandas as pd
import module as md
import time
import select
import random


HOST = "irc.twitch.tv"
PORT = 6667
PASS = "oauth:1pdbazxf5lxb1yjfnus12pknqu8oab"
NICK = "botlommen"
CHANNEL = "#spammiej"

messagelist = []

tournament = md.tournament()
timer = md.timers()

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
    #sendMessage(s,"Joined the channel")
except:
    print("Failed to join channel")


while True:
    time_ = int(time.time())
    if len(messagelist) > 0 and time_ > timer.spam+1:
        sendMessage(s, messagelist[0])
        messagelist.pop(0)
        timer.spam = time_

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

                df = md.updatePlayerData(df, score, playername)

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
                #Todo: +3600
                tournament_cooldown_ = timer.tournament_cooldown * 60
                if time_ > timer.tournament+tournament_cooldown_:
                    if len(tournament.names) < 4:
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

            if "!set_finalist" in message:
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

            if "!set_dnf" in message:
                if len(tournament.names) < 4:
                    int_input_holder_ = ""
                    for i in range(0, len(message)):
                        if message[i].isdigit():
                            int_input_holder_ += message[i]
                    tournament.DNF_score = int(int_input_holder_)
                    messagelist.append("DNF score set to {}".format(tournament.DNF_score))
                else:
                    messagelist.append("Tournament already started, DNF score cannot be changed")

            if "!set_cooldown" in message:
                int_input_holder_ = ""
                for i in range(0, len(message)):
                    if message[i].isdigit():
                        int_input_holder_ += message[i]
                timer.tournament_cooldown = int(int_input_holder_)
                messagelist.append("Tournament cooldown set to {} minutes".format(timer.tournament_cooldown))

            if "!reset" in message:
                tournament = md.tournament()
                timer.tournament = 0
                messagelist.append("Tournament reset")

            if "!mystats" in message:
                message = md.playerStats(df,username)
                if message != "":
                    messagelist.append(message)



# filename = "test.txt"
# df = pd.read_csv(filename)
# print(df)
# # df.at["hud", "high"] = 5000
# # df.set_value("hud", "high", 5000)
# df.loc[df["name"] == "hud", ["high"]] = 5000
# print(df)
# exp = df.to_csv(filename, index=None)