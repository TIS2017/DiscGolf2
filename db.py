import dbconnect as db
from passlib.hash import sha256_crypt


def gettourId(tourname):
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "Select id From tournaments Where name LIKE '{}%'"
    results = []
    try:
        cursor.execute(sql.format(tourname))
        results = list(cursor.fetchall())
    except:
        print("Error: unable to fetch data")

    cursor.close()
    cnx.close()
    if len(results) == 0:
        print("There is no tournament by that name")
    return results[0][0]

def select(tab, wherecase = ""):
    
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "Select * from {} {}"
    
    results = []
    
    try:
        cursor.execute(sql.format(tab,wherecase))
        results = cursor.fetchall()
    except:
        print("Error: unable to fetch data")
    
    cursor.close()
    cnx.close()
    return results

def getAllPlayers(tourId, division):
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "Select players.id,first_name,last_name,eligibility,rating FROM players JOIN players_tournaments ON players_tournaments.player_id = players.id And tournament_id =  {} and division = '{}'"
    sql1 = "Select name FROM players_tournaments JOIN tournaments On players_tournaments.tournament_id = tournaments.id And tournament_id =  {} Limit 1"
    ret = []
    results = []
    try:
        cursor.execute(sql1.format(tourId))
        r = cursor.fetchall()[0]
        ret.append(r)
        cursor.execute(sql.format(tourId,division))
        results = list(cursor.fetchall())
    except:
        print("Error: unable to fetch data")
        raise
    
    cursor.close()
    cnx.close()
    ret.append(results)
    return ret

def countRounds(playerId,tourId):
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "Select Count(*) FROM rounds JOIN players_tournaments ON rounds.player_tournament_id=players_tournaments.id And player_id = {} And tournament_id =  {}"
    
    results = []
    
    try:
        cursor.execute(sql.format(playerId,tourId))
        results = cursor.fetchall()
    except:
        print("Error: unable to fetch data")
    
    cursor.close()
    cnx.close()
    return results[0][0]

# Returns values stored each possible setting --------------------------------------------------------------------------
def getSettings():
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "SELECT * FROM settings"
    data = {}

    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        if len(result) == 18: # means all settings were returned
            data = {
                'update_data_day': result[1],
                'update_data_time': result[2],
                'hot_rounds_MPO': result[3],
                'hot_rounds_FPO': result[4],
                'eligibility_MPO': result[5],
                'eligibility_FPO': result[6],
                'current_year': result[7],
                'tournaments_MPO_FPO': result[8],
                'tournaments_protour_MPO_FPO': result[9],
                'points_scale_MPO_scale': result[10],
                'points_scale_MPO_points': result[11],
                'points_scale_FPO_scale': result[12],
                'points_scale_FPO_points': result[13],
                'points_scale_protour_MPO_scale': result[14],
                'points_scale_protour_MPO_points': result[15],
                'points_scale_protour_FPO_scale': result[16],
                'points_scale_protour_FPO_points': result[17],
            }
    except:
        print("Error: Unable to fetch data!")
    cursor.close()
    cnx.close()
    return data


# Verify Login ---------------------------------------------------------------------------------------------------------
def verifyLogin(login, password_candidate):
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "SELECT * FROM accounts WHERE username='{}';"

    try:
        cursor.execute(sql.format(login))
        result = cursor.fetchone()
        if len(result) > 0:
            password = result[2]
            if sha256_crypt.verify(password_candidate, password):
                cursor.close()
                cnx.close()
                return True
            cursor.close()
            cnx.close()
            return False
        cursor.close()
        cnx.close()
        return False
    except:
        print("Error: Unable to fetch data!")
        raise

    cursor.close()
    cnx.close()
    return False
    
