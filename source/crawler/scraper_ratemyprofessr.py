"""
Scraping Rate My Professor
System setup

Before we start, make sure to install the required libraries

pip install bs4
pip install selenium

For Chrome, I also downloaded the appropriate webdriver from here: http://chromedriver.chromium.org/downloads, unzip it and save in current directory.
"""

#!pip install bs4
#!pip install selenium
#!apt install chromium-chromedriver

from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from RateMyProf import RateMyProfScraper
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from collections import OrderedDict
#from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.chrome.service import Service
import re 
import urllib
import time
import unicodecsv as csv

#create a webdriver object and set options for headless browsing
options = Options()
options.headless = True
#options.add_argument('--no-sandbox')
#options.add_argument('--disable-dev-shm-usage')
#service = Service("chromedriver")
driver = webdriver.Chrome("chromedriver",options=options)

"""
Before we start scraping, we'll define some helper functions
uses webdriver object to execute javascript code and get dynamically loaded webcontent
"""
def get_js_soup(url,driver):
    driver.get(url)
    res_html = driver.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html,'html.parser') #beautiful soup object to be used for parsing html content
    return soup

#tidies extracted text 
def process_bio(bio):
    bio = bio.encode('ascii',errors='ignore').decode('utf-8')       #removes non-ascii characters
    bio = re.sub('\s+',' ',bio)       #repalces repeated whitespace characters with single space
    return bio

''' More tidying
Sometimes the text extracted HTML webpage may contain javascript code and some style elements. 
This function removes script and style tags from HTML so that extracted text does not contain them.
'''
def remove_script(soup):
    for script in soup(["script", "style"]):
        script.decompose()
    return soup

"""
We will now start scraping.
Using the helper class RateMyProfScraper, we can get a list of all the professors at UIUC who have more than 30 reviews. We can use the tid, metadata information from the request to create the corresponding urls which we will use later to scrape.
"""

UIUC = RateMyProfScraper(1112)
#for professor in UIUC.professorlist:
#    print(professor)
#UIUC.SearchProfessor("Laura Hill")
print(len(UIUC.professorlist))

"""
Fetching url with "tid" for each professor, needed for finding the rate my professor url
"""


#extracts all Faculty Profile page urls from the Directory Listing Page
def scrape_dir_page(driver, professor):
    base_url = 'https://www.ratemyprofessors.com/ShowRatings.jsp?tid='
    curr_page = base_url + str(professor['tid'])
    professor_name = professor['tFname'] + " " + professor['tLname']
    faculty_links.append({ professor_name: curr_page }) 

"""
Creating a list of dictionaries with keys [{"professor name":"test", "faculty url":"testurl"}]
"""

#dir_url = 'https://engineering.virginia.edu/departments/electrical-and-computer-engineering/electrical-computer-engineering-faculty?page=' #url of directory listings of CS faculty
faculty_links = []
for professor in UIUC.professorlist:
    scrape_dir_page(driver, professor)

print ('-'*20,'Scraping directory page','-'*20)
print ('-'*20,'Found {} faculty profile urls'.format(len(faculty_links)),'-'*20)

print(faculty_links[0:5])

"""
Helper function that loads each faculty url, pushes "load more comments" button multiple times, and gets the final result list of comments

Fetches:comment rating
"""

def scrape_faculty_page(professor_name, fac_url,driver):
    driver.get(fac_url)
    homepage_found = False
    reviews = []
    bio = ''
    
    while True:
        try:
            element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//button[normalize-space()="Load More Ratings"]')))
            loadmore = driver.find_element_by_xpath('//button[normalize-space()="Load More Ratings"]')
            actions = ActionChains(driver)
            actions.move_to_element(loadmore).perform()
            actions.click().perform()
            #driver.execute_script("arguments[0].scrollIntoView();", loadmore)
            #driver.execute_script("arguments[0].click();", loadmore)
            #print("clicking")
        except TimeoutException:
            print("End of loading")
            break
        except NoSuchElementException:
            print("End of loading")
            break

    res_html = driver.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html,'html.parser') #beautiful soup object to be used for parsing html content
    results = soup.find(id="ratingsList")

    for li in results:
        comment = li.find("div", class_="Comments__StyledComments-dzzyvm-0 gRjWel")
        rating = li.find("div", class_=["CardNumRating__CardNumRatingNumber-sc-17t4b9u-2 kMhQxZ","CardNumRating__CardNumRatingNumber-sc-17t4b9u-2 bUneqk"])
        tags = li.find("div", class_="RatingTags__StyledTags-sc-1boeqx2-0 eLpnFv")

        if comment and rating and tags:
            review = OrderedDict()
            review['professor'] = professor_name
            review['comment'] = comment.text.strip()
            review['rating'] = rating.text.strip()
            tags_list = []
            for span in tags.select('span'):
                tags_list.append(span.text.strip())
            review['tags'] = '|'.join(tags_list)
            reviews.append(review)
    
    return reviews

"""
Finding the comments and ratings for each professor
"""

#reviews = scrape_faculty_page("Gretchen Adams", "https://www.ratemyprofessors.com/ShowRatings.jsp?tid=477677", driver)
#print(reviews)
all_reviews = []
for link in faculty_links[0:150]:
    for item in link.items():
        print ('-'*20,'Scraping faculty url {}'.format(item[1]),'-'*20)
        reviews = scrape_faculty_page(item[0], item[1], driver)
        all_reviews.extend(reviews)

"""
Writing the results to CSV file
"""

print(all_reviews[0:2])

with open('../../prof/spreadsheet_150_tags.csv', 'w') as outfile:
    fp = csv.DictWriter(outfile, all_reviews[0].keys(), encoding='utf-8')
    fp.writeheader()
    #fp.writerow([unicode(s, "utf-8") for s in all_reviews])
    #fp.writerow([str(text, 'utf-8') for s in all_reviews])
