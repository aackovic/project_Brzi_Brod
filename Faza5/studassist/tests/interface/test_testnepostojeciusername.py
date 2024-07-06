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


class TestTestnepostojeciusername(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def tearDown(self):
        self.driver.quit()


    def test_testnepostojeciusername(self):
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.set_window_size(1722, 2000)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("123")
        self.driver.find_element(By.CSS_SELECTOR, ".mt-2").click()
        self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, "ul:nth-child(5) > li").text, "Nekorektni kredencijali.")


if __name__ == "__main__":
    unittest.main()