def insert(tab,*params):
    
    def __insertTournaments(id, name, year, official):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("INSERT INTO tournaments(id, name, year, official) VALUES ({}, \"{}\", {}, {})")
        
        try:
            cursor.execute(sql.format(id, name, year, official))
            cnx.commit()
            passed = True
        except:
            print(sql.format(id, name, year, official))
            cnx.rollback()
            raise

        cursor.close()
        cnx.close()
        return passed
        
    def __insertPlayers(first_name, last_name, gender, pid, rating, eligibility, european):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("INSERT INTO players(first_name, last_name, gender, id, rating, eligibility, european) VALUES (\"{}\", \"{}\", '{}', {}, {}, {}, {} )")
        
        try:
            cursor.execute(sql.format(first_name, last_name, gender, pid, rating, eligibility, european))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()
            print(sql.format(first_name, last_name, gender, pid, rating, eligibility, european))
            raise

        cursor.close()
        cnx.close()
        return passed

    def __insertHotrounds(player_id, round_points, round_rating, official):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("INSERT INTO hotrounds(player_id, round_points, round_rating, official, updateFlag) VALUES ({}, {}, {}, {}, '{}')")
        
        try:
            cursor.execute(sql.format(player_id, round_points, round_rating, official, "o"))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()
            print(sql.format(player_id, round_points, round_rating, official, ""))
            raise

        cursor.close()
        cnx.close()
        return passed
    
    def __insertPlayersTournaments(player_id, tournament_id, division, finished, place):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("INSERT INTO players_tournaments(player_id, tournament_id, division, finished, place)"
               "VALUES ({}, {}, '{}', {}, {})")
        
        try:
            cursor.execute(sql.format(player_id, tournament_id, division, finished, place))
            cnx.commit()
            passed = True
        except:
            print(sql.format(player_id, tournament_id, division, finished, place))
            cnx.rollback()
            raise

        cursor.close()
        cnx.close()
        return passed
    
    def __insertRounds(player_tournament_id, round_number, round_rating, round_points):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("INSERT INTO rounds(player_tournament_id, round_number, round_rating, round_points)"
               "VALUES ({}, {}, {}, {})")
        
        try:
            cursor.execute(sql.format(player_tournament_id, round_number, round_rating, round_points))
            cnx.commit()
            passed = True
        except:
            print(sql.format(player_tournament_id, round_number, round_rating, round_points))
            cnx.rollback()
            raise

        cursor.close()
        cnx.close()
        return passed
        
    if(tab == "tournaments"):
        ## miesto params sa posle instancia turnaj
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        return __insertTournaments(p1, p2, p3, p4)
        
        
    elif(tab == "players"):
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        p5 = params[0][4]
        p6 = params[0][5]
        p7 = params[0][6]
        return __insertPlayers(p1, p2, p3, p4, p5, p6, p7)
    
    elif(tab == "hotrounds"):
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        return __insertHotrounds(p1, p2, p3, p4)
    
    elif(tab == "players_tournaments"):
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        p5 = params[0][4]
        return __insertPlayersTournaments(p1, p2, p3, p4, p5)
    
    if(tab == "rounds"):
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        return __insertRounds(p1, p2, p3, p4)

def deleteAll(tab):
    passed = False
    
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "DELETE FROM {} WHERE updateFlag != 'Y';"

    try:
        cursor.execute(sql.format(tab))
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
    
    cursor.close()
    cnx.close()
    return passed
    
def delete(tab,param):
    passed = False
        
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "DELETE FROM {} WHERE {}"
    
    try:
        cursor.execute(sql.format(tab,param))
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
    
    cursor.close()
    cnx.close()
    return passed

def deleteAllPlayers():
    passed = False
    
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "DELETE FROM players"
    
    try:
        cursor.execute(sql)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
        raise
    
    cursor.close()
    cnx.close()
    return passed

def deleteAllHotrounds():
    passed = False
    
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "DELETE FROM hotrounds"
    
    try:
        cursor.execute(sql)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
        raise
    
    cursor.close()
    cnx.close()
    return passed


def deleteAllTournaments():
    passed = False

    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "DELETE FROM tournaments"

    try:
        cursor.execute(sql)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
        raise

    cursor.close()
    cnx.close()
    return passed

def deleteAllPlayersTournaments():
    passed = False

    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "DELETE FROM players_tournaments"
    try:
        cursor.execute(sql)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
        raise

    cursor.close()
    cursor = cnx.cursor()
    sql = "ALTER TABLE players_tournaments AUTO_INCREMENT = 1"

    try:
        cursor.execute(sql)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
        raise
    cnx.close()
    return passed

