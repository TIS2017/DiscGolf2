from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
from Tournament import Tournament
import time
import copy

# import api2

countries = ["Austria", "Belgium", "Croatia", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany",
             "Hungary", "Iceland", "Italy", "Latvia", "Lithuania", "Netherlands", "Norway", "Poland", "Russia",
             "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "United Kingdom"]


# fetches all hotrounds

# playerArray = dict()
def getAllHotrounds(playerArray, month, year, IDArrayParam, minBoundaryMPO, minBoundaryFPO):
    # print(playerArray)
    # print(len(playerArray))

    t = time.time()
    # all months

    resultList = list()
    IDArray = IDArrayParam[:]
    # for i in range(1, 13):
    url = "https://www.pdga.com/tour/events/" + str(year) + "/" + str(month)
    soup = BeautifulSoup(urlopen(url), "lxml")
    html = soup.find_all("tbody")
    # all the weeks are wrapped in <tbody>
    for tbody in html:
        # -> <tr>
        for row in tbody.children:
            # check whether the child is a <tr> tag (if this row represents a tournament), not a whitespace
            if str(type(row)) == "<class 'bs4.element.Tag'>":
                cont = True
                tour_id = ""
                country = ""
                name = ""
                official = False;
                # -> <td>
                for column in row.children:
                    # tournament id - later used in url
                    # check whether the child is a <td> tag, not a whitespace
                    if str(type(column)) == "<class 'bs4.element.Tag'>":
                        if "views-field-OfficialName" in column.attrs["class"]:
                            name = column.a.string
                            tour_id = column.a.attrs["href"].split("/")[-1]
                        # check whether the results are present and official
                        if "views-field-StatusIcons" in column.attrs["class"]:
                            if column.contents == ['\n']:
                                cont = False
                            elif column.a.img.attrs["title"] == "Official Tournament Results":
                                official = True

                                # check whether the tournament took place in Europe
                                # if cont is True:
                                #     if "views-field-Location" in column.attrs["class"]:
                                #         # gets the country from the tag
                                #         country = column.contents[0].strip().split(", ")[-1]
                                #         if country not in countries:
                                #             cont = False
                                # if cont is True:
                                #     if "views-field-Tier" in column.attrs["class"]:
                                #         print(column.contents)
                if cont:
                    # print(name + " : " + country)

                    if tour_id not in IDArray:
                        if official:
                            tournament = getHotroundsFromOfficialTournamentByID(tour_id, playerArray, minBoundaryMPO,
                                                                                minBoundaryFPO)
                        else:
                            tournament = getHotroundsFromUnofficialTournamentByID(tour_id, playerArray, minBoundaryMPO,
                                                                                  minBoundaryFPO)
                        if tournament is not None:
                            # print("tournament:")
                            # print(tournament.getResults())
                            # print(tournament.getYear())
                            resultList.append(tournament)
                        # else:
                        #     # print(str(tour_id) + " tournament is NONE")
                        IDArray.append(tour_id)
    # print(str(time.time() - t) + " seconds")
    # print(url)
    # print(len(resultList))
    return resultList, IDArray


def getHotroundsFromOfficialTournamentByID(id, playerArray, minBoundaryMPO, minBoundaryFPO):
    try:
        dic = dict()
        dic["id"] = id
        URL = "https://www.pdga.com/tour/event/" + id
        # print("\t" + URL)
        soup = BeautifulSoup(urlopen(URL), "lxml")

        # check if round ratings are present
        html = soup.find_all("div", "tour-show-round-ratings-link")
        if (len(html)) == 0:
            # print("no hide/show")
            return None

        # get the name of tournament
        html = soup.find_all("title")[0]
        # print(html.contents[0].split(" | ")[0])
        dic["name"] = html.contents[0].split(" | ")[0]

        # get some general info about tournament
        html = soup.find_all("ul", "event-info info-list")[0]
        for con in html.contents:
            if con.a is None:
                dic[con.strong.string] = con.contents[-1][2:]
            else:
                dic[con.strong.string] = con.a.string

        # get more info about tournament
        html = soup.find_all("table", "summary sticky-enabled")[0]
        for con in html.contents:
            pom = []
            if str(con) != '\n':
                if con == html.tbody:
                    for con2 in html.tbody.tr:
                        if con2 != " ":
                            dic[list(con2.attrs.values())[0][0].capitalize()] = con2.string

        # parsing results
        results = dict()
        headers = soup.find_all("h3", "division")
        html = soup.findAll("table", "results sticky-enabled")
        division_index = 0
        # right now the ResultSet of all the tables is with class above is in the variable @html
        for tab in html:
            # one <table> tag represents one division
            # <table> is splitted into <thead> and <tbody>
            # in the <thead> tag, the parameter "total" should be stored
            continue_with_division = False

            # search for "total" parameter
            thead = tab.thead

            for th in thead.tr:
                if str(type(th)) == "<class 'bs4.element.Tag'>":
                    if th.attrs['class'][0] == "total":
                        continue_with_division = True

            # if total parameter is present, continue to parse given division
            division = ""
            for content in headers[division_index].contents:
                if (str(type(content))) == "<class 'bs4.element.NavigableString'>" and str(content).strip() != "":
                    division = content.strip()
            if continue_with_division and division in ["Open", "Open Women"]:
                body = tab.tbody

                # row represents one <tr> tag inside of <tbody> tag and thus tournament results for one person
                for row in body:
                    if str(type(row)) == "<class 'bs4.element.Tag'>":
                        player = dict()

                        # obtain person id - pdga#
                        # pid = row.td.next_sibling.next_sibling.next_sibling.string
                        pid = None
                        pdga = None
                        for cell in row:
                            if str(type(cell)) == "<class 'bs4.element.Tag'>":
                                if len(cell.attrs["class"]) == 1 and cell.attrs["class"][0] == "pdga-number":
                                    pdga = cell.string

                        pid = pdga
                        # since the round number is not given on the webpage, it must be counted in the program
                        round_number = 1

                        # some players are not registered PDGA players and thus don't have any PDGA#
                        if pid is not None:
                            pid = str(pid)
                            add = True
                            # parsing each column in row
                            for cell in row:
                                if str(type(cell)) == "<class 'bs4.element.Tag'>":

                                    # all the columns we need have just one class
                                    if len(cell.attrs["class"]) == 1:
                                        cell_class = cell.attrs["class"][0]
                                        # if cell_class == "place":
                                        #     player["place"] = cell.string
                                        if cell_class == "round":
                                            # print(cell.string)
                                            player["round " + str(round_number)] = dict()
                                            player["round " + str(round_number)]["points"] = cell.string
                                        if cell_class == "round-rating":
                                            try:
                                                gender = playerArray[pid]
                                            except KeyError:
                                                # print("player not found in array - deleting round")
                                                add = False
                                                del player["round " + str(round_number)]
                                                break
                                            if cell is None or cell.string is None:
                                                # print("no rating present - deleting round")
                                                del player["round " + str(round_number)]
                                            else:
                                                if cell.string.strip() != "" and (
                                                    (gender == "M" and int(cell.string.strip()) >= minBoundaryMPO) or (
                                                        gender == "F" and int(cell.string.strip()) >= minBoundaryFPO)):
                                                    player["round " + str(round_number)]["rating"] = cell.string
                                                    # print(division)
                                                else:
                                                    # print("player did not reach minimal rating - deleting round")
                                                    del player["round " + str(round_number)]
                                            round_number += 1
                            # print(player)
                            if len(player.items()) >= 1 and add:
                                results[pid] = player.copy()
            division_index += 1
        # if len(results) == 0:
        #     # print("nikto")
        #     pass
        # else:
        #     # print(results)
        if len(results) > 0:
            return Tournament(dic["id"], dic["name"], dic["Date"], results, True)
        else:
            return None
    except AttributeError:
        print("found the experimental event with teams")
        raise


def getHotroundsFromUnofficialTournamentByID(id, playerArray, minBoundaryMPO, minBoundaryFPO):
    try:
        # playerArray = dict((p.getID(), p.getGender()) for p in pArray)
        dic = dict()
        dic["id"] = id
        URL = "https://www.pdga.com/tour/event/" + id
        # print("\t\t" + URL)
        soup = BeautifulSoup(urlopen(URL), "lxml")

        # check if round ratings are present
        html = soup.find_all("div", "tour-show-round-ratings-link")
        if (len(html)) == 0:
            # print("no hide/show")
            return None

        # get the name of tournament
        html = soup.find_all("title")[0]
        # print(html.contents[0].split(" | ")[0])
        dic["name"] = html.contents[0].split(" | ")[0]

        # get some general info about tournament
        html = soup.find_all("ul", "event-info info-list")[0]
        for con in html.contents:
            if con.a == None:
                dic[con.strong.string] = con.contents[-1][2:]
            else:
                dic[con.strong.string] = con.a.string

        # get more info about tournament
        html = soup.find_all("table", "summary sticky-enabled")[0]
        for con in html.contents:
            pom = []
            if str(con) != '\n':
                if con == html.tbody:
                    for con2 in html.tbody.tr:
                        if con2 != " ":
                            dic[list(con2.attrs.values())[0][0].capitalize()] = con2.string

        # parsing results
        results = dict()
        html = soup.findAll("table", "results sticky-enabled")
        # right now the ResultSet of all the tables is with class above is in the variable @html
        holes = soup.find_all("div", "tooltip-templates")
        headers = soup.find_all("h3", "division")
        # print(headers)
        # print(holes[])
        hole_index = 0
        # number_of_rounds = 1
        first_round_id = holes[0].span.attrs["id"].split("-")[-1]
        # print(first_round_id)
        # for hole in holes[1:]:
        #     if hole.span.attrs["id"].split("-")[-1] == first_round_id:
        #         break
        #     number_of_rounds += 1
        temp = soup.find_all("tr")[2]
        # number_of_rounds = 0
        all_rounds = {}
        i = 0
        for th in temp:
            # print(th)
            if str(type(th)) == "<class 'bs4.element.Tag'>":
                if "round" in th.attrs["class"]:
                    all_rounds["Rd" + str(i)] = i
                    i += 1
                elif "semi-finals" in th.attrs["class"]:
                    all_rounds["Semis"] = i
                    i += 1
                elif "finals" in th.attrs["class"]:
                    all_rounds["Finals"] = i
                    # print("\t\t\t", end="")
                    # number_of_rounds += 1
                    # print(th)
                    i += 1
        division_index = 0
        # for
        number_of_rounds = len(all_rounds)
        # print(number_of_rounds)
        # print(num)
        for tab in html:
            skip_rounds = []
            # print(headers[hole_index])
            # print(headers[hole_index].next_sibling)
            # print("zaznamov s jamkami: " + str(len(holes)))
            # print(holes[hole_index].contents)
            node = headers[hole_index].next_sibling
            # all_rounds_temp = all_rounds[:]
            final_metadata = False
            semis_metadata = False
            while True:
                if str(type(node)) == "<class 'bs4.element.Tag'>":
                    if "tooltip-templates" not in node.attrs["class"]:
                        break
                    # print(node)
                    if node.span.attrs["id"].split("-")[-1] == "Finals":
                        final_metadata = True
                    if node.span.attrs["id"].split("-")[-1] == "Semis":
                        semis_metadata = True
                    for child in node.span.contents:
                        if str(type(child)) == "<class 'bs4.element.NavigableString'>" and str(child) != '\n':
                            if int(child.string.split("; ")[1].split(" ")[0]) < 13:
                                number_to_skip = all_rounds[child.parent.attrs["id"].split("-")[-1]]
                                # print("round to skip: " + str(number_to_skip))
                                skip_rounds.append(number_to_skip)
                                # print(node.span.attrs["id"])
                                # print(node.span.string.split("; ")[1].split(" ")[0])
                node = node.next_sibling
            if final_metadata is False and "Finals" in all_rounds.keys():
                skip_rounds.append(all_rounds["Finals"])
            if semis_metadata is False and "Semis" in all_rounds.keys():
                skip_rounds.append(all_rounds["Semis"])
                # print("all rounds: ", end="")
                # print(all_rounds)
                # print("rounds to skip: ", end="")
                # print(skip_rounds)
                # for i in range(hole_index * number_of_rounds, hole_index * number_of_rounds + number_of_rounds):
                #     # print(holes[i].span)
                #     # print(holes[i].span.contents)
                #     print("zaznam " + str(i))
                #     for child in holes[i].span.contents:
                #         if str(type(child)) == "<class 'bs4.element.NavigableString'>" and str(child) != '\n':
                #             if int(child.split("; ")[1].split(" ")[0]) < 13:
                #                 skip_rounds.append(i - hole_index * number_of_rounds + 1)
                #             # print("\t\t\t" + str(child))
                #             # print("\t\t\t" + str(type(child)))
                #     # print(holes[i].span.string)
                # print(skip_rounds)
                # for child in holes[hole_index].contents:
                #     print(child)
                #     if str(type(child)) == "<class 'bs4.element.Tag'>":
                #         print(child)
                # print(child.attrs["id"])
            # one <table> tag represents one division
            # <table> is splitted into <thead> and <tbody>
            # in the <thead> tag, the parameter "total" should be stored
            continue_with_division = False

            # search for "total" parameter
            thead = tab.thead

            for th in thead.tr:
                if str(type(th)) == "<class 'bs4.element.Tag'>":
                    if th.attrs['class'][0] == "total":
                        continue_with_division = True
            division = ""
            for content in headers[division_index].contents:
                if (str(type(content))) == "<class 'bs4.element.NavigableString'>" and str(
                        content).strip() != "":
                    division = content.strip()
            # if total parameter is present, continue to parse given division
            if continue_with_division and division in ["Open", "Open Women"]:
                body = tab.tbody

                # row represents one <tr> tag inside of <tbody> tag and thus tournament results for one person
                for row in body:
                    if str(type(row)) == "<class 'bs4.element.Tag'>":
                        player = dict()

                        # obtain person id - pdga#
                        pid = None
                        pdga = None
                        for cell in row:
                            if str(type(cell)) == "<class 'bs4.element.Tag'>":
                                if len(cell.attrs["class"]) == 1 and cell.attrs["class"][0] == "pdga-number":
                                    pdga = cell.string

                        pid = pdga
                        # print(dict((sibs.attrs["class"], sibs.string) for sibs in row.td.next_siblings if len(sibs.attrs["class"]) == 1))
                        # since the round number is not given on the webpage, it must be counted in the program
                        round_number = 1

                        # some players are not registered PDGA players and thus don't have any PDGA#
                        if pid is not None:
                            pid = str(pid)
                            add = True
                            # parsing each column in row
                            for cell in row:
                                if str(type(cell)) == "<class 'bs4.element.Tag'>":

                                    # all the columns we need have just one class
                                    if len(cell.attrs["class"]) == 1:
                                        cell_class = cell.attrs["class"][0]
                                        # if cell_class == "place":
                                        #     player["place"] = cell.string
                                        if cell_class == "round" and round_number not in skip_rounds:
                                            player["round " + str(round_number)] = dict()
                                            player["round " + str(round_number)]["points"] = cell.string
                                        # if round_number in skip_rounds:
                                        #     print("skip" + pid)
                                        if cell_class == "round-rating" and round_number not in skip_rounds:
                                            try:
                                                gender = playerArray[pid]
                                            except KeyError:
                                                add = False
                                                del player["round " + str(round_number)]
                                                break
                                            if cell is None or cell.string is None:
                                                del player["round " + str(round_number)]
                                            else:
                                                if cell.string.strip() != "" and (
                                                            (gender == "M" and int(
                                                                cell.string.strip()) >= minBoundaryMPO) or (
                                                                        gender == "F" and int(
                                                                    cell.string.strip()) >= minBoundaryFPO)):
                                                    # print(pid + " " + str(round_number))
                                                    player["round " + str(round_number)]["rating"] = cell.string
                                                    # print(division)
                                                else:
                                                    del player["round " + str(round_number)]
                                            round_number += 1
                            if len(player.items()) >= 1 and add:
                                results[pid] = player.copy()
            hole_index += 1
        # if len(results) == 0:
        #     # print("nikto")
        #     pass
        # else:
        #     # print(results)
        if len(results) > 0:
            return Tournament(dic["id"], dic["name"], dic["Date"], results, False)
        else:
            return None
    except AttributeError:
        print("found the experimental event with teams")
        raise


# t = time.time()
# r = getAllTournaments()
# print("Number of tournaments: " + str(len(r)))
#
# print(str(time.time() - t) + " seconds")

# t = getOfficialTournamentByID("33853")
# print(t)

def getTournament(id):
    URL = "https://www.pdga.com/tour/event/" + str(id)
    # print(URL)
    try:
        soup = BeautifulSoup(urlopen(URL), "lxml")
        headers = soup.find_all("h3", "division")
        tables = soup.find_all("table", "results sticky-enabled")

        title = soup.find_all("title")[0]
        tournament_name = title.contents[0].split(" | ")[0]
        print(tournament_name)
        summary_table = soup.find_all("table", "summary sticky-enabled")[0]
        official_string = summary_table.previous_sibling.contents[0].split(" ")[0]
        tournament_official = True if official_string == "Official" else False

        date = soup.find_all("li", "tournament-date")[0]
        tournament_date = ""
        for content in date.contents:
            if (str(type(content))) == "<class 'bs4.element.NavigableString'>" and str(content).strip() != "":
                tournament_date = content.split(" ")[-1]

        tournament_results = dict()
        i = 0
        for table in tables:
            division = ""
            for content in headers[i].contents:
                if (str(type(content))) == "<class 'bs4.element.NavigableString'>" and str(content).strip() != "":
                    division = content.strip()
            if division == "Open" or division == "Open Women":
                division_results = dict()
                tbody = table.tbody
                for row in tbody:
                    if (str(type(row))) == "<class 'bs4.element.Tag'>":
                        pid = None
                        for cell in row:
                            if str(type(cell)) == "<class 'bs4.element.Tag'>":
                                if len(cell.attrs["class"]) == 1 and cell.attrs["class"][0] == "pdga-number":
                                    pid = cell.string
                        player_results = dict()
                        player_results["rounds"] = dict()
                        round_number = 1
                        finished = True
                        for cell in row:
                            if str(type(cell)) == "<class 'bs4.element.Tag'>":
                                if cell.attrs["class"][0] == "place":
                                    player_results["place"] = cell.string
                                if cell.attrs["class"][0] == "round":
                                    player_results["rounds"][str(round_number)] = dict()
                                    player_results["rounds"][str(round_number)]["points"] = cell.string
                                if cell.attrs["class"][0] == "round-rating":
                                    player_results["rounds"][str(round_number)]["rating"] = cell.string
                                    round_number += 1
                                if cell.attrs["class"][0] == "total" and cell.string == "DNF":
                                    finished = False
                        if finished is not False:
                            player_results["finished"] = True
                            division_results[pid] = player_results
                tournament_results[division] = division_results
            i += 1
        return Tournament(id, tournament_name, tournament_date, tournament_results, tournament_official)
    except HTTPError:
        print("not found")
        return None
