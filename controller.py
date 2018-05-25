#from flask import flash, send_from_directory, render_template
import os,db 
import collections
import math


# Performs login
# params:
#   username
#   password
def login(username, password):
    return db.verifyLogin(username, password)
 
# params:
# - division: ak je FPO vraciam pre vysledky zenske vysledky vo vsetkych ostatnych pripadoch muzske (cize MPO), ak by niekto poslal nejaku hlupost, tak stale vraciam MPO
# - rows to display: udaje z pickera, treba validovat ci je to cislo ak ano tak tolko zaznamov vratim, na hodnotu 'all' dostavam ako paramater -1 cize na to special case
# returns:
# - 2 polia
# - table header: pole obsahujuce nazvy stlpcov, turnaje na ktore sa bude prelikovavat maju este dalsi rozmer pola a na dalsom indexe posielaju id daneho turnaja
# - table body: pole dict-ov prvy kluc je PDGA# daneho hraca, druhy kluc 'data' su jeho udaje
def getTotalResuls(division, rowsToDisplay = 200):    
    #select z db
    settings = db.select("settings")[0]

    if division.upper() == "FPO":
        d = "Open Women"
        gender = "W"
    else:
        d = "Open"
        gender = "M"
        
    tableBody = []
        
    print('(Controller) Division: ' + d)
    print('(Controller) Rows to display: ' + str(rowsToDisplay))
    tableHeader = [['Rank'],
                   ['Name'],
                   ['PDGA#'],
                   ['Elibility'],
                   ['Total'],
                   ['PDGA Rating Points','5256'],
                   ['Hot Rounds','235'],
                   ['Euro Pro Tour','1156'],
                   ['Konopiste Open', db.gettourId("Konopi")],
                   ['PDGA PRO Worlds',db.gettourId("2017 PDGA")],
                   ['European Open',db.gettourId("European Open")],
                   ['USDGC','9532']]
                   
    players = db.select("players","Where gender = '{}'".format(gender))
    tour1 = calculateScale(tableHeader[8][1], gender)
    tour2 = calculateScale(tableHeader[9][1], gender)
    tour3 = calculateScale(tableHeader[10][1], gender)
    
    proTours = settings[9].strip("'").split(",")
    proTour = [] 
    for proId in proTours:
        proTour.append(calculateScale(proId, gender))
        
    for p in players:
        prototal = 0
        tableBody.append([0,p[1]+" "+p[2],p[0],p[5],0,p[4],"hotrounds","protours",0,0,0])
        for z in tour1:
            if p[0] in z[0]:
                t1 = z[1]
                break
            t1 = 0
        for z in tour2:
            if p[0] in z[0]:
                t2 = z[1]
                break
            t2 = 0
        for z in tour3:
            if p[0] in z[0]:
                t3 = z[1]
                break
            t3 = 0
        
        for tour in proTour:
            for z in tour:
                if p[0] in z[0]:
                    prototal += z[1]
                    break
                
        total = t1 + t2 + t3 + prototal
        tableBody.append([0,p[1]+" "+p[2],p[0],p[5],total,p[4],"hotrounds",prototal,t1,t2,t3])
    
    tableBody.sort(key=lambda x: x[4], reverse=True)
    rank = 1
    for p in tableBody:
        tableBody[rank-1][0] = rank
        rank += 1
        
    if rowsToDisplay != "All":
        r = int(rowsToDisplay)
        return tableHeader, tableBody[:r]
    return tableHeader, tableBody

# params:
# - id: indetifikator konkretneho turnaja
# returns:
# - tournamentName: meno turnaja, ktore sa ziskalo na zaklade ID
# - tableHeader: pole obsahujuce nazvy stlpcov
# - tableBody: pole poli s jednotlivymi zaznamami
def getTournament(id,division):
    try:
        id += 0
    except TypeError:
        print('Incorrect format of id')
        return False
    # Select z db
    if(division.upper() == "MPO"):
        d = "OPEN"
        gender = "M"
    else:
        d = "OPEN WOMEN"
        gender = "W"
        
    table = db.getAllPlayers(id,d)
    tournamentName = table[0][0]
    tourscale = calculateScale(id,gender)
    
    tableBody = []
    
    for player in table[1]:
        for s in tourscale:
            if player[0] in s[0]:
                tableBody.append([0,player[1] + " " + player[2],s[1],player[3],player[4]])
                
    tableBody.sort(key=lambda x: x[2], reverse=True)
    
    rank = 1
    lastpoints = tableBody[0][2]
    n = 0
    for i in range(len(tableBody)):
        ## ak maju rovnaky pocet bodov maju delenu priecku
        if tableBody[i][2] != lastpoints:
            lastpoints = tableBody[i][2]
            rank += n
            n = 1
        else:
            n += 1
        tableBody[i][0] = rank
        
    print('(Controller) Tournament ID: ' + str(id))
    tableHeader = ['Rank',
                   'Name',
                   'Points',
                   'Elibility',
                   'Rating']
    
    return tournamentName, tableHeader, tableBody