def deleteAllRounds():
    passed = False

    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "DELETE FROM rounds"

    try:
        cursor.execute(sql)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
        raise

    cursor.close()
    cursor = cnx.cursor()
    sql = "ALTER TABLE rounds AUTO_INCREMENT = 1"

    try:
        cursor.execute(sql)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
        raise

    cursor.close()
    cnx.close()
    return passed

def setdate():
    passed = False
    
    cnx = db.getconnect()
    cursor = cnx.cursor()    
    sql = "UPDATE settings SET last_updated = now();"
    try:
        cursor.execute(sql)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
    
    cursor.close()
    cnx.close()
    return passed
    
def getscore(roundnum, playerid, tournamentid):
    
    cnx = db.getconnect()
    cursor = cnx.cursor()
    results = []
    
    sql = "Select score FROM rounds INNER JOIN players_tournaments ON rounds.player_tournament_id=players_tounaments.id where roundNum = {} AND hraci_ID = {} AND turnaje_ID = {};"
    
    try:
        cursor.execute(sql.format(roundnum,playerid,tournamentid))
        results = cursor.fetchall()
    except:
        print("Error: unable to fetch data")
    
    cursor.close()
    cnx.close()
    return results

def getEuroPro(playerid):
    cnx = db.getconnect()
    cursor = cnx.cursor()
    results = []
    
    sql = "Select COUNT(DISTINCT turnaje_ID) FROM tournaments INNER JOIN players_tournaments ON players_tournaments.tournament_id = tournaments.id where EuroPro = 1 AND hraci_ID = {};"
        
    try:
        cursor.execute(sql.format(playerid))
        results = cursor.fetchall()
    except:
        print("Error: unable to fecth data")
    
    cursor.close()
    cnx.close()
    return results

def wipe():
    passed = False
    
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "DELETE FROM players_tournaments;"
    sql1 = "DELETE FROM players;"
    sql2 = "DELETE FROM tournaments;"
    sql3 = "DELETE FROM rounds;"
    
    cursor.execute(sql)
    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.execute(sql3)
        
    try:
        cursor.execute(sql)
        cursor.execute(sql1)
        cursor.execute(sql2)
        cursor.execute(sql3)
        cnx.commit()
        passed = True
    except:
        cnx.rollback()
    
    cursor.close()
    cnx.close()
    return passed
    
def prihlas(meno, heslo):
    cnx = db.getconnect()
    cursor = cnx.cursor()
    sql = "SELECT * FROM acounts WHERE Meno ='{}' And Heslo = '{}';"
    
    try:
        cursor.execute(sql.format(meno,heslo))
        results = cursor.fetchall()
        if(len(results) > 0):
            cursor.close()
            cnx.close()
            return True
    except:
        print("Error: unable to fetch data")
        
    cursor.close()
    cnx.close()    
    return False

def export(path):
    passed = False
    
    cnx = db.getconnect()
    cursor = cnx.cursor()
    
    # mysql 
    sql = "SELECT * INTO OUTFILE '{}/players.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' FROM players; "
    sql1 = "SELECT * INTO OUTFILE '{}/tournaments.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' FROM tournaments; "
    sql2 = "SELECT * INTO OUTFILE '{}/players_tounaments.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' FROM players_tounaments; "
    sql3 = "SELECT * INTO OUTFILE '{}/rounds.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' FROM rounds; "
    sql4 = "SELECT * INTO OUTFILE '{}/hotrounds.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' FROM hotrounds; "
    # postgre
    # sql = " COPY (SELECT * FROM players) TO '{}/players.csv WITH CSV HEADER"
    # sql1 = " COPY (SELECT * FROM tournaments) TO '{}/tournaments.csv WITH CSV HEADER"
    # sql2 = " COPY (SELECT * FROM players_tounaments) TO '{}/players_tounaments.csv WITH CSV HEADER"
    # sql3 = " COPY (SELECT * FROM rounds) TO '{}/rounds.csv WITH CSV HEADER"
    # sql4 = " COPY (SELECT * FROM hotrounds) TO '{}/hotrounds.csv WITH CSV HEADER"
    
    try:
        cursor.execute(sql.format(path))
        cursor.execute(sql1.format(path))
        cursor.execute(sql2.format(path))
        cursor.execute(sql3.format(path))
        cursor.execute(sql4.format(path))
        passed = True
    except:
        print("Error: unable to export data")
        
    cursor.close()
    cnx.close()
    return passed

