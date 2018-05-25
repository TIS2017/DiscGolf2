import db as DatabaseManager

class Player:

    def __init__(self, par_first_name, par_last_name, par_pdga_number, par_rating, par_gender, par_european=False):
        self.__eligibility = False
        self.__first_name = par_first_name
        self.__last_name = par_last_name
        self.__pdga_number = par_pdga_number
        self.__rating = par_rating
        self.__gender = par_gender
        self.__european = par_european

    def setEligibility(self, param):
        self.__eligibility = param

    def getEligibility(self):
        return self.__eligibility

    def getFirstName(self):
        return self.__first_name

    def getLastName(self):
        return self.__last_name

    def getID(self):
        return self.__pdga_number

    def getRating(self):
        return self.__rating if self.__rating is not None else 0
    
    def getGender(self):
        return self.__gender

    def getEuropean(self):
        return self.__european
        
    def insert(self):
        DatabaseManager.insert("players", (self.getFirstName(), self.getLastName(), self.getGender(), self.getID(), self.getRating(), self.getEligibility(), self.getEuropean()))

    # def delete(self):
    #     DatabaseManager.delete("players", "id = " + self.__pdga_number)

    # def edit(self):
    #     pass
