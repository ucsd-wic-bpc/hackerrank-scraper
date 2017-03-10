from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging

logger = logging.getLogger('hackerrank_scraper.scraper')

# The URL used to login
HACKERRANK_LOGIN_URL = 'https://hackerrank.com/login'

# The element names of the username/password textfields and the name of the
# hackerrank feed that recognizes a succesful login
HACKERRANK_USERNAME_ELMNT = 'login'
HACKERRANK_PASSWORD_ELMNT = 'password'
HACKERRANK_FEED_CSS_SELECTOR = 'div.fw.border-bottom.inline-block.psB.pjT'

# The element names of the leaderboard fields
HACKERRANK_LEADERBOARD_LIST_CLASS_NAME = 'leaderboard-list-view'


# The elements corresponding to individual fields in the leaderboard
HACKERRANK_LEADERBOARD_ROW_CLASS_NAME = 'row '
HACKERRANK_LEADERBOARD_ROW_POSITION_CSS_SELECTOR = '.span-flex-1.acm-leaderboard-cell'
HACKERRANK_LEADERBOARD_ROW_USERNAME_CSS_SELECTOR = '.span-flex-2.acm-leaderboard-cell'
HACKERRANK_LEADERBOARD_ROW_COMPLETED_CSS_SELECTOR = '.span-flex-1.acm-leaderboard-cell'


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

    def _parse_leaderboard_row(self, row):
        position = row.find_elements_by_css_selector(HACKERRANK_LEADERBOARD_ROW_POSITION_CSS_SELECTOR)[0]
        username = row.find_elements_by_css_selector(HACKERRANK_LEADERBOARD_ROW_USERNAME_CSS_SELECTOR)[0]
        problems = row.find_elements_by_css_selector(HACKERRANK_LEADERBOARD_ROW_COMPLETED_CSS_SELECTOR)[1]

        return position.text, username.text, problems.text

    def get_competitors_from_leaders_table(self, leadersTableElement):
        userListBoxes = leadersTableElement.find_elements_by_class_name(
            HACKERRANK_LEADERBOARD_LIST_CLASS_NAME
        )

        for listbox in userListBoxes:
            row = listbox.find_element_by_class_name(HACKERRANK_LEADERBOARD_ROW_CLASS_NAME)
            position, username, problems_completed = self._parse_leaderboard_row(row)

            problems_completed = (
                0 if problems_completed == '-' else int(problems_completed)
            )

            competitor = Competitor(position, username, problems_completed)
            logger.debug('Loaded competitor {}'.format(competitor))
            yield competitor

    def get_competitors_from_leaderboard(self, leaderboardURL):
        logger.info('Loading leaderboard from url {}'.format(leaderboardURL))
        self.driver.implicitly_wait(30)
        pageSource = ""
        pageNumber = 1
        while "Sorry, we require a few more submissions" not in pageSource:
            logger.debug('Loading page {}'.format(pageNumber))
            self.driver.get('{}/{}'.format(leaderboardURL, pageNumber))
            pageSource = self.driver.page_source

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, HACKERRANK_LEADERBOARD_LIST_CLASS_NAME)
                    )
                )
            except TimeoutException:
                logger.info('Leaderboard details not found -- Done loading')
                return

            logger.debug('Leaderboard details loaded -- loading competitors')
            leaderboardElement = self.driver.find_element_by_id("leaders")
            pageSource = self.driver.page_source
            for competitor in self.get_competitors_from_leaders_table(leaderboardElement):
                yield competitor

            logger.debug('Page {} loaded.'.format(pageNumber))
            pageNumber += 1

    def _login(self, username, password):
        """
        Logs in the user using the specified username and password by going
        to the login page, entering the username/password, and waiting for the
        feed to load.

        This does not do username/password validation. Ensure that the username
        and password are correct before calling.
        """
        logger.info('Beginning login process for username:password {}:{}'
                    .format(username, password))
        self.driver.get(HACKERRANK_LOGIN_URL)

        logger.debug('Waiting for login page to load')
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located(
                (By.NAME, HACKERRANK_USERNAME_ELMNT)
            )
        )

        logger.debug('Finding login elements (username/password fields)')
        usernameField = self.driver.find_element_by_css_selector(
            'form#legacy-login input[id="login"]'
        )
        passwordField = self.driver.find_element_by_css_selector(
            'form#legacy-login input[id="password"]'
        )

        usernameField.send_keys(username)
        logger.debug('Filled in username')

        passwordField.send_keys(password)
        logger.debug('Filled in password')

        passwordField.send_keys(Keys.RETURN)
        logger.debug('Waiting for after-login page')
        WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, HACKERRANK_FEED_CSS_SELECTOR)
            )
        )

        logger.info('Login succesful')

    def login(self):
        self._login(self.hackerrank_username, self.hackerrank_password)
        self.loggedin = True

    def _scrape(self, leaderboard_url):
        for competitor in self.get_competitors_from_leaderboard(leaderboard_url):
            yield competitor

    def scrape(self, auto_login=False):
        if not self.loggedin:
            if auto_login:
                self.login()
            else:
                raise ValueError('Must call login() before scraping')

        for competitor in self._scrape(self.hackerrank_leaderboard_url):
            yield competitor
