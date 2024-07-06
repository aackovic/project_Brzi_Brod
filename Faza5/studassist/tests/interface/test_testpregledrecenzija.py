import unittest
import time
import json
from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException


class TestTestpregledrecenzija(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def tearDown(self):
        self.driver.quit()



    def test_testpregledrecenzija(self):
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.set_window_size(1722, 2000)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "id_username").send_keys("andrej")
        self.driver.find_element(By.ID, "id_password").send_keys("123")
        self.driver.find_element(By.CSS_SELECTOR, ".mt-2").click()
        self.driver.find_element(By.LINK_TEXT, "Menze").click()
        self.driver.find_element(By.CSS_SELECTOR, ".flex-item:nth-child(1) h4").click()

        # Wait for the expand button to be clickable
        expand_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".expand-btn"))
        )

        try:
            expand_button.click()
        except ElementClickInterceptedException:
            # Scroll to the element and try clicking it again
            self.driver.execute_script("arguments[0].scrollIntoView(true);", expand_button)
            self.driver.execute_script("arguments[0].click();", expand_button)

        qr_modal_label = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "qrModalLabel2"))
        )
        self.assertEqual(qr_modal_label.text, "Karaburma - Recenzije")

        sort_text = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "b"))
        )
        self.assertEqual(sort_text.text, "Sortirajte")


if __name__ == "__main__":
    unittest.main()