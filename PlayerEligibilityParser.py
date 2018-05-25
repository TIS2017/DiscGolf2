from bs4 import BeautifulSoup
from urllib.request import urlopen

def calculateEligibility(pid, minimalPercentage):
    url = "https://www.pdga.com/player/" + str(pid)
    soup = BeautifulSoup(urlopen(url), "lxml")
    # print("\t\t\t" + url)
    openTotal = soup.find_all("td", string="Open")
    if len(openTotal) == 0:
        openTotal = soup.find_all("td", string="Open Women")
        if len(openTotal) == 0:
            return False
    openTotalInt = int(openTotal[0].next_sibling.string)

    proTotal = soup.find_all("td", string="Pro Totals:")
    proTotalInt = 0
    if len(proTotal) != 0:
        proTotalInt = int(proTotal[0].next_sibling.string)

    amTotal = soup.find_all("td", string="Am Totals:")
    amTotalInt = 0
    if len(amTotal) != 0:
        amTotalInt = int(amTotal[0].next_sibling.string)

    if openTotalInt / (proTotalInt + amTotalInt) * 100 >= minimalPercentage:
        return True
    else:
        return False