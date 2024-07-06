# Ema Paunović 0028/2021
# Jelena Blagojević 0029/2021
# Andrej Ačković 0263/2021
# Zlatko Golubović 0089/2021
from django.test import TestCase
from studassist.models import *
from django.db.utils import IntegrityError
from datetime import datetime


class AktivnaTablaModelTest(TestCase):
    def setUp(self):
        meni = Meni.objects.create()
        self.menza = Menza.objects.create(naziv='Test Menza', kapacitet=100, adresa='Test Address', slika='Test Image',
                                          idmen=meni, radnovremedor='08:00-10:00', radnovremeruc='12:00-14:00',
                                          radnovremevec='18:00-20:00', link='https://example.com')

    def test_model_creation(self):
        aktivnatabla = Aktivnatabla.objects.create(idmnz=self.menza, aktivna=1, tipobroka='D')

        self.assertIsNotNone(aktivnatabla)
        self.assertEqual(aktivnatabla.idmnz, self.menza)
        self.assertEqual(aktivnatabla.aktivna, 1)
        self.assertEqual(aktivnatabla.tipobroka, 'D')


class KategorijaModelTest(TestCase):
    def test_model_creation(self):
        kategorija = Kategorija.objects.create(naziv="Test Naziv")

        self.assertIsNotNone(kategorija)
        self.assertTrue(kategorija.idkat)
        self.assertEqual(kategorija.naziv, "Test Naziv")


class KorisnikModelTest(TestCase):
    def test_post_save_signal(self):
        self.assertEqual(Korisnik.objects.count(), 0)

        new_user = User.objects.create_user(username='newuser', email='new@example.com', password='newpassword')

        self.assertEqual(Korisnik.objects.count(), 1)
        korisnik = Korisnik.objects.first()
        self.assertEqual(korisnik.idkor, new_user)


class MeniModelTest(TestCase):
    def test_model_creation(self):
        meni = Meni.objects.create()

        self.assertIsNotNone(meni)
        self.assertTrue(meni.idmen)


class MenzaModelTest(TestCase):
    def setUp(self):
        self.meni = Meni.objects.create()

    def test_model_creation(self):
        menza = Menza.objects.create(naziv='Test Menza', kapacitet=100, adresa='Test Address', slika='Test Image',
                                     idmen=self.meni, radnovremedor='08:00-10:00', radnovremeruc='12:00-14:00',
                                     radnovremevec='18:00-20:00', link='https://example.com')

        self.assertIsNotNone(menza)
        self.assertTrue(menza.idmnz)
        self.assertEqual(menza.naziv, 'Test Menza')
        self.assertEqual(menza.kapacitet, 100)
        self.assertEqual(menza.adresa, 'Test Address')
        self.assertEqual(menza.slika, 'Test Image')
        self.assertEqual(menza.idmen, self.meni)
        self.assertEqual(menza.radnovremedor, '08:00-10:00')
        self.assertEqual(menza.radnovremeruc, '12:00-14:00')
        self.assertEqual(menza.radnovremevec, '18:00-20:00')
        self.assertEqual(menza.link, 'https://example.com')

    def test_naziv_unique(self):
        Menza.objects.create(naziv='Test Menza', kapacitet=100, adresa='Test Address', slika='Test Image',
                             idmen=self.meni, radnovremedor='08:00-10:00', radnovremeruc='12:00-14:00',
                             radnovremevec='18:00-20:00', link='https://example.com')

        with self.assertRaises(IntegrityError):
            Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address', slika='Another Image',
                                 idmen=self.meni, radnovremedor='08:00-10:00', radnovremeruc='12:00-14:00',
                                 radnovremevec='18:00-20:00', link='https://another-example.com')


class ModeratorModelTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.korisnik = Korisnik.objects.first()
        meni = Meni.objects.create()
        self.menza = Menza.objects.create(naziv='Test Menza', kapacitet=100, adresa='Test Address', slika='Test Image',
                                          idmen=meni, radnovremedor='08:00-10:00', radnovremeruc='12:00-14:00',
                                          radnovremevec='18:00-20:00', link='https://example.com')

    def test_model_creation(self):
        moderator = Moderator.objects.create(idmod=self.korisnik, idmnz=self.menza)

        self.assertIsNotNone(moderator)
        self.assertEqual(moderator.idmod, self.korisnik)
        self.assertEqual(moderator.idmnz, self.menza)


class ObrokModelTest(TestCase):
    def test_model_creation(self):
        obrok = Obrok.objects.create(naziv='Test Naziv')

        self.assertIsNotNone(obrok)
        self.assertTrue(obrok.idobr)
        self.assertEqual(obrok.naziv, 'Test Naziv')

    def test_unique_name(self):
        Obrok.objects.create(naziv='Test Naziv')

        with self.assertRaises(IntegrityError):
            Obrok.objects.create(naziv='Test Naziv')


