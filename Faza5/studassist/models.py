# Ema Paunović 0028/2021
# Jelena Blagojević 0029/2021
# Andrej Ačković 0263/2021
# Zlatko Golubović 0089/2021
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Aktivnatabla(models.Model):
    """
    Stores information about active table, 
    related to :model:`studassist.Menza`.
    """
    idmnz = models.OneToOneField('Menza', on_delete=models.CASCADE, db_column='IdMnz', primary_key=True,
                                 help_text='canteen')
    aktivna = models.IntegerField(db_column='Aktivna', blank=True, null=True,
                                  help_text='is it active')
    tipobroka = models.CharField(max_length=1, db_column='TipObroka', blank=True, null=True,
                                 help_text='what type of meals are currently being served in canteen')

    class Meta:
        managed = True
        db_table = 'aktivnatabla'


class Kategorija(models.Model):
    """
    Stores categories of subjects on forum,
    related to :model:`studassist.Tema`.
    """
    idkat = models.AutoField(db_column='IdKat', primary_key=True)
    naziv = models.CharField(db_column='Naziv', max_length=100,
                             help_text='name')

    class Meta:
        managed = True
        db_table = 'kategorija'


class Korisnik(models.Model):
    """
    Stores information about registered users,
    related to :model:`auth.User` and :model:`studassist.Student`,
    :model:`studassist.Moderator`, :model:`studassist.Odgovor`.

    Birthdate and phone number are optional, the rest are mandatory.
    """
    idkor = models.OneToOneField(User, on_delete=models.CASCADE, db_column='IdKor', primary_key=True)
    profilnaslika = models.ImageField(db_column='ProfilnaSlika', upload_to='pfps/', default='pfps/profilna.png',
                                      help_text='profile picture')
    adresa = models.CharField(db_column='Adresa', max_length=500,
                              help_text='address')
    datumrodjenja = models.DateField(db_column='DatumRodjenja', blank=True, null=True,
                                     help_text='birthdate')
    brojtel = models.CharField(db_column='BrojTel', max_length=15, blank=True, null=True,
                               help_text='phone number')

    class Meta:
        managed = True
        db_table = 'korisnik'


@receiver(post_save, sender=User)
def create_korisnik_signal(sender, instance, created, **kwargs):
    """
    after creation of a new User, a new Korisnik related to the said User is created
    """
    if created:
        Korisnik.objects.create(idkor=instance)
    instance.korisnik.save()


class Meni(models.Model):
    """
    Stores information about menus,
    related to :model:`studassist.Menza` and :model:`studassist.Obrok`.
    """
    idmen = models.AutoField(db_column='IdMen', primary_key=True)

    class Meta:
        managed = True
        db_table = 'meni'


class Menza(models.Model):
    """
    Stores information about canteens, 
    related to :model:`studassist.Meni` and :model:`studassist.Moderator`,
    :model:`studassist.Aktivnatabla`, :model:`studassist.Recenzija`.

    Name is unique.
    """
    idmnz = models.AutoField(db_column='IdMnz', primary_key=True)
    naziv = models.CharField(db_column='Naziv', unique=True, max_length=20,
                             help_text='name')
    kapacitet = models.IntegerField(db_column='Kapacitet',
                                    help_text='capacity of students that the canteen can accommodate')
    adresa = models.CharField(db_column='Adresa', max_length=500,
                              help_text='address')
    slika = models.TextField(db_column='Slika',
                             help_text='picture')
    idmen = models.ForeignKey(Meni, on_delete=models.DO_NOTHING, db_column='IdMen',
                              help_text='menu')
    radnovremedor = models.CharField(db_column='RadnoVremeDor', max_length=11,
                                     help_text='breakfast working hours')
    radnovremeruc = models.CharField(db_column='RadnoVremeRuc', max_length=11,
                                     help_text='lunch working hours')
    radnovremevec = models.CharField(db_column='RadnoVremeVec', max_length=11,
                                     help_text='dinner working hours')
    link = models.CharField(db_column='Link', max_length=500,
                            help_text='information necessary for map api')

    class Meta:
        managed = True
        db_table = 'menza'


class Moderator(models.Model):
    """
    Stores information about moderators, 
    related to :model:`studassist.Korisnik` and :model:`studassist.Menza`.
    """
    idmod = models.OneToOneField(Korisnik, on_delete=models.CASCADE, db_column='IdMod', primary_key=True)
    idmnz = models.ForeignKey(Menza, on_delete=models.DO_NOTHING, db_column='IdMnz',
                              help_text='canteen assigned to the moderator')

    class Meta:
        managed = True
        db_table = 'moderator'


class Obrok(models.Model):
    """
    Stores information about meals,
    related to :model:`studassist.Obuhvatanje`.

    Name is unique.
    """
    idobr = models.AutoField(db_column='IdObr', primary_key=True)
    naziv = models.CharField(db_column='Naziv', unique=True, max_length=20,
                             help_text='name')

    class Meta:
        managed = True
        db_table = 'obrok'


