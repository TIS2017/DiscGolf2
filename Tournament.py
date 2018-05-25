import db as DatabaseManager

class Tournament:

    def __init__(self, par_id, par_name, par_date, par_results, par_official):
        self.__id = par_id
        self.__name = par_name
        self.__date = par_date
        self.__results = par_results
        self.__official = par_official

    def __repr__(self):
        result = ""
        for k, v in self.__results.items():
            result += (k + "\n")
            for kk, vv in v.items():
                result += ("\t" + kk + " : ")
                result += str(vv)
                result += "\n"
        return result

    def getID(self):
        return self.__id

    def getName(self):
        return self.__name

    def getYear(self):
        return self.__date.split("-")[-1]

    def getDate(self):
        return self.__date

    def getResults(self):
        return self.__results

    def getOfficial(self):
        return self.__official

    def insert(self):
        DatabaseManager.insert("tournaments", (self.getID(), self.getName(), self.getYear(), self.getOfficial()))
        for division, division_results in self.__results.items():
            for pid, player_results in division_results.items():
                DatabaseManager.insert("players_tournaments", (pid, self.getID(), division, player_results["finished"], player_results["place"]))
                player_tournament_id =  DatabaseManager.select("players_tournaments", "WHERE player_id = {} AND tournament_id = {}".format(pid, self.getID()))
                print(player_tournament_id)
                print(player_tournament_id[0][0])
                player_tournament_id = player_tournament_id[0][0]
                rounds = player_results["rounds"]
                for round_number, round_results in rounds.items():
                    try:
                        DatabaseManager.insert("rounds", (player_tournament_id, int(round_number), int(round_results["rating"]), int(round_results["points"])))
                    except TypeError:
                        print(player_results)
        # DatabaseManager.update("players_tournaments", )

    def insertAsHotround(self):
        for k, v in self.__results.items():
            for k1, v1 in v.items():
                DatabaseManager.insert("hotrounds", (int(k), int(v1["points"]), int(v1["rating"]), self.__official))
    #
    # def delete(self):
    #     DatabaseManager.delete("tournaments", "id = " + self.__id)