class ObuhvatanjeModelTest(TestCase):
    def setUp(self):
        self.meni = Meni.objects.create()
        self.obrok = Obrok.objects.create(naziv='Test Obrok')

    def test_model_creation(self):
        obuhvatanje = Obuhvatanje.objects.create(idmen=self.meni, idobr=self.obrok, danunedelji='PON', tip='D')

        self.assertIsNotNone(obuhvatanje)
        self.assertTrue(obuhvatanje.idobu)
        self.assertEqual(obuhvatanje.idmen, self.meni)
        self.assertEqual(obuhvatanje.danunedelji, 'PON')
        self.assertEqual(obuhvatanje.tip, 'D')

    def test_unique_together_constraint(self):
        Obuhvatanje.objects.create(idmen=self.meni, idobr=self.obrok, danunedelji='PON', tip='D')

        with self.assertRaises(IntegrityError):
            Obuhvatanje.objects.create(idmen=self.meni, idobr=self.obrok, danunedelji='PON', tip='D')


class OdgovorModelTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.korisnik = Korisnik.objects.first()

        kategorija = Kategorija.objects.create(naziv="Test Naziv")
        self.tema = Tema.objects.create(naziv='Test Naziv', opis='Test Opis', idkat=kategorija)

    def test_model_creation(self):
        odgovor = Odgovor.objects.create(naslov='Test Naslov', datumvreme=datetime(2022, 1, 1, 10, 30, 0),
                                         komentar='Test Komentar', idtem=self.tema, idkor=self.korisnik)

        self.assertIsNotNone(odgovor)
        self.assertTrue(odgovor.idodg)
        self.assertEqual(odgovor.naslov, 'Test Naslov')
        self.assertEqual(odgovor.datumvreme, datetime(2022, 1, 1, 10, 30, 0))
        self.assertEqual(odgovor.komentar, 'Test Komentar')
        self.assertEqual(odgovor.idtem, self.tema)
        self.assertEqual(odgovor.idkor, self.korisnik)


class RecenzijaModelTest(TestCase):
    def setUp(self):
        meni = Meni.objects.create()
        self.menza = Menza.objects.create(naziv='Test Menza', kapacitet=50, adresa='Another Address',
                                          slika='Another Image', idmen=meni, radnovremedor='08:00-10:00',
                                          radnovremeruc='12:00-14:00', radnovremevec='18:00-20:00', link='')

        User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        korisnik = Korisnik.objects.first()
        verpin = Verifikacionipin.objects.create(brojstudkartice='1234-5678-9012-3456', pin='12345678901234567890')
        self.student = Student.objects.create(idstu=korisnik, stanjeracuna=2000, brojstudkartice=verpin)

    def test_model_creation(self):
        recenzija = Recenzija.objects.create(opis='Test Opis', tekst='Test Tekst',
                                             datumvreme=datetime(2022, 1, 1, 10, 30, 0),
                                             ocena=5, idstu=self.student, idmnz=self.menza)

        self.assertIsNotNone(recenzija)
        self.assertTrue(recenzija.idrec)
        self.assertEqual(recenzija.opis, 'Test Opis')
        self.assertEqual(recenzija.tekst, 'Test Tekst')
        self.assertEqual(recenzija.datumvreme, datetime(2022, 1, 1, 10, 30, 0))
        self.assertEqual(recenzija.ocena, 5)
        self.assertEqual(recenzija.idstu, self.student)
        self.assertEqual(recenzija.idmnz, self.menza)

    def test_unique_together_constraint(self):
        Recenzija.objects.create(opis='Test Opis', tekst='Test Tekst', datumvreme=datetime(2022, 1, 1, 10, 30, 0),
                                 ocena=5, idstu=self.student, idmnz=self.menza)

        with self.assertRaises(IntegrityError):
            Recenzija.objects.create(opis='Another Opis', tekst='Another Tekst',
                                     datumvreme=datetime(2022, 1, 1, 10, 30, 0),
                                     ocena=4, idstu=self.student, idmnz=self.menza)


class StudentModelTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.korisnik = Korisnik.objects.first()
        self.verpin = Verifikacionipin.objects.create(brojstudkartice='1234-5678-9012-3456', pin='12345678901234567890')

    def test_model_creation(self):
        student = Student.objects.create(idstu=self.korisnik, stanjeracuna=2000, brojstudkartice=self.verpin)

        self.assertIsNotNone(student)
        self.assertEqual(student.idstu, self.korisnik)
        self.assertEqual(student.stanjeracuna, 2000)
        self.assertEqual(student.brojstudkartice, self.verpin)


class TemaModelTest(TestCase):
    def setUp(self):
        self.kategorija = Kategorija.objects.create(naziv="Test Naziv")

    def test_model_creation(self):
        tema = Tema.objects.create(naziv='Test Naziv', opis='Test Opis', idkat=self.kategorija)

        self.assertIsNotNone(tema)
        self.assertTrue(tema.idtem)
        self.assertEqual(tema.naziv, 'Test Naziv')
        self.assertEqual(tema.opis, 'Test Opis')
        self.assertEqual(tema.idkat, self.kategorija)


class VerifikacionipinModelTest(TestCase):
    def test_model_creation(self):
        verpin = Verifikacionipin.objects.create(pin='12345678901234567890', brojstudkartice='1234-5678-9012-3456')

        self.assertIsNotNone(verpin)
        self.assertEqual(verpin.pin, '12345678901234567890')
        self.assertEqual(verpin.brojstudkartice, '1234-5678-9012-3456')

    def test_unique_pin(self):
        Verifikacionipin.objects.create(pin='12345678901234567890', brojstudkartice='1234-5678-9012-3456')

        with self.assertRaises(IntegrityError):
            Verifikacionipin.objects.create(pin='12345678901234567890', brojstudkartice='1234-5678-9012-3457')