import socket
import pandas as pd
import time

### interaction with twitch
def loadDataFrame():
    filename = "Data.txt"
    df = pd.read_csv(filename)
    return df


def saveDataFrame(df):
    filename = "Data.txt"
    exp = df.to_csv(filename, index=None)


def openSocket(host, port, PASS, nick, channel):
    s = socket.socket()
    s.connect((host, port))
    s.setblocking(0)
    s.settimeout(3)
    s.send(("PASS " + PASS + "\r\n").encode())
    s.send(("nick " + nick + "\r\n").encode())
    s.send(("JOIN " + channel + "\r\n").encode())
    return s


def joinRoom(s):
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


### local magic
class timers:
    def __init__(self):
        self.tournament = 0
        self.tournament_cooldown = 60
        self.spam = 0
        self.info = int(time.time())
        self.chatallowed = True

class deltaholder:
    def __init__(self):
        self.deltanames = []
        self.deltascores = []

def getUserMessage(line):
    username = ""
    message = ""
    try:
        sep = line.split(":", 2)
        username = sep[1].split("!", 1)[0]
        message = sep[2]
        return username, message
    except:
        return username, message


def split_lp(message):
    x = message.find("has")+4
    y = message.find("LP")-1
    score = int(message[x:y])
    username = str(message[0:x-5]).lower()
    return score, username


# Player data updating
def updatePlayerData(df,score,playername, deltascore):
    names_ = df["Name"] == playername
    found_ = False
    for each in names_:
        if each:
            found_ = True
    if found_:
        print("Player found")
        df.loc[(df.Name == playername), 'Count'] += 1
        df.loc[(df.Name == playername), 'TotalLP'] += score
        df.loc[(df.Name == playername) & (df.Highscore < score), 'Highscore'] = score
        df.loc[(df.Name == playername) & (df.Highscore == score), 'HighscoreCount'] = df.loc[(df.Name == playername), 'Count']
        df.loc[(df.Name == playername) & (df.Highscore == score), 'HighscoreDate'] = time.strftime("%d.%m.%y %H:%M")
        df.loc[(df.Name == playername) & (df.Lowscore > score), 'Lowscore'] = score
        df.loc[(df.Name == playername) & (df.Lowscore == score), 'LowscoreCount'] = df.loc[(df.Name == playername), 'Count']
        df.loc[(df.Name == playername) & (df.Lowscore == score), 'LowscoreDate'] = time.strftime("%d.%m.%y %H:%M")
        if deltascore > -1:
            df.loc[(df.Name == playername) & (df.Deltascore > deltascore), 'Deltascore'] = deltascore
            df.loc[(df.Name == playername) & (df.Deltascore == deltascore), 'DeltascoreCount'] = df.loc[(df.Name == playername), 'Count']
            df.loc[(df.Name == playername) & (df.Deltascore == deltascore), 'DeltascoreDate'] = time.strftime("%d.%m.%y %H:%M")
    else:
        print("Player NOT found")
        dato = time.strftime("%d.%m.%y %H:%M")
        df2 = pd.DataFrame({"Name": [playername], "Count": [1], "TotalLP": [score], "Highscore": [score], "HighscoreDate": [dato],
                            "HighscoreCount": [1], "Lowscore": [score], "LowscoreDate": [dato], "LowscoreCount": [1],
                            "Deltascore": [100000], "DeltascoreDate": [dato], "DeltascoreCount": [0], "TournamentWins": [0]})
        df = df.append(df2, ignore_index=True)
    return df


# High/Low score check
def check_highlow(df,score,playername):
    highscore = df.loc[df["Highscore"].idxmax()]
    lowscore = df.loc[df["Lowscore"].idxmin()]
    message = ""

    if int(score) > int(highscore["Highscore"]):
        message = "New HIGH score of {:,} set by {}".format(int(score),str(playername))

    if int(score) < int(lowscore["Lowscore"]):
        message = "New LOW score of {:,} set by {}".format(int(score), str(playername))

    return message


# Tournament
class tournament:
    def __init__(self):
        self.names = []
        self.guess = [-1, -1, -1, -1]
        self.score = [0, 0, 0, 0]
        # self.names =["Pixel", "Steinem", "Pead"]
        # self.guess = [23650, 46785, 78954, -1]
        # self.score = [25, 25, 25, 25]
        self.delta = [0,0,0,0]
        self.roundscore = [0,0,0,0]
        self.finalist_score = 30
        self.DNF_score = 30000


