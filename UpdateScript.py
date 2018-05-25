import PlayerManager as PlayerManager
import TournamentManager as TournamentManager
import PlayerEligibilityParser as PlayerEligibilityParser
import time
import db as DatabaseManager

settings = DatabaseManager.getSettings()
# print(settings)

minPercentageFPO = settings["eligibility_FPO"]
minPercentageMPO = settings["eligibility_MPO"]
minHotroundBoundaryMPO = settings["hot_rounds_MPO"]
minHotroundBoundaryFPO = settings["hot_rounds_FPO"]
currentYear = settings["current_year"]
tournaments_to_parse = settings["tournaments_MPO_FPO"].split(", ") + settings["tournaments_protour_MPO_FPO"].split(", ")
# print(minPercentageMPO)
# print(minPercentageFPO)
# print(currentYear)
# print(tournaments_to_parse)

t = time.time()
IDArray = list()

##### GATHER PLAYERS

print("Gathering player info...")
all_players = PlayerManager.getAllPlayers()
print(time.time() - t, end=" seconds : ")
print("all players (" + str(len(all_players)) + ") gathered")
print()

playerIDGenderArray = dict((p.getID(), p.getGender()) for p in all_players)

##### GATHER HOTROUNDS

# all_hotrounds = []
# print("Gathering hot rounds info...")
# for i in range(1, 13):
#     # print("\t\t\t\t\t\t\t\t\t\t" + str(i))
#     month_hotrounds, IDArrayMonth = TournamentManager.getAllHotrounds(playerIDGenderArray, i, currentYear, IDArray, minHotroundBoundaryMPO, minHotroundBoundaryFPO)
#     IDArray += IDArrayMonth
#     all_hotrounds += month_hotrounds
#     print("\t" + str(i) + ". month successful (" + str(time.time() - t) + " seconds - " + str(len(month_hotrounds)) + " hotrounds)")
# print(str(time.time() - t), end=" seconds : ")
# print("all hot rounds (" + str(len(all_hotrounds)) + ") gathered")
# print()

##### GATHER ELIGIBILITY

# i = 0
# print("Updating eligibility info...")
# for player in all_players:
#     if i % 100 == 0:
#         print("\t" + str(i) + " players updated so far (" + str(time.time() - t) + " seconds)")
#     player.eligibility = PlayerEligibilityParser.calculateEligibility(player.getID(), minPercentageFPO if player.getGender() == "F" else minPercentageMPO)
#     i += 1
# print(str(time.time() - t), end=" seconds : ")
# print("all players updated")
# print()

##### GATHER TOURNAMENTS

all_tournaments = list()
for id in tournaments_to_parse:
    tournament = TournamentManager.getTournament(id)
    if tournament is not None:
        all_tournaments += [tournament]
        print(tournament.getName())
    results = tournament.getResults()
    non_european_players = []
    playerIDArray = list(p.getID() for p in all_players)
    print("\tnumber of players: " + str(len(all_players)))
    for division_name, division_results in results.items():
        for pid in division_results.keys():
            if str(pid) not in playerIDArray:
                non_european_players.append(pid)
    print("\tnumber of players to add: " + str(len(non_european_players)))
    all_players += PlayerManager.getPlayersByIDArray(non_european_players)
    print("\tnumber of player after addition: " + str(len(all_players)))
print(str(time.time() - t), end=" seconds : ")
print("all tournaments gathered")
print()


################################################################################################################## DATABASE SAVE ##################################################################################################

##### SAVE PLAYERS

print("Deleting old players from database...")
print(DatabaseManager.deleteAllPlayers())
print("Inserting new players...")
i = 0
for player in all_players:
    if i % 1000 == 0:
        print("\t" + str(i) + " players inserted so far (" + str(time.time() - t) + " seconds)")
    player.insert()
    i += 1

print(time.time() - t, end=" seconds : ")
print("all players (" + str(len(all_players)) + ") inserted")
print()

##### SAVE HOTROUNDS

# print("Deleting old hotrounds from database...")
# print(DatabaseManager.deleteAllHotrounds())
# print("Inserting new hotrounds...")
# i = 0
# for hotround in all_hotrounds:
#     hotround.insertAsHotround()
#     i += 1
#
# print(time.time() - t, end=" seconds : ")
# print("all hotrounds (" + str(len(all_hotrounds)) + ") inserted")
# print()

##### SAVE TOURNAMENTS

print("Deleting old tournaments from database...")
print(DatabaseManager.deleteAllTournaments())
print(DatabaseManager.deleteAllPlayersTournaments())
print(DatabaseManager.deleteAllRounds())
print("Inserting new tournaments...")
for tournament in all_tournaments:
    print("tournament: " + tournament.getName() + " - was just inserted (" + str(time.time() - t) + " seconds)")
    tournament.insert()

print(time.time() - t, end=" seconds : ")
print("all tournaments (" + str(len(all_tournaments)) + ") inserted")
print()