# Ema Paunović 0028/2021
# Jelena Blagojević 0029/2021
# Andrej Ačković 0263/2021
# Zlatko Golubović 0089/2021
from django.test import TestCase, Client
from studassist.models import *
from django.contrib.auth.models import Group
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponseForbidden
from unittest.mock import patch, Mock
from datetime import datetime
from studassist.forms import RegistrationStudentForm


class StudentViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.group = Group.objects.create(name='student')
        self.user.groups.add(self.group)
        self.user.save()
        self.korisnik = Korisnik.objects.filter(idkor=self.user).first()
        self.verpin = Verifikacionipin.objects.create(brojstudkartice='1234-5678-9012-3456', pin='12345678901234567890')
        self.student = Student.objects.create(idstu=self.korisnik, stanjeracuna=2000, brojstudkartice=self.verpin,
                                              zeton=1, dorucak=1, rucak=2, vecera=3)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('student'))
        self.assertRedirects(response, '/login/?next=/student/')

    def test_forbidden_if_not_in_student_group(self):
        user_not_in_group = User.objects.create_user(username='otheruser', password='password')
        self.client.login(username='otheruser', password='password')
        response = self.client.get(reverse('student'))
        self.assertEqual(response.status_code, 403)

    def test_get_student_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('student'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/student.html')
        self.assertIn('bgStyle', response.context)
        self.assertEqual(response.context['username'], 'testuser')
        self.assertEqual(response.context['stanje'], 2000)

    def test_post_valid_token_purchase(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('student'), {'submit': 'submit', })

        self.student.refresh_from_db()
        self.assertRedirects(response, reverse('student'))
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].tags, "success")

        self.assertEqual(str(messages_list[0]), 'Žeton je uspešno kupljen')
        self.assertEqual(self.student.zeton, 2)
        self.assertEqual(self.student.stanjeracuna, 1000)

    def test_post_invalid_token_purchase(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('student'), {})

        self.student.refresh_from_db()
        self.assertRedirects(response, reverse('student'))
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].tags, "error")
        self.assertEqual(str(messages_list[0]), 'Greška - uneti podaci nisu validni.')
        self.assertEqual(self.student.zeton, 1)
        self.assertEqual(self.student.stanjeracuna, 2000)

    def test_post_not_enough_money(self):
        self.student.stanjeracuna = 500
        self.student.save()

        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('student'), {'submit': 'submit', })

        self.student.refresh_from_db()
        self.assertRedirects(response, reverse('student'))
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].tags, "error")
        self.assertEqual(str(messages_list[0]), 'Nemate dovoljno novca!')
        self.assertEqual(self.student.zeton, 1)
        self.assertEqual(self.student.stanjeracuna, 500)


class KupovinaBonovaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.group = Group.objects.create(name='student')
        self.user.groups.add(self.group)
        self.user.save()
        self.korisnik = Korisnik.objects.filter(idkor=self.user).first()
        self.verpin = Verifikacionipin.objects.create(brojstudkartice='1234-5678-9012-3456', pin='12345678901234567890')
        self.student = Student.objects.create(idstu=self.korisnik, stanjeracuna=2000, brojstudkartice=self.verpin,
                                              zeton=1, dorucak=1, rucak=2, vecera=3)

    def test_get_kupovina_bonova_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('kupovina_bonova'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/kupovina_bonova.html')

    def test_post_kupovina_bonova_success_d_1(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.dorucak = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'd_1'})
        self.assertRedirects(response, reverse('student'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')
        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 1950)
        self.assertEqual(self.student.dorucak, 1)

    def test_post_kupovina_bonova_success_d_5(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.dorucak = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'd_5'})
        self.assertRedirects(response, reverse('student'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 1750)
        self.assertEqual(self.student.dorucak, 5)

    def test_post_kupovina_bonova_success_d_10(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.dorucak = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'd_10'})
        self.assertRedirects(response, reverse('student'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 1500)
        self.assertEqual(self.student.dorucak, 10)

    def test_post_kupovina_bonova_success_r_1(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.rucak = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'r_1'})
        self.assertRedirects(response, reverse('student'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')
        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 1880)
        self.assertEqual(self.student.rucak, 1)

    def test_post_kupovina_bonova_success_r_5(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.rucak = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'r_5'})
        self.assertRedirects(response, reverse('student'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 1400)
        self.assertEqual(self.student.rucak, 5)

    def test_post_kupovina_bonova_success_r_10(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.rucak = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'r_10'})
        self.assertRedirects(response, reverse('student'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 800)
        self.assertEqual(self.student.rucak, 10)

    def test_post_kupovina_bonova_success_v_1(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.vecera = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'v_1'})
        self.assertRedirects(response, reverse('student'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')
        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 1910)
        self.assertEqual(self.student.vecera, 1)

    def test_post_kupovina_bonova_success_v_5(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.vecera = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'v_5'})
        self.assertRedirects(response, reverse('student'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 1550)
        self.assertEqual(self.student.vecera, 5)

    def test_post_kupovina_bonova_success_v_10(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 2000
        self.student.vecera = 0
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'v_10'})
        self.assertRedirects(response, reverse('student'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Obrok je kupljen')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 1100)
        self.assertEqual(self.student.vecera, 10)

    def test_post_kupovina_bonova_insufficient_funds_d_1(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.dorucak = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'd_1'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.dorucak, 2)

    def test_post_kupovina_bonova_insufficient_funds_d_5(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.dorucak = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'd_5'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.dorucak, 2)

    def test_post_kupovina_bonova_insufficient_funds_d_10(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.dorucak = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'd_10'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.dorucak, 2)

    def test_post_kupovina_bonova_insufficient_funds_r_1(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.rucak = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'r_1'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.rucak, 2)

    def test_post_kupovina_bonova_insufficient_funds_r_5(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.rucak = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'r_5'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.rucak, 2)

    def test_post_kupovina_bonova_insufficient_funds_r_10(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.rucak = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'r_10'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.rucak, 2)

    def test_post_kupovina_bonova_insufficient_funds_v_1(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.vecera = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'v_1'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.vecera, 2)

    def test_post_kupovina_bonova_insufficient_funds_v_5(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.vecera = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'v_5'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.vecera, 2)

    def test_post_kupovina_bonova_insufficient_funds_v_10(self):
        self.client.login(username='testuser', password='password')
        self.student.stanjeracuna = 0
        self.student.vecera = 2
        self.student.save()
        response = self.client.post(reverse('kupovina_bonova'), {'form_id': 'v_10'})
        self.assertRedirects(response, reverse('kupovina_bonova'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Nemate dovoljno novca!')

        self.student.refresh_from_db()
        self.assertEqual(self.student.stanjeracuna, 0)
        self.assertEqual(self.student.vecera, 2)


class UplataViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.group = Group.objects.create(name='student')
        self.user.groups.add(self.group)
        self.user.save()
        self.korisnik = Korisnik.objects.filter(idkor=self.user).first()
        self.verpin = Verifikacionipin.objects.create(brojstudkartice='1234-5678-9012-3456', pin='12345678901234567890')
        self.student = Student.objects.create(idstu=self.korisnik, stanjeracuna=2000, brojstudkartice=self.verpin,
                                              zeton=1, dorucak=1, rucak=2, vecera=3)

    def test_get_uplata_view(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('uplata'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/uplata.html')

    @patch('studassist.views.create_payment')
    def test_post_uplata_valid_form(self, mock_create_payment):
        mock_payment = Mock(links=[Mock(rel='approval_url', href='http://mock_approval_url')])
        mock_create_payment.return_value = mock_payment

        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('uplata'), {'amount': 10000})

        self.assertRedirects(response, 'http://mock_approval_url')

    @patch('studassist.views.create_payment')
    def test_post_uplata_invalid_form(self, mock_create_payment):
        mock_create_payment.return_value = None

        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('uplata'), {'amount': 10000})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/uplata.html')
        self.assertContains(response, 'Neuspešno pravljenje uplate')


class HomepageViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_homepage_view(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/index.html')
        self.assertIn('bgStyle', response.context)
        self.assertEqual(response.context['bgStyle'], 'bgorange')


class ModeratorViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.mod_user = User.objects.create_user(username='testuser', password='password')
        self.mod_group = Group.objects.create(name='moderator')
        self.mod_user.groups.add(self.mod_group)
        self.mod_user.save()
        self.korisnik = Korisnik.objects.filter(idkor=self.mod_user).first()

        self.meni = Meni.objects.create()
        self.menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                          slika='Another Image', idmen=self.meni, radnovremedor='08:00-10:00',
                                          radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')
        self.moderator = Moderator.objects.create(idmod=self.korisnik, idmnz=self.menza)

    def test_moderator_view_as_admin(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('moderator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bgmoderator')
        self.assertEqual(response.context['username'], 'testuser')
        self.assertTemplateUsed(response, 'studassist/moderator.html')

    def test_moderator_view_as_non_admin(self):
        self.client.login(username='testuser', password='password')
        self.mod_user.groups.clear()
        response = self.client.get(reverse('moderator'))
        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response, HttpResponseForbidden)


class MenzaViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_menza_view(self):
        meni = Meni.objects.create()
        menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                     slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                     radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')
        response = self.client.get(reverse('menza', kwargs={'naziv': 'Test Menza'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/menza.html')


class ModeratorFuncTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.mod_user = User.objects.create_user(username='testuser', password='password')
        self.mod_group = Group.objects.create(name='moderator')
        self.mod_user.groups.add(self.mod_group)
        self.mod_user.save()
        self.korisnik = Korisnik.objects.filter(idkor=self.mod_user).first()

        self.meni = Meni.objects.create()
        self.menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                          slika='Another Image', idmen=self.meni, radnovremedor='08:00-10:00',
                                          radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')
        self.moderator = Moderator.objects.create(idmod=self.korisnik, idmnz=self.menza)

        self.aktivnatabla = Aktivnatabla.objects.create(idmnz=self.menza, aktivna=1, tipobroka='D')

        self.user = User.objects.create_user(username='testuser2', password='password')

        self.korisnik2 = Korisnik.objects.filter(idkor=self.user).first()
        self.verpin = Verifikacionipin.objects.create(brojstudkartice='1234-5678-9012-3456', pin='12345678901234567890')
        self.student = Student.objects.create(idstu=self.korisnik2, stanjeracuna=2000, brojstudkartice=self.verpin,
                                              zeton=1, dorucak=1, rucak=2, vecera=3)

        self.client.login(username='testuser', password='password')

    def test_otvori_menzu(self):
        input_data = {'form_id': 'formTip', 'tip': 'D'}
        response = self.client.post(reverse('moderator'), input_data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(str(messages[0]),
                      ['Obrok aktivan', 'Menza već radi', "Greška - uneti podaci nisu validni.", "Nesto"])

    def test_zatvori_menzu(self):
        input_data = {'form_id': 'formZatvori'}
        response = self.client.post(reverse('moderator'), input_data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(str(messages[0]), ['Obrok zatvoren', "Greška - uneti podaci nisu validni."])

    def test_ulaz_studenta(self):
        input_data = {'form_id': 'formUlaz', 'id_kartice': '1234-5678-9012-3456'}
        response = self.client.post(reverse('moderator'), input_data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

        self.assertIn(str(messages[0]),
                      ['Nepostojeci student', 'Menza ne radi', 'Student nema zeton', 'Zeton skeniran!',
                       "Greška - uneti podaci nisu validni."])

    def test_izlaz_studenta(self):
        input_data = {'form_id': 'formIzlaz', 'id_kartice': '1234-5678-9012-3456'}
        response = self.client.post(reverse('moderator'), input_data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(str(messages[0]), ['Nepostojeci student', 'Zeton skeniran!', 'Menza ne radi',
                                         "Greška - uneti podaci nisu validni."])

    def test_kupovina_obroka(self):
        input_data = {'form_id': 'formKupi', 'id_kartice': '1234-5678-9012-3456'}
        response = self.client.post(reverse('moderator'), input_data)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn(str(messages[0]),
                      ['Menza ne radi', 'Student nema bon', 'Bon skeniran!', "Greška - uneti podaci nisu validni.",
                       'Nepostojeci student'])


class MenzeViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_menza_view(self):
        response = self.client.get(reverse('menze'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/menze.html')


class OstavljanjeRecenzijaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        meni = Meni.objects.create()
        self.menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                          slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                          radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')

        User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        korisnik = Korisnik.objects.first()
        verpin = Verifikacionipin.objects.create(brojstudkartice='1234-5678-9012-3456', pin='12345678901234567890')
        self.student = Student.objects.create(idstu=korisnik, stanjeracuna=2000, brojstudkartice=verpin)

    def test_post_valid_data(self):
        recenzija = Recenzija.objects.create(opis='Test Opis', tekst='Test Tekst',
                                             datumvreme=datetime(2022, 1, 1, 10, 30, 0),
                                             ocena=5, idstu=self.student, idmnz=self.menza)

        url = reverse('menza', kwargs={'naziv': '123'})
        url1 = reverse('menza_sort', kwargs={'menza': 'Test Menza', 'sortVal': '-datumvreme'})
        response = self.client.post('', {
            'url1': url,
            'url2': url1,
            'form_id': 'S',
            'users': 'testuser',
            'opis': recenzija.opis,
            'tekst': recenzija.tekst,
            'datumvreme': recenzija.datumvreme,
            'ocena': recenzija.ocena,
            'idstu': recenzija.idstu,
            'idmnz': recenzija.idmnz
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Recenzija.objects.filter(opis='Test Opis', tekst='Test Tekst').exists())

    def test_post_invalid_data(self):
        recenzija = Recenzija.objects.create(opis='Test Opis', tekst='Test Tekst',
                                             datumvreme=datetime(2022, 1, 1, 10, 30, 0),
                                             ocena=5, idstu=self.student, idmnz=self.menza)

        url = reverse('menza', kwargs={'naziv': '123'})
        url1 = reverse('menza_sort', kwargs={'menza': 'Test Menza', 'sortVal': '-datumvreme'})
        response = self.client.post('', {
            'url1': url,
            'url2': url1,
            'form_id': 'M',
            'users': 'testuser',
            'opis': recenzija.opis,
            'tekst': recenzija.tekst,
            'datumvreme': recenzija.datumvreme,
            'ocena': recenzija.ocena,
            'idstu': recenzija.idstu,
            'idmnz': recenzija.idmnz
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Recenzija.objects.filter(opis='Test Opis', tekst='Test Tekst').exists())


class OstavljanjeOdgovoraViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_superuser(username='testuser', password='testpassword')
        self.student_group = Group.objects.create(name='student')
        self.moderator_group = Group.objects.create(name='moderator')
        self.moderator_user = User.objects.create_superuser(username='testuser1', password='testpassword1')
        self.moderator_user.groups.add(self.moderator_group)
        self.student_user.groups.add(self.student_group)
        self.student_user.save()

        self.client.login(username='testuser', password='testpassword')

    def test_post_valid_data(self):
        korisnik = Korisnik.objects.filter(idkor=self.student_user).first()
        d = datetime(2023, 10, 9, 23, 55, 59, 342380)
        kategorija = Kategorija.objects.create(naziv='Kat')
        tema = Tema.objects.create(naziv='123', opis='123', idkat=kategorija)
        odgovor = Odgovor.objects.create(naslov='123', datumvreme=d, komentar='123', slika='', idtem=tema,
                                         idkor=korisnik)

        url = reverse('podforum', kwargs={'naziv': '123'})
        response = self.client.post(url, {
            'form_id': 'S',
            'users': 'testuser1',
            'naslov': odgovor.naslov,
            'datumvreme': odgovor.datumvreme,
            'komentar': odgovor.komentar,
            'slika': '',
            'idtem': odgovor.idtem.idtem,
            'idkor': odgovor.idkor.idkor.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Odgovor.objects.filter(naslov='123', datumvreme=d).exists())

    def test_post_invalid_data(self):
        korisnik = Korisnik.objects.filter(idkor=self.moderator_user).first()
        d = datetime(2023, 10, 9, 23, 55, 59, 342380)
        kategorija = Kategorija.objects.create(naziv='Kat')
        tema = Tema.objects.create(naziv='123', opis='123', idkat=kategorija)
        odgovor = Odgovor.objects.create(naslov='123', datumvreme=d, komentar='123', slika='', idtem=tema,
                                         idkor=korisnik)
        url = reverse('podforum', kwargs={'naziv': '123'})
        response = self.client.post(url, {
            'form_id': 'S',
            'users': 'testuser1',
            'naslov': odgovor.naslov,
            'datumvreme': odgovor.datumvreme,
            'komentar': odgovor.komentar,
            'slika': '',
            'idtem': odgovor.idtem.idtem,
            'idkor': odgovor.idkor.idkor.id
        })

        self.assertEqual(response.status_code, 200)


class RegistrationStudentFormTest(TestCase):
    def setUp(self):
        Verifikacionipin.objects.create(brojstudkartice='1234-5678-9012-3456', pin='12345678901234567890')

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Pera',
            'last_name': 'Perić',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'address': 'Test Address',
            'birthdate': '2000-01-01',
            'telnum': '+381601234567',
            'cardNumber': '1234-5678-9012-3456',
            'PIN': '12345678901234567890'
        }
        form = RegistrationStudentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'username': 'testuser',
            'first_name': 'Pera',
            'last_name': 'Perić',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'address': 'Test Address',
            'birthdate': '2000-01-01',
            'telnum': '*381601234567',
            'cardNumber': '1234-5678-9012-3456',
            'PIN': '11111111111111111111'
        }
        form = RegistrationStudentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Podaci o kartici su nekorektni.', form.errors['__all__'])


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/login.html')

    def test_post_login_view_success(self):
        test_user = User.objects.create_user(username='testuser', password='password')
        group = Group.objects.create(name="administrator")
        test_user.groups.set([group])
        login_data = {'username': 'testuser', 'password': 'password'}
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/administrator/')

    def test_post_login_view_invalid_credentials(self):
        login_data = {'username': 'invaliduser', 'password': 'invalidpassword'}
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Nekorektni kredencijali.", response.context['form'].errors['__all__'])

    def test_post_login_view_blocked_user(self):
        test_user = User.objects.create_user(username='blockeduser', password='blockedpassword')
        test_user.is_active = False
        test_user.save()
        login_data = {'username': 'blockeduser', 'password': 'blockedpassword'}
        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Blokirani ste.", response.context['form'].errors['__all__'])

    def test_post_login_view_login_data_not_provided(self):
        response = self.client.post(reverse('login'), {})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Molimo Vas unesite korisničko ime/broj kartice i lozinku.",
                      response.context['form'].errors['__all__'])


class ProfilnaViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin_group = Group.objects.create(name='administrator')
        self.moderator_group = Group.objects.create(name='moderator')
        self.student_group = Group.objects.create(name='student')

    def test_profilna_view_admin(self):
        self.user.groups.add(self.admin_group)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profilna'))
        self.assertRedirects(response, '/administrator/', fetch_redirect_response=False)

    def test_profilna_view_moderator(self):
        self.user.groups.add(self.moderator_group)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profilna'))
        self.assertRedirects(response, '/moderator/', fetch_redirect_response=False)

    def test_profilna_view_student(self):
        self.user.groups.add(self.student_group)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profilna'))
        self.assertRedirects(response, '/student/', fetch_redirect_response=False)

    def test_profilna_view_not_logged_in(self):
        response = self.client.get(reverse('profilna'))
        self.assertRedirects(response, '/login/?next=/profilna/', fetch_redirect_response=False)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_logout(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homepage'))
        self.assertFalse('_auth_user_id' in self.client.session)


class RegistracijaViewTest(TestCase):
    def setUp(self):
        self.data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'first_name': 'testfirstname',
            'last_name': 'testlastname',
            'email': 'test@example.com',
            'address': 'testaddress',
            'cardNumber': '1234-5678-9012-3456',
            'PIN': '12345678901234567890'
        }

    def test_get_registration_page(self):
        response = self.client.get(reverse('registracija'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/registracija.html')

    def test_post_registration_form_success(self):
        Verifikacionipin.objects.create(pin='12345678901234567890', brojstudkartice='1234-5678-9012-3456')
        Group.objects.create(name="student")

        response = self.client.post(reverse('registracija'), self.data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertEqual(Student.objects.count(), 1)

    def test_post_registration_form_invalid_card_data(self):
        response = self.client.post(reverse('registracija'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Podaci o kartici su nekorektni.", response.context['form'].errors['__all__'])

    def test_post_registration_form_taken_card(self):
        verpin = Verifikacionipin.objects.create(pin='12345678901234567890', brojstudkartice='1234-5678-9012-3456')
        User.objects.create_user(username='anotheruser', password='anotherpassword')
        korisnik = Korisnik.objects.first()
        Student.objects.create(idstu=korisnik, stanjeracuna=2000, brojstudkartice=verpin)

        response = self.client.post(reverse('registracija'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Podaci o kartici su nekorektni.", response.context['form'].errors['__all__'])


class AdministratorViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.admin_group = Group.objects.create(name='administrator')
        self.user.groups.add(self.admin_group)

    def test_administrator_view_as_admin(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('administrator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bgadministrator')
        self.assertEqual(response.context['username'], 'testuser')
        self.assertTemplateUsed(response, 'studassist/administrator.html')

    def test_administrator_view_as_non_admin(self):
        self.client.login(username='testuser', password='password')
        self.user.groups.clear()
        response = self.client.get(reverse('administrator'))
        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response, HttpResponseForbidden)


class RegistracijaModeratoraViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='password')
        self.admin_group = Group.objects.create(name='administrator')
        self.admin_user.groups.add(self.admin_group)
        self.admin_user.save()

        meni = Meni.objects.create()
        self.menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                          slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                          radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')

        self.client.login(username='admin', password='password')

    def test_registracija_moderatora_view_get_as_admin(self):
        response = self.client.get(reverse('registracija_moderatora'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/registracija_moderatora.html')

    def test_registracija_moderatora_view_get_as_non_admin(self):
        self.admin_user.groups.clear()
        response = self.client.get(reverse('registracija_moderatora'))
        self.assertEqual(response.status_code, 403)
        self.assertIsInstance(response, HttpResponseForbidden)

    def test_registracija_moderatora_view_post_success(self):
        Group.objects.create(name="moderator")
        data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'first_name': 'testfirstname',
            'last_name': 'testlastname',
            'email': 'test@example.com',
            'address': 'Test Address',
            'birthdate': '1990-01-01',
            'telnum': '+381601234567',
            'canteen_name': 'Test Menza'
        }
        response = self.client.post(reverse('registracija_moderatora'), data, format='multipart')
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertRedirects(response, reverse('administrator'))
        self.assertEqual(Moderator.objects.count(), 1)

    def test_registracija_moderatora_view_post_invalid_form(self):
        data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'first_name': 'testfirstname',
            'last_name': 'testlastname',
            'email': 'test@example.com',
            'address': '',
            'canteen_name': ''
        }
        response = self.client.post(reverse('registracija_moderatora'), data)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        self.assertIn('address', form.errors)
        self.assertEqual(form.errors['address'], ['This field is required.'])


class BrisanjeStudentaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin', password='password')
        self.admin_group = Group.objects.create(name='administrator')
        self.admin_user.groups.add(self.admin_group)
        self.admin_user.save()

        self.client.login(username='admin', password='password')

    def test_get_request(self):
        response = self.client.get(reverse('brisanje_studenata'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/brisanje_studenata.html')

    def test_post_valid_data(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        korisnik = Korisnik.objects.filter(idkor=user).first()

        verpin = Verifikacionipin.objects.create(pin='12345678901234567890', brojstudkartice='1234-5678-9012-3456')
        student = Student.objects.create(idstu=korisnik, stanjeracuna=2000, brojstudkartice=verpin)

        response = self.client.post(reverse('brisanje_studenata'), {
            'form_id': 'S',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)

        student = User.objects.filter(username='testuser').first()
        self.assertFalse(student.is_active)

        response = self.client.post(reverse('brisanje_studenata'), {
            'form_id': 'D',
            'users': 'testuser'
        })
        self.assertRedirects(response, reverse('potvrdi_brisanje', args=('studenata', 'D', 'testuser')),
                             fetch_redirect_response=False)

        response = self.client.post(reverse('brisanje_studenata'), {
            'form_id': 'U',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)

        student = User.objects.filter(username='testuser').first()
        self.assertTrue(student.is_active)

    def test_post_invalid_data(self):
        response = self.client.post(reverse('brisanje_studenata'), {
            'form_id': 'S',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('brisanje_studenata'), {
            'form_id': 'D',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('brisanje_studenata'), {
            'form_id': 'U',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)


class BrisanjeModeratoraViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin', password='password')
        self.admin_group = Group.objects.create(name='administrator')
        self.admin_user.groups.add(self.admin_group)
        self.admin_user.save()

        self.client.login(username='admin', password='password')

    def test_get_request(self):
        response = self.client.get(reverse('brisanje_moderatora'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studassist/brisanje_moderatora.html')

    def test_post_valid_data(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        korisnik = Korisnik.objects.filter(idkor=user).first()

        meni = Meni.objects.create()
        menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                     slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                     radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')
        moderator = Moderator.objects.create(idmod=korisnik, idmnz=menza)

        response = self.client.post(reverse('brisanje_moderatora'), {
            'form_id': 'S',
            'users': 'testuser'
        })
        self.assertRedirects(response, reverse('potvrdi_brisanje', args=('moderatora', 'S', 'testuser')),
                             fetch_redirect_response=False)

        response = self.client.post(reverse('brisanje_moderatora'), {
            'form_id': 'D',
            'users': 'testuser'
        })
        self.assertRedirects(response, reverse('potvrdi_brisanje', args=('moderatora', 'D', 'testuser')),
                             fetch_redirect_response=False)

        user.is_active = False
        user.save()

        response = self.client.post(reverse('brisanje_moderatora'), {
            'form_id': 'U',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)

        moderator = User.objects.filter(username='testuser').first()
        self.assertTrue(moderator.is_active)

    def test_post_invalid_data(self):
        response = self.client.post(reverse('brisanje_moderatora'), {
            'form_id': 'S',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('brisanje_moderatora'), {
            'form_id': 'D',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('brisanje_moderatora'), {
            'form_id': 'U',
            'users': 'testuser'
        })
        self.assertEqual(response.status_code, 200)


class PotvrdiBrisanjeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='password')
        self.admin_group = Group.objects.create(name='administrator')
        self.admin_user.groups.add(self.admin_group)
        self.admin_user.save()

        self.client.login(username='admin', password='password')

        user = User.objects.create_user(username='testuser', password='testpassword')
        korisnik = Korisnik.objects.filter(idkor=user).first()

        meni = Meni.objects.create()
        menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                     slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                     radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')
        moderator = Moderator.objects.create(idmod=korisnik, idmnz=menza)

    def test_cancel_action(self):
        response = self.client.post(reverse('potvrdi_brisanje', args=('moderatora', 'S', 'testuser')),
                                    {'cancel': True})
        self.assertRedirects(response, reverse('brisanje_moderatora'))

    def test_confirm_moderator_suspension(self):
        response = self.client.post(reverse('potvrdi_brisanje', args=('moderatora', 'S', 'testuser')),
                                    {'confirm': True, 'password': 'password'})
        self.assertRedirects(response, reverse('brisanje_moderatora'))

        moderator = User.objects.get(username='testuser')
        self.assertFalse(moderator.is_active)

    def test_confirm_moderator_deletion(self):
        response = self.client.post(reverse('potvrdi_brisanje', args=('moderatora', 'D', 'testuser')),
                                    {'confirm': True, 'password': 'password'})
        self.assertRedirects(response, reverse('brisanje_moderatora'))

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='testuser')

    def test_confirm_student_deleteion(self):
        response = self.client.post(reverse('potvrdi_brisanje', args=('studenata', 'D', 'testuser')),
                                    {'confirm': True, 'password': 'password'})
        self.assertRedirects(response, reverse('brisanje_studenata'))

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='testuser')

    def test_incorrect_password(self):
        response = self.client.post(reverse('potvrdi_brisanje', args=('moderatora', 'S', 'testuser')),
                                    {'confirm': True, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pogrešna lozinka.")
