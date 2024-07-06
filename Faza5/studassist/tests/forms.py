# Ema Paunović 0028/2021
# Jelena Blagojević 0029/2021
# Andrej Ačković 0263/2021
# Zlatko Golubović 0089/2021
from django.test import TestCase
from studassist.forms import *
from datetime import date, datetime

class StudentDepositMoneyFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'amount' : 1000
        }
        form = StudentDepositMoneyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'amount' : 10000000000
        }
        form = StudentDepositMoneyForm(data=form_data)
        self.assertFalse(form.is_valid())


class StudentCardFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'id_kartice' : '1234123412341234',
            'form_id' : 's'
        }
        form = StudentCardForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'id_kartice' : '123412341234123412341234123412341234123412341234',
            'form_id' : 's'
        }
        form = StudentCardForm(data=form_data)
        self.assertFalse(form.is_valid())


class RegisterFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'first_name': 'Andrej',
            'last_name' : 'Ackovic',
            'email' : 'andrej@gmail.com',
            'address' : 'Nis',
            'birthdate' : date(2022,1,1),
            'telnum' : '+381641021575',
            'username' : 'acko',
            'password1' : 'Kolokvijum123*',
            'password2' : 'Kolokvijum123*'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'first_name': '',
            'last_name' : 'Ackovic',
            'email' : 'andrej@gmail.com',
            'address' : 'Nis',
            'birthdate' : datetime(2022,1,1),
            'telnum' : '+381641021575',
            'username' : 'acko',
            'password1' : 'Kolokvijum123*',
            'passwrod2' : 'Kolokvijum123*'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())


class LoginFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username' : 'andrej',
            'password' : '123',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'username' : 'acko',
            'password1' : 'Kolokvijum123*ABCDEGGGFFG',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserPasswordFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'password': 'abcde'
        }
        form = UserPasswordForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'password' : 'abcdeabcdeabcdeabcdea'
        }
        form = UserPasswordForm(data=form_data)
        self.assertFalse(form.is_valid())


class OdgovorFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'naslov': 'Odlicna je hrana',
            'comment': 'Bas je dobra hrana sve pohvale',
        }
        form = OdgovorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'naslov': '123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920',
            'comment': 'Bas je dobra hrana sve pohvale',
        }
        form = OdgovorForm(data=form_data)
        self.assertFalse(form.is_valid())


class RecenzijaFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'descr': 'Odlicna je hrana',
            'comment': 'Bas je dobra hrana sve pohvale',
            'rating' : 4,
        }
        form = RecenzijaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'descr': '123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920\
            123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920123456789101112131415161718192012345678910111213141516171819201234567891011121314151617181920',
            'comment': 'Bas je dobra hrana sve pohvale',
        }
        form = RecenzijaForm(data=form_data)
        self.assertFalse(form.is_valid())