def dbimport(path, tab):
    passed = False
    
    cnx = db.getconnect()
    cursor = cnx.cursor()
    
    sql1 = "Delete from {}"    
    #mysql
    sql = "LOAD DATA INFILE '{}' INTO TABLE {} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'"
    # postgre
    #sql = "COPY {} FROM '{}/{}.csv' WITH (FORMAT csv); "
    try:
        cursor.execute(sql1.format(tab))      
        cursor.execute(sql.format(tab,path,tab))
        cnx.commit()
        passed = True
    except:
        print("Error: unable to import data")
        
    cursor.close()
    cnx.close()
    return passed
    
def update(tab,*params):
    
    def __updateTournaments(id, name, year, official):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("INSERT INTO tournaments(id, name, year, official) VALUES ({}, '{}', {}, '{}')")
        sql1 = ("Delete from tournaments where id = '{}'")
        
        try:
            cursor.execute(sql1.format(id))
            cursor.execute(sql.format(id, name, year, official))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        return passed
        
    def __updatePlayers(first_name, last_name, gender, pid, rating, eligibility, european):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("INSERT INTO players(first_name, last_name, gender, pid, rating, eligibility, european) VALUES ('{}', '{}', '{}', {}, {}, {}, {})")
        sql1 = ("DELETE FROM players WHERE id = {}")
        
        try:
            cursor.execute("SELECT * FROM players WHERE id = {}".format(id))
            results = cursor.fetchall()
            if(results[0][5] < 0):
                print("UPDATE FLAG IS SET")
                return False
            cursor.execute(sql1.format(pid))
            cursor.execute(sql.format(first_name, last_name, gender, pid, rating, eligibility, european))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        return passed
    
    def __updaterounds(id, roundNum,score,updateFlag):        
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql1 =  "DELETE FROM rounds WHERE id = {};"
        sql = ("INSERT INTO rounds(id,roundNum,score,updateFlag)"
               "VALUES ({}, {}, {}, '{}')")
        
        try:
            cursor.execute(sql1.format(id))
            cursor.execute(sql.format(id, roundNum,score,updateFlag))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        return passed
     
    def __updatehraci_turnaj(hraci_ID,turnaje_ID,round_id,Division,Finished,Rating,Place):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("Update players_tounaments SET hraci_ID = {}, turnaje_ID = {}, round_ID = {}, Division = '{}', Finished = '{}', Rating = {}, Place = {}")
        
        try:
            cursor.execute(sql.format(hraci_ID,turnaje_ID,round_id,Division,Finished,Rating,Place))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()
        
        cursor.close()
        cnx.close()
        return passed
    
    def __updatehotrounds(sex, value):
        passed = False
        
        if sex == "man":
            sql = ("UPDATE settings SET hot_rounds_MPO = {}")
        elif sex == "woman":
            sql = ("UPDATE settings SET hot_rounds_FPO = {}")
        else:
            return False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()  
        
        try:
            cursor.execute(sql.format(value))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        return passed
        
    def __updateelegibility(sex, value):
        passed = False
        
        if(sex == "man"):
            sql = ("UPDATE settings SET eligibility_MPO = {}")
        elif(sex == "woman"):
            sql = ("UPDATE settings SET eligibility_FPO = {}")
        else:
            return False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()  
        
        try:
            cursor.execute(sql.format(value))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        
        return passed
    
    def __updatedate(value):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()  
        sql = ("Update settings SET update_date = '{}'")
        
        try:
            cursor.execute(sql.format(value))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        
        return passed
    
    def __updateyear(value):
        passed = False
        
        sql = ("Update settings SET current_year = {}")
        
        cnx = db.getconnect()
        cursor = cnx.cursor()  
        
        try:
            cursor.execute(sql.format(value))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        
        return passed
    
    def __updatepointscale(sex, scale, value):
        passed = False
        # print(" (DB) " + scale)
        # print(" (DB) " + points)
        if sex == "man":
            sql = ("UPDATE settings SET points_scale_MPO_scale = '{}'")
            sql1 = ("UPDATE settings SET points_scale_MPO_points = '{}'")
        elif sex == "woman":
            sql = ("UPDATE settings SET points_scale_FPO_scale = '{}'")
            sql1 = ("UPDATE settings SET points_scale_FPO_points = '{}'")
        else:
            return False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()  
        
        try:
            cursor.execute(sql.format(scale))
            cursor.execute(sql1.format(value))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        return passed
    
    def __updatepointscalepro(sex, scale, value):
        passed = False
        
        if sex == "man":
            sql = ("UPDATE settings SET points_scale_protour_MPO_scale = '{}'")
            sql1 = ("UPDATE settings SET points_scale_protour_MPO_points = '{}'")
        elif sex == "woman":
            sql = ("UPDATE settings SET points_scale_protour_FPO_scale = '{}'")
            sql1 = ("UPDATE settings SET points_scale_protour_FPO_points = '{}'")
        else:
            return False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()  
        
        try:
            cursor.execute(sql.format(scale))
            cursor.execute(sql1.format(value))
            cnx.commit()
            passed = True
        except:
            cnx.rollback()

        cursor.close()
        cnx.close()
        
        return passed
    
    def __updateImportantTournaments(text):        
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("UPDATE settings SET tournaments_MPO_FPO = '{}'")
        print(sql)
        print(sql.format(text))
        try:
            cursor.execute(sql.format(text))
            cnx.commit()
            passed = True
        except:
            print(sql.format(text))
            print("Error: unable to fetch data")
        
        cursor.close()
        cnx.close()
        return passed 
    
    def __updateProTournaments(text):
        passed = False
        
        cnx = db.getconnect()
        cursor = cnx.cursor()
        sql = ("UPDATE settings SET tournaments_protour_MPO_FPO = '{}'")
        
        try:
            cursor.execute(sql.format(text))
            cnx.commit()
            passed = True
        except:
            print(sql.format(text))
            print("Error: unable to fetch data")
        
        cursor.close()
        cnx.close()
        return passed

    if tab == "tournaments":
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        return __updateturnaje(p1, p2, p3, p4)

    elif tab == "players":
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        p5 = params[0][4]
        p6 = params[0][5]
        p7 = params[0][6]
        return __updatePlayers(p1, p2, p3, p4, p5, p6, p7)
    
    elif tab == "players_tournaments":
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        p5 = params[0][4]
        p6 = params[0][5]
        p7 = params[0][6]
        p8 = params[0][7]
        p9 = params[0][8]
        p10 = params[0][9]
        return __updatehraci_turnaj(p1,p2,p3,p4,p5,p6,p7,p8,p9,p10)
		
    elif tab == "rounds":
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        p4 = params[0][3]
        return __updaterounds(p1, p2, p3, p4)
	
    elif tab == "hotrounds":
        p1 = params[0][0]
        p2 = params[0][1]
        __updatehotrounds(p1, p2)
		
    elif tab == "eligibility":
        p1 = params[0][0]
        p2 = params[0][1]
        __updateelegibility(p1, p2)
	
    elif tab == "date":
        p1 = params[0][0]
        __updatedate(p1)
	
    elif tab == "year":
        p1 = params[0]
        __updateyear(p1)
		
    elif tab == "scale":
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        __updatepointscale(p1, p2, p3)
		
    elif tab == "proscale":
        p1 = params[0][0]
        p2 = params[0][1]
        p3 = params[0][2]
        __updatepointscalepro(p1,p2,p3)
    
    elif tab == "ImportantTournaments":
        p1 = params[0]
        return __updateImportantTournaments(p1)
    
    elif tab == "ProTournaments":
        p1 = params[0]
        return __updateProTournaments(p1)
