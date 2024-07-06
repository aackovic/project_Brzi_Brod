# Zlatko Golubović 0089/2021
from typing import Any
from django.core.management.base import CommandError, BaseCommand
from django.contrib.auth.models import Group, User
from studassist.models import *

from datetime import datetime, date


class Command(BaseCommand):
    help = "Create necessary groups and superuser using given arguments and superusers"

    def handle(self, *args: Any, **options: Any) -> str | None:
        group_administrator, created_administrator = Group.objects.get_or_create(name="administrator")
        group_moderator, created_moderator = Group.objects.get_or_create(name="moderator")
        group_student, created_student = Group.objects.get_or_create(name="student")

        profilna = ['bulbasaur', 'squirtle', 'pikachu', 'charmander']

        if not User.objects.filter(is_superuser=True).exists():
            users = []
            users.append(User.objects.create_superuser(username="jelena", password="123", first_name="Jelena", last_name="Blagojević"))
            users.append(User.objects.create_superuser(username="ema", password="123", first_name="Ema", last_name="Paunović"))
            users.append(User.objects.create_superuser(username="andrej", password="123", first_name="Andrej", last_name="Ačković"))
            users.append(User.objects.create_superuser(username="zlatko", password="123", first_name="Zlatko", last_name="Golubović"))

            for i in range(len(users)):
                users[i].groups.set([group_administrator])
                users[i].korisnik.profilnaslika = 'pfps/' + profilna[i] + '.png'
                users[i].korisnik.save()
        
        studenti = [
            {'ime': 'Pera', 'prezime': 'Perić', 'user': 'pera', 'pass': 'St1#1111', 'email': 'pera@gmail.com', 'birthdate': date(2002, 1, 3),
             'adresa': 'Avalska 10, Beograd', 'pfp': 'kuriboh', 'stanjeracuna': 5000, 'brojstudkartice': '5555-4444-6666-7777'},
            {'ime': 'Bukvalno', 'prezime': 'Ja', 'user': 'ja', 'pass': 'St2#1111', 'email': 'taj@.samcom', 'birthdate': date(2002, 6, 17), 'tel': '+381601234567',
             'adresa': 'Baba Višnjina 11, Beograd', 'pfp': 'tom', 'stanjeracuna': 7000, 'brojstudkartice': '7778-7778-8887-8887'} ]

        stu = None
        ludo = None
        ledje = None
        for student in studenti:
            ledje = user = User.objects.create_user(username=student['user'], password=student['pass'], first_name=student['ime'], last_name=student['prezime'], email=student['email'])
            if not ludo:
                ludo = ledje
            user.groups.set([group_student])
            user.korisnik.profilnaslika = 'pfps/' + student['pfp'] + '.png'
            if 'birthdate' in student:
                user.korisnik.datumrodjenja = student['birthdate']
            if 'tel' in student:
                user.korisnik.brojtel = student['tel']
            user.korisnik.adresa = student['adresa']
            user.korisnik.save()

            verpin = Verifikacionipin.objects.filter(brojstudkartice=student['brojstudkartice']).first()
            novi = Student.objects.create(idstu=user.korisnik, stanjeracuna=student['stanjeracuna'], brojstudkartice=verpin)
            if not stu:
                stu = novi

        menza = Menza.objects.filter(idmnz=1).first()
        moderator = {'ime': 'Mika', 'prezime': 'Mikić', 'user': 'mika', 'pass': 'Mo1#1111', 'email': 'mika@gmail.com', 'birthdate': date(1985, 3, 3), 'tel': '+381660124756',
                     'adresa': 'Avalska 12, Beograd', 'pfp': 'jerry', 'idmnz': menza}
        
        user = User.objects.create_user(username=moderator['user'], password=moderator['pass'], first_name=moderator['ime'], last_name=moderator['prezime'], email=moderator['email'])
        user.groups.set([group_moderator])
        user.korisnik.profilnaslika = 'pfps/' + moderator['pfp'] + '.png'
        user.korisnik.datumrodjenja = moderator['birthdate']
        user.korisnik.brojtel = moderator['tel']
        user.korisnik.adresa = moderator['adresa']
        user.korisnik.save()

        Moderator.objects.create(idmod=user.korisnik, idmnz=menza)

        Recenzija.objects.create(opis='Student 2. godine ETF-a', tekst='Izvanredno', ocena=5, datumvreme=datetime(2024, 6, 12, 7, 59, 59), idstu=stu, idmnz=menza)

        tema = Tema.objects.filter(idtem=6).first()
        Odgovor.objects.create(naslov='Značajna tema', komentar='Odnos cene i kvaliteta hrane je kompleksna tema koja utiče na mnoge aspekte života potrošača. Cena hrane može biti važan faktor prilikom donošenja odluka o kupovini, ali ne uvek i presudan. Kvalitet hrane, s druge strane, odnosi se na nutritivnu vrednost, svežinu, ukus i bezbednost proizvoda.'\
        'Ponekad se može uočiti da hrana nižeg kvaliteta ima nižu cenu, dok hrana višeg kvaliteta može biti skuplja. Međutim, ovo nije univerzalno pravilo, jer postoje mnogi faktori koji mogu uticati na cenu hrane, kao što su proizvodni proces, transport, marka proizvoda i tržišne tendencije.'\
        'Takođe, važno je uzeti u obzir i druge faktore osim cene i kvaliteta hrane, kao što su dostupnost, preferencije potrošača, zdravstvene potrebe i ekološki uticaji.'
        'U krajnjem slučaju, optimalan odnos između cene i kvaliteta hrane varira od osobe do osobe, a ključno je pronaći ravnotežu koja najbolje odgovara individualnim potrebama i prioritetima.', datumvreme=datetime(2024, 6, 12, 5, 14, 15), idtem=tema, idkor=ludo.korisnik)

        Odgovor.objects.create(naslov='...', komentar='Au brate', datumvreme=datetime(2024, 6, 12, 10, 0, 0), idtem=tema, idkor=ledje.korisnik, slika='replies/tom_face.png')