#-----------------------------------------------------------------------------------------------------------------------
# calculating methodes for tournaments
#-----------------------------------------------------------------------------------------------------------------------
def calculateScale(tournamentId, gender):
    settings = db.select("settings")[0]
    ## Ids of tournaments
    tours = settings[8].strip("'")
    ## Ids of Protournaments
    proTours = settings[9].strip("'")
    ## sets the Scale for gender and type of tournamet
    if str(tournamentId) in tours:
        if gender == "M":
            Scale = settings[10]
            ScaleVal = settings[11]
        elif gender == "W":
            Scale = settings[12]
            ScaleVal = settings[13]
            
    elif str(tournamentId) in proTours:
        if gender == "M":
            Scale = settings[14]
            ScaleVal = settings[15]
        elif gender == "W":
            Scale = settings[16]
            ScaleVal = settings[17]
    else:
        print("Id not found")
        return
    
    if gender == "M":
        tab = db.select("players_tournaments","WHERE tournament_id = {} and division = 'Open'".format(tournamentId))
    elif gender == "W":
        tab = db.select("players_tournaments","WHERE tournament_id = {} and division = 'Open Women'".format(tournamentId))
    #p = []
    ret = []
    points = dict()
    #players = set()
    
    s = Scale.split("-")
    sv = ScaleVal.split("-")
    
    ## adds all players that played on Tournament into set
    for zaz in tab:
        total = db.select("rounds","WHERE player_tournament_id = {}".format(zaz[0]))[0][4]
        playerId = zaz[1]
        if total in points.keys():
            points[total].add(playerId)
        else:
            newSet = set([playerId])
            points.update({total : newSet})
            
    ## sorts dictionary in reverse order by keys
    points = collections.OrderedDict(sorted(points.items(), reverse=True))
    
    # position in lists
    sPos = 0
    svPos = 0
    retPos = 0
    if s[len(s)-1] == "//":
        endPos = int(s[len(s)-2])
    else:
        endPos = 1000
    
    ## add rating to each player
    for key in points:
        ids = set()
        rank = 0
        # number of players with same rank
        pNum = 0
        if sPos >= endPos:
            return ret
        for playerId in points[key]:
            if(svPos >= len(sv)-1):
                rank += int(sv[len(sv)-1])
            else:
                rank += int(sv[svPos])
            ids.add(playerId)
            pNum += 1
            sPos += 1
            svPos += 1
        ret.append((ids, math.ceil(rank/pNum)))
        retPos += 1
        
    return ret
        
    
#-----------------------------------------------------------------------------------------------------------------------
# Save/Load related methods:
#-----------------------------------------------------------------------------------------------------------------------

#Spracuje data, resp naplni databazu, defaultne sa csv subor uklada do /static foldra
def loadData():
    return
    folder_name = 'static'
    filename = 'database.csv'
    #return MyImport(folder_name,filename)

#ziska subor s db a vrati ho uzivatelovi
def exportData():
    return
    folder_name = 'static'
    filename = 'database.csv'
    #if myExport(folder_name,filename)==True:
        #if (os.path.isfile(folder_name+'/'+filename)):
           # return send_from_directory(folder_name, filename, as_attachment=True, attachment_filename=filename)
        #else:
           # flash('File not found!', 'danger')
           # return render_template('saveload.html')
   # else:
       # return False

# Zmaze udaje zo vsetkych tabuliek v databaze
# returns:
# - bool: ci prebehlo uspesne
def wipeDatabase():
    print('(Controller) Wipe DB')
    return db.wipe()

#-----------------------------------------------------------------------------------------------------------------------
# Settings related methods:
#-----------------------------------------------------------------------------------------------------------------------

# returns:
# dict - udaje je prednotlive polozky v settingoch, nazvy klucov musia zostat zachovane
def getSettings():
    return db.getSettings()

#TODO - kazda zo SET funckii potrebuje validaciu na spravny format (spravny format je v getSettings()), pri scale, treba porovnavat aj ci sa rovnaju pocty po splitnuti

# returns:
# - bool: ci prebehlo uspesne
def setUpdateData(day, time):
    err=False
    days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    if day not in days:
        print('Incorrect format of days.')
        return False
    try:
        hm=time.split(":")
        print(hm[0])
        print(hm[1])
    except IndexError:
        print('Incorrect format of time.')
        return False
    if len(hm)!=2:
        err=True
    try:
        hm[0]=int(hm[0])
        hm[1]=int(hm[1])
    except ValueError:
        print('Incorrect format of time.')
        return False
    if hm[0]<0 or hm[0]>23:
        err=True
    elif hm[1]<0 or hm[1]>59:
        err=True
        
    if err==True:
        print('Incorrect format of time.')
        return False
    print('(Controller) day: ' + day)
    print('(Controller) time: ' + time)
    #insert do db
    return db.updatedate(day+str(time))

