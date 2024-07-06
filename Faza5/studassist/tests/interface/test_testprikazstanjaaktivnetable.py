import unittest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TestTestprikazstanjaaktivnetable(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def tearDown(self):
        self.driver.quit()

    def test_testprikazstanjaaktivnetable(self):
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.set_window_size(1722, 2000)
        self.driver.find_element(By.LINK_TEXT, "Menze").click()
        self.driver.find_element(By.CSS_SELECTOR, ".flex-item:nth-child(1) h4").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".main-title").text == "Menza - Karaburma"
        self.driver.find_element(By.ID, "stanje-container").click()
        elements = self.driver.find_elements(By.ID, "tabla-stanje")
        assert len(elements) > 0


if __name__ == "__main__":
    unittest.main()