class Obuhvatanje(models.Model):
    """
    Connects a meal to a menu for specific type of meal (breakfast, lunch, dinner)
    and weekday, 
    related to :model:`studassist.Meni`
    and :model:`studassist.Obrok`.

    Tuple idmen, idobr, weekday and type of meal is unique.
    """
    idobu = models.AutoField(db_column='IdObu', primary_key=True)
    idmen = models.ForeignKey(Meni, on_delete=models.CASCADE, db_column='IdMen',
                              help_text='menu')
    idobr = models.ForeignKey(Obrok, on_delete=models.CASCADE, db_column='IdObr',
                              help_text='meal')
    danunedelji = models.CharField(db_column='DanUNedelji', max_length=3,
                                   help_text='weekday')
    tip = models.CharField(db_column='Tip', max_length=1,
                           help_text='breakfast, lunch or dinner')

    class Meta:
        managed = True
        db_table = 'obuhvatanje'
        unique_together = (('idmen', 'idobr', 'danunedelji', 'tip'),)


class Odgovor(models.Model):
    """
    Stores information about student's replies,
    related to :model:`studassist.Tema` and :model:`studassist.Korisnik`.

    Picture is optional, the rest are mandatory.
    """
    idodg = models.AutoField(db_column='IdOdg', primary_key=True)
    naslov = models.CharField(db_column='Naslov', max_length=100,
                              help_text='title')
    datumvreme = models.DateTimeField(db_column='DatumVreme',
                                      help_text='datetime')
    komentar = models.CharField(db_column='Komentar', max_length=1000,
                                help_text='replie\'s content')
    slika = models.ImageField(db_column='Slika', upload_to='replies/', blank=True, null=True,
                              help_text='attached picture')
    idtem = models.ForeignKey('Tema', on_delete=models.CASCADE, db_column='IdTem',
                              help_text='subject')
    idkor = models.ForeignKey(Korisnik, on_delete=models.CASCADE, db_column='IdKor',
                              help_text='user')

    class Meta:
        managed = True
        db_table = 'odgovor'


class Recenzija(models.Model):
    """
    Stores information about canteen reviews left by students,
    related to :model:`studassist.Student` and :model:`studassist.Menza`.

    Pair idstu, idmnz is unique.
    Review text is optional, the rest are mandatory.
    """
    idrec = models.AutoField(db_column='IdRec', primary_key=True)
    opis = models.CharField(db_column='Opis', max_length=200,
                            help_text='student description')
    tekst = models.CharField(db_column='Tekst', max_length=500, blank=True, null=True,
                             help_text='review text')
    datumvreme = models.DateTimeField(db_column='DatumVreme',
                                      help_text='datetime')
    ocena = models.IntegerField(db_column='Ocena',
                                help_text='rating')
    idstu = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='IdStu',
                              help_text='student')
    idmnz = models.ForeignKey(Menza, on_delete=models.CASCADE, db_column='IdMnz',
                              help_text='canteen')

    class Meta:
        managed = True
        db_table = 'recenzija'
        unique_together = (('idstu', 'idmnz'),)


class Student(models.Model):
    """
    Stores information about students,
    related to :model:`studassist.Korisnik` and :model:`studassist.Verifikacionipin`,
    :model:`studassist.Recenzija`.
    """
    stanjeracuna = models.DecimalField(db_column='StanjeRacuna', max_digits=20, decimal_places=2,
                                       help_text='account balance')
    dorucak = models.IntegerField(db_column='Dorucak', default=0,
                                  help_text='number of breakfast coupons student owns')
    rucak = models.IntegerField(db_column='Rucak', default=0,
                                help_text='number of lunch coupons student owns')
    vecera = models.IntegerField(db_column='Vecera', default=0,
                                 help_text='number of dinner coupons student owns')
    zeton = models.IntegerField(db_column='Zeton', default=0,
                                help_text='number of chips student owns')
    idstu = models.OneToOneField(Korisnik, on_delete=models.CASCADE, db_column='IdStu', primary_key=True)
    brojstudkartice = models.OneToOneField('Verifikacionipin', on_delete=models.DO_NOTHING, db_column='BrojStudKartice',
                                           help_text='card number')

    class Meta:
        managed = True
        db_table = 'student'


class Tema(models.Model):
    """
    Stores information about subjects that represent subforums,
    related to :model:`studassist.Kategorija` and :model:`studassist.Odgovor`.
    """
    idtem = models.AutoField(db_column='IdTem', primary_key=True)
    naziv = models.CharField(db_column='Naziv', max_length=100,
                             help_text='name')
    opis = models.CharField(db_column='Opis', max_length=200,
                            help_text='description')
    idkat = models.ForeignKey(Kategorija, on_delete=models.CASCADE, db_column='IdKat',
                              help_text='category')

    class Meta:
        managed = True
        db_table = 'tema'


class Verifikacionipin(models.Model):
    """
    Stores information about canteen reviews left by students,
    related to :model:`studassist.Korisnik`.

    PIN is unique.
    """
    pin = models.CharField(db_column='PIN', unique=True, max_length=20,
                           help_text='PIN')
    brojstudkartice = models.CharField(db_column='BrojStudKartice', primary_key=True, max_length=20,
                                       help_text='student card number')

    class Meta:
        managed = True
        db_table = 'verifikacionipin'
