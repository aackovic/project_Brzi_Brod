from selenium import webdriver
from studassist.models import *

from django.contrib.auth.models import Group

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


class TestLoginmoderatoraispravno(StaticLiveServerTestCase):
    def setUp(self):
        service = webdriver.ChromeService(
            executable_path='C:\\Users\\zlatk\\Documents\\ETF\\PSI\\Projekat\\proj\\project_Brzi_Brod\\Faza5\\chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)
        self.appUrl = self.live_server_url + "/login"

        user = User.objects.create_user(username='testuser', password='testpassword')
        korisnik = Korisnik.objects.filter(idkor=user).first()

        meni = Meni.objects.create()
        menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                     slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                     radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')
        moderator = Moderator.objects.create(idmod=korisnik, idmnz=menza)

        moderator_group = Group.objects.create(name='moderator')
        user.groups.add(moderator_group)

    def tearDown(self):
        self.browser.close()

    def test_loginmoderatoraispravno(self):
        self.browser.get(self.appUrl)
        self.browser.set_window_size(1536, 816)

        self.browser.find_element(By.ID, "id_username").send_keys("testuser")
        self.browser.find_element(By.ID, "id_password").click()
        self.browser.find_element(By.ID, "id_password").send_keys("testpassword")
        self.browser.find_element(By.CSS_SELECTOR, ".mt-2").click()


class TestLoginmoderatoranepostojeciusername(StaticLiveServerTestCase):
    def setUp(self):
        service = webdriver.ChromeService(
            executable_path='C:\\Users\\zlatk\\Documents\\ETF\\PSI\\Projekat\\proj\\project_Brzi_Brod\\Faza5\\chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)
        self.appUrl = self.live_server_url + "/login"

        user = User.objects.create_user(username='testuser', password='testpassword')
        korisnik = Korisnik.objects.filter(idkor=user).first()

        meni = Meni.objects.create()
        menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                     slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                     radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')
        moderator = Moderator.objects.create(idmod=korisnik, idmnz=menza)

        moderator_group = Group.objects.create(name='moderator')
        user.groups.add(moderator_group)

    def tearDown(self):
        self.browser.close()

    def test_loginmoderatoranepostojeciusername(self):
        self.browser.get(self.appUrl)
        self.browser.set_window_size(1536, 816)

        self.browser.find_element(By.ID, "id_username").click()
        self.browser.find_element(By.ID, "id_username").send_keys("Mika")
        self.browser.find_element(By.ID, "id_password").click()
        self.browser.find_element(By.ID, "id_password").send_keys("Mika3#1111")
        self.browser.find_element(By.CSS_SELECTOR, ".mt-2").click()

        self.assertEqual(self.browser.find_element(By.CSS_SELECTOR, "ul:nth-child(5) > li").text,
                         "Nekorektni kredencijali.")


class TestLoginmoderatorapogresanpass(StaticLiveServerTestCase):
    def setUp(self):
        service = webdriver.ChromeService(
            executable_path='C:\\Users\\zlatk\\Documents\\ETF\\PSI\\Projekat\\proj\\project_Brzi_Brod\\Faza5\\chromedriver.exe')
        self.browser = webdriver.Chrome(service=service)
        self.appUrl = self.live_server_url + "/login"

        user = User.objects.create_user(username='testuser', password='testpassword')
        korisnik = Korisnik.objects.filter(idkor=user).first()

        meni = Meni.objects.create()
        menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                     slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                     radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')
        moderator = Moderator.objects.create(idmod=korisnik, idmnz=menza)

        moderator_group = Group.objects.create(name='moderator')
        user.groups.add(moderator_group)

    def tearDown(self):
        self.browser.close()

    def test_loginmoderatoranepostojeciusername(self):
        self.browser.get(self.appUrl)
        self.browser.set_window_size(1536, 816)

        self.browser.find_element(By.ID, "id_username").click()
        self.browser.find_element(By.ID, "id_username").send_keys("testuser")
        self.browser.find_element(By.ID, "id_password").click()
        self.browser.find_element(By.ID, "id_password").send_keys("incorrectpassword")
        self.browser.find_element(By.CSS_SELECTOR, ".mt-2").click()

        self.assertEqual(self.browser.find_element(By.CSS_SELECTOR, "ul:nth-child(5) > li").text,
                         "Nekorektni kredencijali.")