# returns:
# - bool: ci prebehlo uspesne
def setHotRounds(division, score):
    try:
        int(score)
    except ValueError:
        print('Incorrect format of score.')
        return False
    if int(score)<0:
        print('Incorrect format of score.')
        return False
    print('(Controller) division: ' + division)
    print('(Controller) score: ' + score)
    #insert do db
    if division=="FPO" or division=="fpo":
        return db.update("hotrounds", ("woman", score))
    if division=="MPO" or division=="mpo":
        return db.update("hotrounds", ("man", score))
    else:
        print('Incorrect format of division.')
        return False

# returns:
# - bool: ci prebehlo uspesne
def setEligibilityPercentage(division, percentage):
    ####### TREBA PRE OBOJE DIVIZIE V DB #######
    try:
        int(percentage)
    except ValueError:
        print('Incorrect format of percentage.')
        return False
    if int(percentage)<0 or int(percentage)>100:
        print('Incorrect format of percentage.')
        return False
    print('(Controller) division: ' + division)
    print('(Controller) percentage: ' + percentage)
    #insert do db
    if division=="FPO" or division=="fpo":
        return db.update("eligibility", ("woman", percentage))
    if division=="MPO" or division=="mpo":
        return db.update("eligibility", ("man", percentage))
    else:
        print('Incorrect format of division.')
        return False

# returns:
# - bool: ci prebehlo uspesne
def setCurrentYear(year):
    try:
        int(year)
    except ValueError:
        print('Incorrect format of year.')
        return False
    if int(year)<0:
        print('Incorrect format of year.')
        return False
    
    print('(Controller) year: ' + year)
    #insert do db
    return db.update("year",(year))

# returns:
# - bool: ci prebehlo uspesne
def setPointsScale(division, scale, points):
    if len(scale.split("-"))!=len(points.split("-")):
        print('Incorrect format of scale or points.')
        return False
    p = points.split("-")
    s = scale.split("-")
    try:
        for i in range(len(p)):
            p[i]=int(p[i])
    except ValueError:
        print('Incorrect format of points.')
        return False
    try:
        for i in range(len(s)):
            s[i]=int(s[i])
    except ValueError:
        print('Incorrect format of scale.')
        return False
    
    print('(Controller) division: ' + division)
    print('(Controller) scale: ' + scale)
    print('(Controller) points: ' + points)
    #insert do db
    if division=="FPO" or division=="fpo":
        return db.update("scale", ("woman", scale, points))
    if division=="MPO" or division=="mpo":
        return db.update("scale", ("man", scale, points))
    else:
        print('Incorrect format of division.')
        return False

# returns:
# - bool: ci prebehlo uspesne
def setPointsScaleProTour(division, scale, points):
    if len(scale.split("-"))!=len(points.split("-")):
        print('Incorrect format of scale or points.')
        return False
    p=points.split("-")
    s=scale.split("-")
    try:
        for i in range(len(p)):
            p[i]=int(p[i])
    except ValueError:
        print('Incorrect format of points.')
        return False
    try:
        for i in range(len(s)):
            s[i]=int(s[i])
    except ValueError:
        print('Incorrect format of scale.')
        return False
    
    print('(Controller) division: ' + division)
    print('(Controller) scale: ' + scale)
    print('(Controller) points: ' + points)
    #insert do db
    if division=="FPO" or division=="fpo":
        return db.update("proscale", ("woman", scale, points))
    if division=="MPO" or division=="mpo":
        return db.update("proscale", ("man", scale, points))
    else:
        print('Incorrect format of division.')
        return False

def setTournamentsMPOFPO(tournaments):
    if str(type(tournaments)) == "<class 'str'>":
        if tournaments.find(", ") == -1:
            try:
                int(tournaments)
            except ValueError:
                print('Incorrect format of tournaments.')
                return False
        temp = tournaments.split(", ")
        for tournament in temp:
            try:
                int(tournament)
            except ValueError:
                print('Incorrect format of tournaments.')
                return False
        return db.update("ImportantTournaments", (tournaments))
    else:
        return False

def setTournamentsProTourMPOFPO(tournaments):
    if str(type(tournaments)) == "<class 'str'>":
        if tournaments.find(", ") == -1:
            try:
                int(tournaments)
            except ValueError:
                print('Incorrect format of tournaments.')
                return False
        temp = tournaments.split(", ")
        for tournament in temp:
            try:
                int(tournament)
            except ValueError:
                print('Incorrect format of tournaments.')
                return False
        return db.update("ProTournaments", (tournaments))
    else:
        return False
    
#print(getTotalResuls("MPO",200))     
#getTournament(31401,"MPO")
#getTotalResuls("MPO",1)