def updateTournament(tournament,NBscore):
    #Todo: Save tournament data - Wins (out of?) - avg delta (maybe WR?)
    message = ""
    winner = False
    winner_name = ""
    if -1 not in tournament.guess:

        for i,each in enumerate(tournament.guess):
            tournament.delta[i] = abs(each-NBscore)
        delta_sorted_ = []
        for each in tournament.delta:
            delta_sorted_.append(each)
        delta_sorted_.sort()

        reward_points = [10, 6, 4, 3]
        check_win_fin = [0,0,0,0]
        winner_delta_ = 0
        current_delta_ = 0
        for i, each in enumerate(delta_sorted_):
            finalist_score_ = tournament.finalist_score

            if i == 0:
                winner_delta_ = each
                current_delta_ = each
            if i != 0:
                current_delta_ = each - winner_delta_

            if current_delta_ < tournament.DNF_score:
                if tournament.score[tournament.delta.index(each)] > finalist_score_ and reward_points[i] == 10:
                    check_win_fin[tournament.delta.index(each)] = 2

                tournament.score[tournament.delta.index(each)] += reward_points[i]
                tournament.roundscore[tournament.delta.index(each)] = reward_points[i]
            else:
                tournament.roundscore[tournament.delta.index(each)] = "DNF"
            if tournament.score[tournament.delta.index(each)] > finalist_score_ and reward_points[i] == 10 \
                    and check_win_fin[tournament.delta.index(each)] != 2:
                check_win_fin[tournament.delta.index(each)] = 1
            if tournament.score[tournament.delta.index(each)] > finalist_score_ and reward_points[i] != 10:
                check_win_fin[tournament.delta.index(each)] = 1
        if 2 in check_win_fin:
            winner = True
            winner_name = tournament.names[check_win_fin.index(2)]
        else:
            winner = False

        score_scorted_ = []
        for each in tournament.score:
            score_scorted_.append(each)
        score_scorted_.sort(reverse=True)

        names_ = []
        for each in tournament.names:
            names_.append(each)

        score_ = []
        for each in tournament.score:
            score_.append(each)

        points_ = []
        for each in tournament.roundscore:
            points_.append(each)

        for i, each in enumerate(tournament.delta):
            tournament.delta[i] = tournament.delta[i] - delta_sorted_[0]

        for each in score_scorted_:
            playername_ = names_[score_.index(each)]

            if check_win_fin[score_.index(each)] == 2:
                playerscore_ = "WINNER"
                playername_ = playername_.upper()
            elif check_win_fin[score_.index(each)] == 1:
                playerscore_ = "Finalist"
            else:
                playerscore_ = score_[score_.index(each)]
            playerpoints_ = points_[score_.index(each)]
            if tournament.delta[score_.index(each)] > 0:
                holder_ = tournament.delta[score_.index(each)] / 10000
                holder_ = "{:1.2f}".format(holder_)
                delta_time = "0:0{}:{}".format(holder_[0], holder_[2:4])
                if playerpoints_ == "DNF":
                    message += "- {}: {} ({}) +{} -".format(playername_, playerscore_, playerpoints_, delta_time)
                else:
                    message += "- {}: {} (+{}) +{} -".format(playername_, playerscore_, playerpoints_, delta_time)
            else:
                message += "- {}: {} (+{}) -".format(playername_, playerscore_, playerpoints_)
            names_.pop(score_.index(each))
            points_.pop(score_.index(each))
            tournament.delta.pop(score_.index(each))
            check_win_fin.pop(score_.index(each))
            score_.pop(score_.index(each))
    print(message)
    # tournament.guess = [23650, 46785, 78954, -1]
    tournament.guess = [-1,-1,-1,-1]
    tournament.delta = [0, 0, 0, 0]
    tournament.roundscore = [0, 0, 0, 0]

    return tournament, message, winner, winner_name


