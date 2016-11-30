from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# The URL used to login
HACKERRANK_LOGIN_URL = 'https://hackerrank.com/login'

# The element names of the username/password textfields and the name of the
# hackerrank feed that recognizes a succesful login
HACKERRANK_USERNAME_ELMNT = 'login'
HACKERRANK_PASSWORD_ELMNT = 'password'
HACKERRANK_FEED_CLASS_NAME = 'track-master'

class Competitor:
    def __init__(self, position, username, completedCount):
        self.position = position
        self.username = username
        self.completedCount = completedCount

    def __str__(self):
        return '{0:<5} {1:<25} {2:<5}'.format(self.position, self.username, 
                self.completedCount)

    def __repr__(self):
        return self.__str__()

class Scraper:
    def __init__(self, hackerrank_username, hackerrank_password,
                 hackerrank_leaderboard_url, driver_factory=webdriver.PhantomJS):
        self.driver = driver_factory()
        self.hackerrank_username = hackerrank_username
        self.hackerrank_password = hackerrank_password
        self.hackerrank_leaderboard_url = hackerrank_leaderboard_url
        self.loggedin = False

    def print_clean_usernames_from_page(self, leadersTableElement):
        userListBoxes = leadersTableElement.find_elements_by_class_name("leaderboard-list-view")
        for listbox in userListBoxes:
            row = listbox.find_element_by_class_name("row ")
            number = row.find_elements_by_css_selector(".span-flex-1.acm-leaderboard-cell")[0]
            nameCell = row.find_elements_by_css_selector(".span-flex-2.acm-leaderboard-cell")[0]
            completedCell = row.find_elements_by_css_selector(".span-flex-1.acm-leaderboard-cell")[1]
            competitorToAdd = Competitor(number.text, nameCell.text, completedCell.text)
            print("Found competitor {}".format(competitorToAdd))
            yield competitorToAdd

        
    def load_leaderboard_pages(self, leaderboardURL):
        self.driver.implicitly_wait(30)
        pageSource = ""
        pageNumber = 1
        while not "Sorry, we require a few more submissions" in pageSource:
            print("Loading page {}".format(pageNumber))
            self.driver.get('{}/{}'.format(leaderboardURL, pageNumber))
            pageSource = self.driver.page_source
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "leaderboard-list-view"))
                )
            except TimeoutException:
                return
            print("Loaded!.. getting leaders")
            leaderboardElement = self.driver.find_element_by_id("leaders")
            pageSource = self.driver.page_source
            for competitor in self.print_clean_usernames_from_page(leaderboardElement):
                yield competitor
            pageNumber += 1

    def _login(self, username, password):
        """
        Logs in the user using the specified username and password by going
        to the login page, entering the username/password, and waiting for the
        feed to load.

        This does not do username/password validation. Ensure that the username
        and password are correct before calling.
        """
        print("Logging in...")
        self.driver.get(HACKERRANK_LOGIN_URL)
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located(
                (By.NAME, HACKERRANK_USERNAME_ELMNT)
            )
        )
        usernameField = self.driver.find_element_by_css_selector(
            'form#legacy-login input[id="login"]'
        )
        passwordField = self.driver.find_element_by_css_selector(
            'form#legacy-login input[id="password"]'
        )
        usernameField.send_keys(username)
        print("filled in username")
        passwordField.send_keys(password)
        print("filled in password")
        passwordField.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 100).until (
            EC.presence_of_element_located(
                (By.CLASS_NAME, HACKERRANK_FEED_CLASS_NAME)
            )
        )
        print("DONE!")

    def login(self):
        self._login(self.hackerrank_username, self.hackerrank_password)
        self.loggedin = True

    def _scrape(self, leaderboard_url):
        print("scraping...")
        for list in self.load_leaderboard_pages(leaderboard_url):
            yield list

    def scrape(self):
        if not self.loggedin:
            raise ValueError('Must call login() before scraping')

        for list in self._scrape(self.hackerrank_leaderboard_url):
            yield list
