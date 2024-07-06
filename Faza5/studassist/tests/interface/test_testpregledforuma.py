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

class TestTestpregledforuma(unittest.TestCase):
  def setUp(self):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def tearDown(self):
    self.driver.quit()
  
  def test_testpregledforuma(self):
    self.driver.get("http://127.0.0.1:8000/")
    self.driver.set_window_size(1722, 1042)
    self.driver.find_element(By.LINK_TEXT, "Forum").click()
    self.assertEqual(self.driver.find_element(By.LINK_TEXT, "Kvalitet hrane").text, "Kvalitet hrane")
    self.driver.find_element(By.LINK_TEXT, "Kvalitet hrane").click()
    self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, "h1:nth-child(1)").text, "Kvalitet hrane")
    self.assertEqual(self.driver.find_element(By.CSS_SELECTOR, "h3").text, "Odgovori")
  
if __name__ == "__main__":
    unittest.main()