def playerStats(df,playername):
    try:
        Highscore_rank_ = df.sort_values("Highscore", ascending=False)
        Highscore_rank_ = Highscore_rank_.reset_index(drop=True)
        Highscore_rank_ = Highscore_rank_[Highscore_rank_['Name'] == playername].index[0] +1
        
        Lowscore_rank_ = df.sort_values("Lowscore", ascending=True)
        Lowscore_rank_ = Lowscore_rank_.reset_index(drop=True)
        Lowscore_rank_ = Lowscore_rank_[Lowscore_rank_['Name'] == playername].index[0] +1

        Deltascore_rank_ = df.sort_values("Deltascore", ascending=True)
        Deltascore_rank_ = Deltascore_rank_.reset_index(drop=True)
        Deltascore_rank_ = Deltascore_rank_[Deltascore_rank_['Name'] == playername].index[0] +1

        Tournament_rank_ = df.sort_values("TournamentWins", ascending=False)
        Tournament_rank_ = Tournament_rank_.reset_index(drop=True)
        Tournament_rank_ = Tournament_rank_[Tournament_rank_['Name'] == playername].index[0] +1
        Data = df.loc[df["Name"] == playername]

        index_ = Data["Name"].index[0]
        Name_ = str(Data["Name"][index_])
        Highscore_  = int(Data["Highscore"][index_])
        Lowscore_ = int(Data["Lowscore"][index_])
        Delta_ = str(Data["Deltascore"][index_])
        Tournament_ = str(Data["TournamentWins"][index_])

        if int(Delta_) == 100000:
            message = "@{} High score: {:,} (#{}), Low score: {:,} (#{}), Tournament wins: {} (#{}).".format(
            str(Name_), int(Highscore_), str(Highscore_rank_), int(Lowscore_),
            str(Lowscore_rank_),
            str(Tournament_), str(Tournament_rank_))
        else:
            message = "@{} High score: {:,} (#{}), Low score: {:,} (#{}), Delta: {} (#{}), Tournament wins: {} (#{}).".format(
            str(Name_), int(Highscore_), str(Highscore_rank_), int(Lowscore_),
            str(Lowscore_rank_), str(Delta_), str(Deltascore_rank_),
            str(Tournament_), str(Tournament_rank_))
    except:
        message = "You need to call !skill once to have a record @{}".format(str(playername))

    return message

def Highscore(df):
    Highscore_rank_ = df.sort_values("Highscore", ascending=False)
    Highscore_rank_ = Highscore_rank_.reset_index(drop=True)
    Highscore_rank_ = Highscore_rank_.head()

    names = []
    for each in Highscore_rank_.Name:
        names.append(each)

    scores = []
    for each in Highscore_rank_.Highscore:
        scores.append(each)

    message = ""
    for i, each in enumerate(names):
        message += "- #{} {}: {:,} -".format(i + 1, names[i], scores[i])
    return message


def Lowscore(df):
    Lowscore_rank_ = df.sort_values("Lowscore", ascending=True)
    Lowscore_rank_ = Lowscore_rank_.reset_index(drop=True)
    Lowscore_rank_ = Lowscore_rank_.head()

    names = []
    for each in Lowscore_rank_.Name:
        names.append(each)

    scores = []
    for each in Lowscore_rank_.Lowscore:
        scores.append(each)

    message = ""
    for i, each in enumerate(names):
        message += "- #{} {}: {:,} -".format(i + 1, names[i], scores[i])
    return message


def Deltascore(df):
    Deltascore_rank_ = df.sort_values("Deltascore", ascending=True)
    Deltascore_rank_ = Deltascore_rank_.reset_index(drop=True)
    Deltascore_rank_ = Deltascore_rank_.head()

    names = []
    for each in Deltascore_rank_.Name:
        names.append(each)

    scores = []
    for each in Deltascore_rank_.Deltascore:
        scores.append(each)

    message = ""
    for i, each in enumerate(names):
        message += "- #{} {}: {:,} -".format(i + 1, names[i], scores[i])
    return message


def Tourneywins(df):
    tourney_rank_ = df.sort_values("TournamentWins", ascending=False)
    tourney_rank_ = tourney_rank_.reset_index(drop=True)
    tourney_rank_ = tourney_rank_.head()

    names = []
    for each in tourney_rank_.Name:
        names.append(each)

    scores = []
    for each in tourney_rank_.TournamentWins:
        scores.append(each)

    message = ""
    for i, each in enumerate(names):
        message += "- #{} {}: {:,} -".format(i + 1, names[i], scores[i])
    return message


def checkdelta(df,score,username, deltanames, deltasguess):
    message = ""
    if username in deltanames:
        deltascore = abs(int(deltasguess[deltanames.index(username)]) - int(score))
        message = "Deltascore: {:,}".format(deltascore)

    return message, deltascore