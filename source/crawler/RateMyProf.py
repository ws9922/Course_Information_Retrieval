import requests
import json
import math

class RateMyProfScraper:
        def __init__(self,schoolid):
            self.UniversityId = schoolid
            self.professorlist = self.createlist()
            self.indexnumber = False

        def createlist(self):#creates List object that include basic information on all Professors from the IDed University
            tempprofessorlist = []
            num_of_prof = self.getNumOfProfessors(self.UniversityId)
            num_of_pages = math.ceil(num_of_prof / 20)
            i = 1
            while (i <= num_of_pages):# the loop insert all professor into list
                page = requests.get("http://www.ratemyprofessors.com/filter/professor/?&page=" + str(
                    i) + "&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" + str(
                    self.UniversityId))
                temp_jsonpage = json.loads(page.content)
                temp_list = temp_jsonpage['professors']
                #temp_add = []
                for professor in temp_list:
                    if professor['tNumRatings'] > 20:
                        tempprofessorlist.append(professor)
                #tempprofessorlist.extend(temp_add)
                i += 1
            return tempprofessorlist

        def getNumOfProfessors(self,id):  # function returns the number of professors in the university of the given ID.
            page = requests.get(
                "http://www.ratemyprofessors.com/filter/professor/?&page=1&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" + str(
                    id))  # get request for page
            temp_jsonpage = json.loads(page.content)
            num_of_prof = temp_jsonpage[
                              'remaining'] + 20  # get the number of professors at William Paterson University
            return num_of_prof