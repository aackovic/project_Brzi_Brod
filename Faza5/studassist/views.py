# Andrej Ačković 0263/2021
# Ema Paunović 0028/2021
# Jelena Blagojević 0029/2021
# Zlatko Golubović 0089/2021
import base64
import json
from datetime import datetime

import paypalrestsdk
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from redis import Redis

from web_project_brzi_brod import settings

from .forms import StudentTokenForm, StudentBuyMealForm, StudentDepositMoneyForm, ModeratorMealForm, StudentCardForm, \
    RegistrationStudentForm, LoginForm, RegistrationModeratorForm, ModeratorAddMeal, ModeratorChoiceForm, ModeratorRemoveMeal, \
    ModeratorCloseRestaurant, UserSuspensionDeletion, OdgovorForm, RecenzijaForm, UserPasswordForm
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from .models import *

from django.contrib.auth import authenticate, login as slogin, logout as slogout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


from .decorators import group_required

# Create your views here.
"""
Andrej Ačković - inital views set up
"""


def homepage(request):
    """
    Display a homepage.

    **Template:**

    :template:`studassist/index.html`
    """
    context = {
        'bgStyle': "bgorange"
    }
    return render(request, "studassist/index.html", context)


def login(request):
    """
    Display a login page. Handle login logic.

    **Context**

    ``User``
        :model:`auth.User`.

    **Template:**

    :template:`studassist/login.html`
    """
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            slogin(request, user)
            group = user.groups.all()[0]
            return redirect(str(group))
        else:
            # print(form.errors)
            pass
    else:
        form = LoginForm()
    context = {
        'bgStyle': "bglogin",
        'form': form
    }
    return render(request, "studassist/login.html", context)


@login_required
def profilna(request):
    """
    Display a profile page of a logged in user.

    **Templates:**

    ``Admin``
        :template:`studassist/administrator.html`
    ``Moderator``
        :template:`studassist/moderator.html`
    ``Student``
        :template:`studassist/student.html`
    """
    group = request.user.groups.all()[0]
    return redirect(str(group))


@login_required
def logout(request):
    """
    Display a homepage after successfully logging out a user.

    **Template:**

    :template:`studassist/index.html`
    """
    slogout(request)
    return redirect("homepage")


def menze(request):
    """
    Display a list of canteens.

    **Context**

    ``Menza``
        :model:`studassist.Menza`.

    **Template:**

    :template:`studassist/menze.html`
    """
    menze = []
    m = Menza.objects.all()
    for i in m:
        menza = dict()
        menza['naziv'] = i.naziv
        menza['slika'] = base64.b64encode(i.slika).decode('utf-8')
        menza['lokacija'] = i.link
        menza['adresa'] = i.adresa
        menze.append(menza)

    context = {
        'bgStyle': "bgorange",
        'menze': menze
    }
    return render(request, "studassist/menze.html", context)


def forum(request):
    """
    Display a forum.

    **Context**

    ``Kategorija``
        :model:`studassist.Kategorija`
    ``Tema``
        :model:`studassist.Tema`
    ``Odgovor``
        :model:`studassist.Odgovor`    
        
    **Template:**

    :template:`studassist/forum.html`
    """
    kats = Kategorija.objects.all()
    kategorije = []

    for kat in kats:
        kategorija = dict()
        kategorija['naziv'] = kat.naziv
        kategorija['teme'] = []
        for t in Tema.objects.filter(idkat=kat.idkat):
            tema = dict()
            tema['id'] = t.idtem
            tema['naziv'] = t.naziv
            tema['opis'] = t.opis
            tema['lastOdg'] = Odgovor.objects.filter(idtem=t.idtem).order_by("-datumvreme").first()
            tema['brOdg'] = Odgovor.objects.filter(idtem=t.idtem).count()

            if tema['lastOdg']:
                user = tema['lastOdg'].idkor.idkor
                tema['lastKorisnikTip'] = str(user.groups.all()[0])
                tema['lastKorisnikImePrezime'] = user.first_name
            else:
                tema['lastKorisnikTip'] = ""

            kategorija['teme'].append(tema)

        kategorije.append(kategorija)

    context = {
        'bgStyle': "bgorange",
        'kategorije': kategorije,
    }
    return render(request, "studassist/forum.html", context)


def registracija(request):
    """
    Display a registration page. Handle registration logic.
    After successful registration redirect to login page.

    **Context**

    ``User``
        :model:`auth.User`
    ``Korisnik``
        :model:`studassist.Korisnik`
    ``Student``
        :model:`studassist.Student`   

    **Templates:**

    ``Registration``
        :template:`studassist/registracija.html`
    ``Login``
        :template:`studassist/login.html`
    """
    if request.method == "POST":
        # print(request.FILES)
        form = RegistrationStudentForm(request.POST, request.FILES)
        if form.is_valid():
            # print("ALO")
            address = form.cleaned_data.get('address')
            birthdate = form.cleaned_data.get('birthdate')
            telnum = form.cleaned_data.get('telnum')
            pfp = form.cleaned_data.get('profile_picture')
            cardNumber = form.cleaned_data.get('cardNumber')
            PIN = form.cleaned_data.get('PIN')

            if telnum == '':
                telnum = None

            verpin = Verifikacionipin.objects.filter(brojstudkartice=cardNumber, pin=PIN, student=None).first()
            user = form.save()
            group = Group.objects.get(name="student")
            user.groups.set([group])
            user.refresh_from_db()

            korisnik = user.korisnik

            korisnik.adresa = address
            korisnik.datumrodjenja = birthdate
            korisnik.brojtel = telnum
            if pfp != '' and pfp:
                korisnik.profilnaslika = pfp

            korisnik.save()

            Student.objects.create(stanjeracuna=2000, idstu=korisnik, brojstudkartice=verpin)

            return redirect("login")
        else:
            # print(form.errors)
            # nesto ne valja u formi ispraviti
            messages.error(request, "Neuspešno registrovanje.")
            pass
    else:
        form = RegistrationStudentForm()
    context = {
        'bgStyle': "bglogin",
        'form': form
    }
    return render(request, "studassist/registracija.html", context)


def getRecenzije(sortVal, menza):
    """
    returns dictionary in which 'recenzije' represents list of all reviews sorted based on 'sortVal'
    and 'prosecnaOcena' represents average rating for canteen 'menza'
    """
    recs = Recenzija.objects.filter(idmnz=menza).all().order_by(sortVal)

    recenzije = []
    prosecnaOcena = 0.0

    for rec in recs:
        recenzija = dict()
        recenzija['opis'] = rec.opis
        if rec.tekst:
            recenzija['komentar'] = rec.tekst
        else:
            recenzija['komentar'] = ""
        recenzija['datum'] = rec.datumvreme
        recenzija['ocena'] = rec.ocena
        recenzija['korisnik'] = rec.idstu
        user = rec.idstu.idstu.idkor
        recenzija['imeprezime'] = user.first_name + " " + user.last_name
        prosecnaOcena += rec.ocena

        recenzija['ocene'] = []
        for i in range(5):
            if i < rec.ocena:
                recenzija['ocene'].append("checked")
            else:
                recenzija['ocene'].append("")

        recenzije.append(recenzija)

    if recs.count() != 0:
        prosecnaOcena = prosecnaOcena / recs.count()
    else:
        prosecnaOcena = 0.0

    recenzije = recenzije[0:5] or [[], [], [], [], []]

    if recenzije[0] == []:
        recenzije[0] = dict()
        recenzije[0]['imeprezime'] = "Trenutno ne postoji nijedna recenzija"
        recenzije = recenzije[0:1]

    recOcene = dict()
    recOcene['recenzije'] = recenzije
    recOcene['prosecnaOcena'] = prosecnaOcena

    return recOcene

def menzaSort(request, menza, sortVal):
    """
    Display a list of properly sorted reviews.

    **Context**

    ``Recenzija``
        :model:`studassist.Recenzija`

    **Template:**

    :template:`recenzije_snippet.html`
    """
    recenzije = getRecenzije(sortVal,menza)['recenzije']
    return JsonResponse({'html' : render_to_string('recenzije_snippet.html', {'recenzije' : recenzije})})

def menza(request, naziv):
    """
    Display a canteen page. Handle student leaving a review.

    **Context**

    ``Menza``
        :model:`studassist.Menza`
    ``Obuhvatanje``
        :model:`studassist.Obuhvatanje`
    ``Odgovor``
        :model:`studassist.Odgovor`
    ``Korisnik``
        :model:`studassist.Korisnik`
    ``Recenzija``
        :model:`studassist.Recenzija`

    **Template:**

    :template:`studassist/menza.html`
    """
    dani = ['PON', 'UTO', 'SRE', 'CET', 'PET', 'SUB', 'NED']
    if len(Menza.objects.filter(naziv=naziv).all()) > 0:
        menza = Menza.objects.filter(naziv=naziv).all()[0]
    else:
        context = {
            'bgStyle': "bgorange",
            'naziv': "Error",
            'radnoDorucak': "-",
            'radnoRucak': "-",
            'radnoVecera': "-",
            'obroci_dani': [],
        }
        return render(request, "studassist/menza.html", context)
    obroci = Obuhvatanje.objects.filter(idmen=menza.idmen)
    obroci_dorucak = obroci.filter(tip='D')
    obroci_rucak = obroci.filter(tip='R')
    obroci_vecera = obroci.filter(tip='V')
    obroci_dani = []
    for d in dani:
        dan = dict()
        dan['dan'] = d
        ids_d = obroci_dorucak.filter(danunedelji=d).values_list('idobr', flat=True)
        dan['dorucak'] = Obrok.objects.filter(idobr__in=ids_d).values_list('naziv', flat=True)
        ids_r = obroci_rucak.filter(danunedelji=d).values_list('idobr', flat=True)
        dan['rucak'] = Obrok.objects.filter(idobr__in=ids_r).values_list('naziv', flat=True)
        ids_v = obroci_vecera.filter(danunedelji=d).values_list('idobr', flat=True)
        dan['vecera'] = Obrok.objects.filter(idobr__in=ids_v).values_list('naziv', flat=True)
        obroci_dani.append(dan)

        # recenzije


    korisnik = Korisnik.objects.filter(idkor=request.user.id).first()
    # print(korisnik.idkor.id)

    cond = True
    if korisnik == None or str(korisnik.idkor.groups.all()[0]) != "student":
        # print("ALO")
        cond = False
    else:
        cond = not Recenzija.objects.filter(idmnz=menza, idstu=korisnik.student).exists()
        # print(cond)

    if (request.method == "POST"):
        form = RecenzijaForm(request.POST)
        if form.is_valid():
            if korisnik == None or str(korisnik.idkor.groups.all()[0]) != "student":
                messages.error(request, 'Greška - samo ulogovani studenti mogu ostavljati recenzije za menze.')
                return redirect('menza', naziv)
            recs = Recenzija.objects.filter(idmnz=menza).all()
            for rec in recs:
                if rec.idstu == korisnik.student:
                    messages.error(request, 'Greška - korisnik je vec ostavio recenziju.')
                    return redirect('menza', naziv)
            opisKom = form.cleaned_data.get('descr')
            ocena = form.cleaned_data.get('rating')
            komentar = form.cleaned_data.get('comment')
            if komentar == '':
                komentar = None
            vreme = datetime.now()
            novaRecenzija = Recenzija(opis = opisKom, tekst = komentar, datumvreme  = vreme, ocena = ocena, idstu = korisnik.student, idmnz = menza)
            novaRecenzija.save()
            cond = False
        # print(form)

    sortVal = "-datumvreme"
    recenzijeOcena = getRecenzije(sortVal, menza)

    recenzije = recenzijeOcena['recenzije']
    prosecnaOcena = recenzijeOcena['prosecnaOcena']

    context = {
        'bgStyle': "bgorange",
        'naziv': naziv,
        'radnoDorucak': menza.radnovremedor,
        'radnoRucak': menza.radnovremeruc,
        'radnoVecera': menza.radnovremevec,
        'obroci_dani': obroci_dani,
        'recenzije': recenzije,
        'prvaRecenzija': recenzije[0],
        'prosecnaOcena': prosecnaOcena,
        'stanje': aktivna_tabla(naziv),
        'lokacija': menza.link,
        'idMenze' : menza.idmnz,
        'cond': cond
    }
    return render(request, "studassist/menza.html", context)


def podforum(request, naziv):
    """
    Display a subforum. Handle user leaving a reply.

    **Context**

    ``Tema``
        :model:`studassist.Tema`
    ``Odgovor``
        :model:`studassist.Odgovor`
    ``Korisnik``
        :model:`studassist.Korisnik`
        
    **Template:**

    :template:`studassist/podforum.html`
    """
    tema = Tema.objects.filter(naziv=naziv).first()
    odgs = Odgovor.objects.filter(idtem=tema.idtem).order_by('-datumvreme').all()

    korisnik = Korisnik.objects.filter(idkor=request.user.id).first()

    if korisnik == None or str(korisnik.idkor.groups.all()[0]) != "student":
        cond = False
    else:
        cond = True

    if (request.method == "POST"):
        form = OdgovorForm(request.POST, request.FILES)
        if form.is_valid():
            if korisnik == None or str(korisnik.idkor.groups.all()[0]) != "student":
                messages.error(request, 'Greška - samo ulogovani studenti mogu ostavljati odgovore na forumima.')
                return redirect('podforum', naziv)
            naslov = form.cleaned_data.get('naslov')
            comment = form.cleaned_data.get('comment')
            # picture = request.FILES.get('picture')
            picture = form.cleaned_data.get('picture')
            vreme = datetime.now()
            noviOdgovor = Odgovor(naslov=naslov, datumvreme=vreme, komentar=comment, slika= picture, idtem=tema, idkor=korisnik)
            noviOdgovor.save()
        # print(form)

    odgovori = []
    for odg in odgs:
        odgovor = dict()
        odgovor['naslov'] = odg.naslov
        odgovor['datum'] = odg.datumvreme
        odgovor['sadrzaj'] = odg.komentar
        odgovor['slika'] = odg.slika
        user = odg.idkor.idkor
        odgovor['korisnikIme'] = user.first_name
        odgovor['korisnikTip'] = str(user.groups.all()[0])

        odgovori.append(odgovor)

    placeholder = ""
    if odgovori == []:
        placeholder = "Trenutno nema nijednog odgovora"

    odgovorForma = OdgovorForm()

    context = {
        'bgStyle': "bgorange",
        'nazivTeme': naziv,
        'odgovori': odgovori,
        'placeholder' : placeholder,
        'odgovorForma' : odgovorForma,
        'cond': cond
    }
    return render(request, "studassist/podforum.html", context)


@login_required
@group_required(groups=['administrator'])
def administrator(request):
    """
    Display an admin page.

    **Context**

    ``User``
        :model:`auth.User`

    **Template:**

    :template:`studassist/administrator.html`
    """
    user = request.user
    context = {
        'bgStyle': "bgadministrator",
        'username': user.username,
        'ime': user.first_name,
        'prezime': user.last_name,
        'img': user.korisnik.profilnaslika if user.korisnik.profilnaslika else ""
    }
    return render(request, "studassist/administrator.html", context)


@login_required
@group_required(groups=['administrator'])
def registracija_moderatora(request):
    """
    Display a moderator registration page. Handle registration logic.

    **Context**

    ``User``
        :model:`auth.User`
    ``Korisnik``
        :model:`studassist.Korisnik`
    ``Moderator``
        :model:`studassist.Moderator`
    ``Menza``
        :model:`studassist.Menza`

    **Templates:**

    ``Moderator registration``
        :template:`studassist/registracija_moderatora.html`
    ``Admin``
        :template:`studassist/administrator.html`
    """
    menze = Menza.objects.all()
    izbor = [(m.naziv, m.naziv) for m in menze]

    if request.method == "POST":
        form = RegistrationModeratorForm(request.POST, request.FILES, choices=izbor)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            birthdate = form.cleaned_data.get('birthdate')
            telnum = form.cleaned_data.get('telnum')
            canteen_name = form.cleaned_data.get('canteen_name')
            pfp = form.cleaned_data.get('profile_picture')

            if telnum == '':
                telnum = None

            canteen = Menza.objects.filter(naziv=canteen_name).first()
            user = form.save()
            group = Group.objects.get(name="moderator")
            user.groups.set([group])
            user.refresh_from_db()

            korisnik = user.korisnik
    
            korisnik.adresa = address
            korisnik.datumrodjenja = birthdate
            if pfp != "" and pfp:
                korisnik.profilnaslika = pfp
            korisnik.brojtel = telnum

            korisnik.save()

            Moderator.objects.create(idmod=korisnik, idmnz=canteen)

            # print("predji na glavnu admin. Uspeh")
            return redirect("administrator")
        else:
            # print(form.errors)
            # nesto ne valja u formi ispraviti
            messages.error(request, "Neuspešno registrovanje.")
            pass
    else:
        # print("tek sam doso")
        form = RegistrationModeratorForm(choices=izbor)
    context = {
        'bgStyle': "bgadministrator",
        'form': form
    }
    return render(request, "studassist/registracija_moderatora.html", context)


@login_required
@group_required(groups=['administrator'])
def brisanje_studenata(request):
    """
    Display a update student page. Handle suspension, deletion and activation logic.

    **Context**

    ``User``
        :model:`auth.User`

    **Template:**

    ``Student update``
        :template:`studassist/brisanje_studenata.html`
    ``Confirm update``
        :template:`studassist/potvrdi_brisanje.html`
    """
    if request.session.pop('D', False):
        messages.success(request, "Uspešno je obrisan student.")
    if request.session.pop('S', False):
        messages.success(request, "Uspešno je blokiran student.")
    studenti = Student.objects.all()
    izaberiS = [(s.idstu.idkor.username, s.idstu.idkor.username) for s in studenti if s.idstu.idkor.is_active]
    izaberiD = [(s.idstu.idkor.username, s.idstu.idkor.username) for s in studenti]
    izaberiU = [(s.idstu.idkor.username, s.idstu.idkor.username) for s in studenti if not s.idstu.idkor.is_active]

    if request.method == "POST":
        form_id = request.POST.get('form_id')
        if form_id == 'S':
            formS = UserSuspensionDeletion(request.POST, choices=izaberiS)
            if formS.is_valid():
                naziv_studenta = formS.cleaned_data.get('users')
                # print(naziv_studenta)
                student = User.objects.get(username=naziv_studenta)
                student.is_active = False
                student.save()
                izaberiS.remove((naziv_studenta, naziv_studenta))
                izaberiU.append((naziv_studenta, naziv_studenta))
                messages.success(request, "Uspešno je blokiran studentski nalog.")
            else:
                pass

        elif form_id == 'D':
            formD = UserSuspensionDeletion(request.POST, choices=izaberiD)
            if formD.is_valid():
                naziv_studenta = formD.cleaned_data.get('users')
                return redirect("potvrdi_brisanje", "studenata", "D", naziv_studenta)
            else:
                pass

        elif form_id == 'U':
            formU = UserSuspensionDeletion(request.POST, choices=izaberiU)
            if formU.is_valid():
                naziv_studenta = formU.cleaned_data.get('users')
                student = User.objects.get(username=naziv_studenta)
                student.is_active = True
                student.save()
                izaberiS.append((naziv_studenta, naziv_studenta))
                izaberiU.remove((naziv_studenta, naziv_studenta))
                messages.success(request, "Uspešno je aktiviran studentski nalog.")
            else:
                pass

    formS = UserSuspensionDeletion(initial={'form_id': 'S'}, choices=izaberiS, label='studenta')
    formD = UserSuspensionDeletion(initial={'form_id': 'D'}, choices=izaberiD, label='studenta')
    formU = UserSuspensionDeletion(initial={'form_id': 'U'}, choices=izaberiU, label='studenta')

    context = {
        'bgStyle': "bgadministrator",
        'formS': formS,
        'formD': formD,
        'formU': formU
    }
    return render(request, "studassist/brisanje_studenata.html", context)


@login_required
@group_required(groups=['administrator'])
def brisanje_moderatora(request):
    """
    Display a update moderator page. Handle suspension, deletion and activation logic.

    **Context**

    ``User``
        :model:`auth.User`

    **Template:**

    ``Moderator update``
        :template:`studassist/brisanje_moderatora.html`
    ``Confirm update``
        :template:`studassist/potvrdi_brisanje.html`
    """
    if request.session.pop('D', False):
        messages.success(request, "Uspešno je obrisan moderator.")
    if request.session.pop('S', False):
        messages.success(request, "Uspešno je blokiran moderator.")
    moderatori = Moderator.objects.all()
    izaberiS = [(m.idmod.idkor.username, m.idmod.idkor.username) for m in moderatori if m.idmod.idkor.is_active]
    izaberiD = [(m.idmod.idkor.username, m.idmod.idkor.username) for m in moderatori]
    izaberiU = [(m.idmod.idkor.username, m.idmod.idkor.username) for m in moderatori if not m.idmod.idkor.is_active]

    if request.method == "POST":
        form_id = request.POST.get('form_id')
        if form_id == 'S':
            formS = UserSuspensionDeletion(request.POST, choices=izaberiS)
            if formS.is_valid():
                naziv_moderatora = formS.cleaned_data.get('users')
                return redirect("potvrdi_brisanje", "moderatora", "S", naziv_moderatora)
            else:
                pass

        elif form_id == 'D':
            formD = UserSuspensionDeletion(request.POST, choices=izaberiD)
            if formD.is_valid():
                naziv_moderatora = formD.cleaned_data.get('users')
                return redirect("potvrdi_brisanje", "moderatora", "D", naziv_moderatora)
            else:
                pass

        elif form_id == 'U':
            formU = UserSuspensionDeletion(request.POST, choices=izaberiU)
            if formU.is_valid():
                naziv_moderatora = formU.cleaned_data.get('users')
                moderator = User.objects.get(username=naziv_moderatora)
                moderator.is_active = True
                moderator.save()
                izaberiS.append((naziv_moderatora, naziv_moderatora))
                izaberiU.remove((naziv_moderatora, naziv_moderatora))
                messages.success(request, "Uspešno je aktiviran moderator.")
            else:
                pass

    formS = UserSuspensionDeletion(initial={'form_id': 'S'}, choices=izaberiS, label='moderatora')
    formD = UserSuspensionDeletion(initial={'form_id': 'D'}, choices=izaberiD, label='moderatora')
    formU = UserSuspensionDeletion(initial={'form_id': 'U'}, choices=izaberiU, label='moderatora')

    context = {
        'bgStyle': "bgadministrator",
        'formS': formS,
        'formD': formD,
        'formU': formU
    }
    return render(request, "studassist/brisanje_moderatora.html", context)


@login_required
@group_required(groups=['administrator'])
def potvrdi_brisanje(request, vrsta, akcija, naziv):
    """
    Display a password confirmation page. Check password to confirm user update.

    **Context**

    ``User``
        :model:`auth.User`

    **Template:**

    ``Student update``
        :template:`studassist/brisanje_studenata.html`
    ``Moderator update``
        :template:`studassist/brisanje_moderatora.html`
    """
    # print(request.POST)
    if request.method == "POST":
        if "cancel" in request.POST:
            return redirect("brisanje_" + vrsta)
        elif "confirm" in request.POST:
            form = UserPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get('password')
                user = authenticate(username=request.user, password=password)
                if user is not None:
                    curuser = User.objects.get(username=naziv)
                    if akcija == "D":
                        curuser.delete()
                    elif akcija == "S":
                        curuser.is_active = False
                        curuser.save()
                    request.session[akcija] = True
                    return redirect("brisanje_" + vrsta)
                else:
                    messages.error(request, "Pogrešna lozinka.")
    else:
        form = UserPasswordForm()
    context = {
        'bgStyle': "bgadministrator",
        'form': form,
        'vrsta': vrsta
    }
    return render(request, "studassist/potvrdi_brisanje.html", context)


@login_required
@group_required(groups=['student'])
def student(request):
    """
    Display a student page. Handle chip purchase logic.

    **Context**

    ``User``
        :model:`auth.User`
    ``Korisnik``
        :model:`studassist.Korisnik`
    ``Student``
        :model:`studassist.Student`

    **Template:**

    :template:`studassist/student.html`
    """
    user = request.user
    korisnik = user.korisnik
    curstudent = korisnik.student
    context = {
        'bgStyle': "bgstudent",
        'username': user.username,
        'ime': user.first_name,
        'prezime': user.last_name,
        'email': user.email,
        'adresa': korisnik.adresa,
        'datumrodjenja': korisnik.datumrodjenja if korisnik.datumrodjenja else "-",
        'brtel': korisnik.brojtel if korisnik.brojtel else "-",
        'broj_kartice': curstudent.brojstudkartice.brojstudkartice,
        'stanje': curstudent.stanjeracuna,
        'dorucak': curstudent.dorucak,
        'rucak': curstudent.rucak,
        'vecera': curstudent.vecera,
        'zeton': curstudent.zeton,
        'img': korisnik.profilnaslika if korisnik.profilnaslika else ""
    }
    if request.method == "POST":
        form = StudentTokenForm(request.POST)
        if form.is_valid():
            if curstudent.stanjeracuna < 1000:
                messages.error(request, 'Nemate dovoljno novca!')
                return redirect('student')
            curstudent.zeton += 1
            curstudent.stanjeracuna -= 1000
            curstudent.save()
            messages.success(request, 'Žeton je uspešno kupljen')
            return redirect('student')
        else:
            messages.error(request, 'Greška - uneti podaci nisu validni.')
            context['form'] = form
            return redirect('student')
    else:
        form = StudentTokenForm()
        context['form'] = form
    return render(request, "studassist/student.html", context)


@login_required
@group_required(groups=['student'])
def kupovina_bonova(request):
    """
    Display a coupon purchase page. Handle coupon purchase logic.

    **Context**

    ``User``
        :model:`auth.User`
    ``Korisnik``
        :model:`studassist.Korisnik`
    ``Student``
        :model:`studassist.Student`

    **Template:**

    ``Coupon purchase``
        :template:`studassist/kupovina_bonova.html`
    ``Student``
        :template:`studassist/student.html`
    """
    user = request.user
    korisnik = user.korisnik
    curstudent = korisnik.student
    context = {
        'bgStyle': "bgstudent",
        'dorucak': curstudent.dorucak,
        'rucak': curstudent.rucak,
        'vecera': curstudent.vecera,
        'stanje': curstudent.stanjeracuna,
    }
    if request.method == "POST":
        form = StudentBuyMealForm(request.POST)
        if form.is_valid():
            obrok = form.cleaned_data['form_id']
            vrsta, kol = obrok.split('_')
            kol = int(kol)

            student = Student.objects.get(idstu=korisnik)

            if vrsta == 'd':
                if student.stanjeracuna < kol * 50:
                    messages.error(request, 'Nemate dovoljno novca!')
                    return redirect('kupovina_bonova')
                student.stanjeracuna -= kol * 50
                student.dorucak += kol
            elif vrsta == 'r':
                if student.stanjeracuna < kol * 120:
                    messages.error(request, 'Nemate dovoljno novca!')
                    return redirect('kupovina_bonova')
                student.stanjeracuna -= kol * 120
                student.rucak += kol
            elif vrsta == 'v':
                if student.stanjeracuna < kol * 90:
                    messages.error(request, 'Nemate dovoljno novca!')
                    return redirect('kupovina_bonova')
                student.stanjeracuna -= kol * 90
                student.vecera += kol
            student.save()
            messages.success(request, 'Obrok je kupljen')
            return redirect('student')
    elif request.method == "GET":
        form = StudentBuyMealForm(initial={'form_id': 'd_1'})
        context['d_1'] = form
        form1 = StudentBuyMealForm(initial={'form_id': 'r_1'})
        context['r_1'] = form1
        form2 = StudentBuyMealForm(initial={'form_id': 'v_1'})
        context['v_1'] = form2
        form3 = StudentBuyMealForm(initial={'form_id': 'd_5'})
        context['d_5'] = form3
        form4 = StudentBuyMealForm(initial={'form_id': 'r_5'})
        context['r_5'] = form4
        form5 = StudentBuyMealForm(initial={'form_id': 'v_5'})
        context['v_5'] = form5
        form6 = StudentBuyMealForm(initial={'form_id': 'd_10'})
        context['d_10'] = form6
        form7 = StudentBuyMealForm(initial={'form_id': 'r_10'})
        context['r_10'] = form7
        form8 = StudentBuyMealForm(initial={'form_id': 'v_10'})
        context['v_10'] = form8

    return render(request, "studassist/kupovina_bonova.html", context)


paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "AXgU3kDJpDTRqI3NOEx7UvQQ8Wtp0E9m5e7WKMQWGxtyXOFeQ-YEEKPrHSQKV0vosYsY-ORdNM-nRbh8",
    "client_secret": "EJO3W6s52TF2erConHbXfxu-qfcY7HkcufxU5Vm_f-f6WfIXx1h3L9ZyGf_Jqon7kdBrZptbEM4IPJfF"
})


def create_payment(amount, currency="USD"):
    """
    creates paypal-rest-sdk payment of given amount
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": currency
            },
            "description": "Test payment."
        }],
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment/execute",
            "cancel_url": "http://localhost:8000/payment/cancel"
        }
    })

    if payment.create():
        return payment
    else:
        return None


def create_payment_view(request):
    payment = create_payment(amount=0.1)

    if payment:
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        return JsonResponse({"error": "Payment creation failed"})


def execute_payment_view(request):
    """
    Handle execution payment logic.

    **Context**

    ``User``
        :model:`auth.User`
    ``Korisnik``
        :model:`studassist.Korisnik`
    ``Student``
        :model:`studassist.Student`

    **Template:**

    :template:`studassist/student.html`
    """
    user_id = request.session.get('user_id')
    # print(user_id)
    user = request.user
    korisnik = user.korisnik

    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        stud = korisnik.student
        stud.stanjeracuna += int(float(payment.transactions[0].amount.total) * 100)
        stud.save()
        messages.success(request, 'Uplata uspešno izvršena')
        return redirect('student')
    else:
        # print(payment.error)
        messages.error(request, 'Uplata neuspela')
        return redirect(student)


def cancel_payment_view(request):
    """
    Handle cancel payment logic.

    **Template:**

    :template:`studassist/student.html`
    """
    messages.error(request, 'Uplata otkazana')
    return redirect(student)


def uplata(request):
    """
    Displays payment page.

    **Context**

    ``User``
        :model:`auth.User`
    ``Korisnik``
        :model:`studassist.Korisnik`
    ``Student``
        :model:`studassist.Student`

    **Template:**

    :template:`studassist/uplata.html`
    """
    user = request.user
    korisnik = user.korisnik
    student = korisnik.student
    context = {
        'bgStyle': "bgstudent",
        'stanje': student.stanjeracuna,
    }
    if request.method == 'POST':
        form = StudentDepositMoneyForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            amount = amount / 100
            payment = create_payment(amount=amount)
            if payment:
                request.session['user_id'] = user.id
                # print(request.session['user_id'])
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = str(link.href)
                        return redirect(approval_url)
            else:
                form = StudentDepositMoneyForm()
                context['form'] = form
                messages.error(request, 'Neuspešno pravljenje uplate')
    else:
        form = StudentDepositMoneyForm()
        context['form'] = form
    return render(request, "studassist/uplata.html", context)


@login_required
@group_required(groups=['moderator'])
def moderator(request):
    """
    Display a moderator page.

    **Context**

    ``User``
        :model:`auth.User`
    ``Korisnik``
        :model:`studassist.Korisnik`
    ``Student``
        :model:`studassist.Student`
    ``Moderator``
        :model:`studassist.Moderator`
    ``Aktivnatabla``
        :model:`studassist.Aktivnatabla`

    **Template:**

    :template:`studassist/moderator.html`
    """
    user = request.user
    korisnik = user.korisnik
    modista = korisnik.moderator
    if request.method == "POST":
        form_id = request.POST.get('form_id')
        if form_id == 'formTip':
            form = ModeratorMealForm(request.POST)
            if form.is_valid():
                tip = form.cleaned_data['tip']
                tabla = Aktivnatabla.objects.get(idmnz=modista.idmnz)
                if tabla.aktivna == 1:
                    # greska - obrok aktivan
                    messages.error(request, 'Menza već radi')
                else:
                    tabla.aktivna = True
                    tabla.tipobroka = tip
                    tabla.save()
                    otvoriMenzuRedis(modista.idmnz.naziv, modista.idmnz.kapacitet)
                    messages.success(request, 'Obrok aktivan')
            else:
                # print(form.errors)
                # greska - nesto univerzalno
                messages.error(request, 'Nesto')
        elif form_id == 'formZatvori':
            tabla = Aktivnatabla.objects.get(idmnz=modista.idmnz)
            if tabla.aktivna == 1:
                tabla.aktivna = False
                tabla.save()
                zatvoriMenzuRedis(modista.idmnz.naziv)
            messages.success(request, 'Obrok zatvoren')
        else:
            form = StudentCardForm(request.POST)
            if form.is_valid():
                tabla = Aktivnatabla.objects.get(idmnz=modista.idmnz.idmnz)
                if tabla.aktivna is False:
                    # greska - nema aktivnog obroka
                    messages.error(request, 'Menza ne radi')
                id_kartice = form.cleaned_data['id_kartice']
                student = Student.objects.filter(brojstudkartice=id_kartice).first()
                if student is None:
                    messages.error(request, 'Nepostojeci student')
                    return redirect('moderator')
                if form_id == 'formUlaz':
                    zeton = student.zeton
                    # print(zeton)
                    if zeton == 0:
                        # nema zeton
                        messages.error(request, 'Student nema zeton')
                    else:
                        student.zeton = 0
                        student.save()
                        dodajStudentaRedis(modista.idmnz.naziv)
                        messages.success(request, 'Zeton skeniran!')
                elif form_id == 'formIzlaz':
                    student.zeton = 1
                    student.save()
                    smanjiStudentaRedis(modista.idmnz.naziv)
                    messages.success(request, 'Zeton skeniran!')
                else:
                    tabla = Aktivnatabla.objects.get(idmnz=modista.idmnz)
                    if tabla.aktivna is False:
                        # greska - nema aktivnog obroka
                        messages.error(request, 'Menza ne radi')
                    else:
                        tip_obroka = tabla.tipobroka
                        if tip_obroka == 'D':
                            br_bonova = student.dorucak
                            if br_bonova == 0:
                                # greska - nema bonove
                                messages.error(request, 'Student nema bon')
                            else:
                                student.dorucak -= 1
                                student.save()
                                messages.success(request, 'Bon skeniran!')
                        elif tip_obroka == 'R':
                            br_bonova = student.rucak
                            if br_bonova == 0:
                                # greska - nema bonove
                                messages.error(request, 'Student nema bon')
                            else:
                                student.dorucak -= 1
                                student.save()
                                messages.success(request, 'Bon skeniran!')
                        else:
                            br_bonova = student.vecera
                            if br_bonova == 0:
                                # greska - nema bonove
                                messages.error(request, 'Student nema bon')
                            else:
                                student.dorucak -= 1
                                student.save()
                                messages.success(request, 'Bon skeniran!')
            else:
                messages.error(request, "Greška - uneti podaci nisu validni.")
        return redirect('moderator')
    else:
        formTip = ModeratorMealForm(initial={'form_id': 'formTip'})
        formUlaz = StudentCardForm(initial={'form_id': 'formUlaz'})
        formIzlaz = StudentCardForm(initial={'form_id': 'formIzlaz'})
        formKupi = StudentCardForm(initial={'form_id': 'formKupi'})
        formZatvori = ModeratorCloseRestaurant(initial={'form_id': 'formZatvori'})
        context = {
            'bgStyle': "bgmoderator",
            'formTip': formTip,
            'formUlaz': formUlaz,
            'formIzlaz': formIzlaz,
            'formKupi': formKupi,
            'formZatvori': formZatvori,
            'ime': user.first_name,
            'prezime': user.last_name,
            'adresa': korisnik.adresa,
            'brtel': korisnik.brojtel if korisnik.brojtel else "-",
            'datumrodjenja': korisnik.datumrodjenja if korisnik.datumrodjenja else "-",
            'username': user.username,
            'email': user.email,
            'img': korisnik.profilnaslika if korisnik.profilnaslika else ""
        }
        return render(request, "studassist/moderator.html", context)


def otvoriMenzuRedis(naziv, kapacitet):
    """
    sets key (canteen name + _open) in Redis, this signifies that canteen is open
    """
    with Redis(host='localhost', port=6379) as r:
        key = naziv + "_open"
        key_number = naziv + "_cnt"
        key_kap = naziv + "_kapacitet"
        r.set(key, 1)
        r.setnx(key_number, 0)
        r.set(key_kap, kapacitet)


def zatvoriMenzuRedis(naziv):
    """
    deletes keys (canteen name + _open, canteen name + _cnt, canteen name + _kapacitet) from Redis,
    this signifies that canteen is closed
    """
    with Redis(host='localhost', port=6379) as r:
        key = naziv + "_open"
        key_number = naziv + "_cnt"
        key_kap = naziv + "_kapacitet"
        key_naziv = naziv +"_obroci"
        r.delete(key)
        r.delete(key_number)
        r.delete(key_kap)
        r.delete(key_naziv)


def dodajStudentaRedis(naziv):
    """
    increases value set by key (canteen name + _cnt), this value represents number of student in canteen
    """
    with Redis(host='localhost', port=6379) as r:
        key = naziv + "_cnt"
        r.incr(key)


def smanjiStudentaRedis(naziv):
    """
    decreases value set by key (canteen name + _cnt), this value represents number of students in canteen
    """
    with Redis(host='localhost', port=6379) as r:
        key = naziv + "_cnt"
        r.decr(key)


def dodajObrokRedis(naziv, obrok):
    """
    pushes 'obrok' to Redis list (canteen name + _obroci), this list represents all meals that are on active table 
    """
    with Redis(host='localhost', port=6379) as r:
        ime_lista = naziv + "_obroci"
        r.lpush(ime_lista, obrok)


def skiniObrokRedis(naziv, obrok):
    """
    pops 'obrok' from Redis list (canteen name + _obroci), this list represents all meals that are on active table
    """
    with Redis(host='localhost', port=6379) as r:
        ime_lista = naziv + "_obroci"
        lista = r.lrange(ime_lista, 0, -1)
        r.delete(ime_lista)
        for l in lista:
            l = l.decode('utf-8')
            if l == obrok:
                continue
            r.lpush(ime_lista, l)


def dohvatiObrokeRedis(naziv):
    """
    retrives list of decoded values from Redis list (canteen name + _obroci), this is list of all meals that are on active table
    """
    with Redis(host='localhost', port=6379) as r:
        ime_lista = naziv + "_obroci"
        lista = r.lrange(ime_lista, 0, -1)
        decoded_lista = [value.decode('utf-8') for value in lista]
        return decoded_lista


def aktivna_tabla(naziv):
    """
    retrives all necessary information about active table from Redis
    """
    stanje = {}
    with Redis(host='localhost', port=6379) as r:
        key = naziv + "_cnt"
        radi = r.get(key)
        if radi is None:
            stanje['radi'] = 'zatvoreno'
            stanje['broj_studenata'] = 0
            stanje['obroci'] = []
            stanje['progres'] = 0
            return stanje
        stanje['radi'] = 'otvoreno'
        stanje['broj_studenata'] = int(radi.decode('utf-8'))
        stanje['obroci'] = r.lrange(naziv + "_obroci", 0, -1)
        if stanje['obroci'] is None:
            stanje['obroci'] = []
        else:
            stanje['obroci'] = [cur.decode('utf-8') for cur in stanje['obroci']]
            if stanje['obroci'] is None:
                stanje['obroci'] = []
        kap_bytes = r.get(naziv + "_kapacitet")
        if kap_bytes is None:
            stanje['progres'] = 0
        else:
            kap = int(kap_bytes.decode('utf-8'))
            if kap != 0:
                stanje['progres'] = 100 * int(radi.decode('utf-8')) / kap
            else:
                stanje['progres'] = 0
        return stanje


def dohvatiStanje(request, name):
    """
    Handles active table display.

    **Template:**

    :template:`stanje_snippet.html`
    """
    stanje = aktivna_tabla(name)
    html = render_to_string('stanje_snippet.html', {'stanje': stanje})
    return JsonResponse({'html': html})


@login_required
@group_required(groups=['moderator'])
def moderator_promena_table(request):
    """
    Display active table update page. Handle update table logic.

    **Context**

    ``Obuhvatanje``
        :model:`studassist.Obuhvatanje`
    ``Obrok``
        :model:`studassist.Obrok`
    ``Moderator``
        :model:`studassist.Moderator`

    **Template:**

    :template:`studassist/moderator_azuriraj_tablu.html`
    """
    moderator = request.user.korisnik.moderator
    context = {
        'bgStyle': 'bgmoderator',
        'naziv': moderator.idmnz.naziv
    }
    obrociAT = dohvatiObrokeRedis(moderator.idmnz.naziv)
    obrociM = Obuhvatanje.objects.filter(idmen=moderator.idmnz.idmen).values_list('idobr', flat=True)
    obrociM = Obrok.objects.filter(idobr__in=obrociM)
    izaberiI = list((o.naziv, o.naziv) for o in obrociM if o.naziv not in obrociAT)
    # print(izaberiI)

    izaberiD = list((o, o) for o in obrociAT)
    # print(izaberiD)
    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        if form_id == 'form_dodaj_o':
            # print("ALOI")
            form = ModeratorAddMeal(request.POST, choices=izaberiI)
            if form.is_valid():
                naziv_obroka = form.cleaned_data['obroci']
                dodajObrokRedis(moderator.idmnz.naziv, naziv_obroka)
                izaberiI.remove((naziv_obroka, naziv_obroka))
                izaberiD.append((naziv_obroka, naziv_obroka))

        else:
            form = ModeratorRemoveMeal(request.POST, choices=izaberiD)
            if form.is_valid():
                naziv_obroka = form.cleaned_data['obroci']
                skiniObrokRedis(moderator.idmnz.naziv, naziv_obroka)
                izaberiI.append((naziv_obroka, naziv_obroka))
                izaberiD.remove((naziv_obroka, naziv_obroka))

    form_dodaj_obroci = ModeratorAddMeal(initial={'form_id': 'form_dodaj_o', 'dan': '', 'tip': ''}, choices=izaberiI)
    form_ukloni_obroci = ModeratorRemoveMeal(initial={'form_id': 'form_ukloni_o', 'dan': '', 'tip': ''},
                                                choices=izaberiD)
    context['formDodajO'] = form_dodaj_obroci
    context['formUkloniO'] = form_ukloni_obroci
    return render(request, "studassist/moderator_azuriraj_tablu.html", context)


@login_required
@group_required(groups=['moderator'])
def moderator_promena_menija(request):
    """
    Display menu update page. Handle update menu logic.

    **Context**

    ``Obuhvatanje``
        :model:`studassist.Obuhvatanje`
    ``Obrok``
        :model:`studassist.Obrok`
    ``Moderator``
        :model:`studassist.Moderator`

    **Template:**

    :template:`studassist/moderator_promena_menija.html`
    """
    moderator = request.user.korisnik.moderator
    form_dodaj = ModeratorChoiceForm(initial={'form_id': 'form_dodaj'})
    form_ukloni = ModeratorChoiceForm(initial={'form_id': 'form_ukloni'})

    context = {
        'formDodaj': form_dodaj,
        'formUkloni': form_ukloni,
        'bgStyle': 'bgmoderator',
        'naziv': moderator.idmnz.naziv
    }

    if request.method == "POST":
        form_id = request.POST.get('form_id')
        if form_id == 'form_dodaj':
            form = ModeratorChoiceForm(request.POST)
            if form.is_valid():
                dan = form.cleaned_data['dani']
                tip = form.cleaned_data['obroci']
                obroci = Obuhvatanje.objects.filter(danunedelji=dan, tip=tip,
                                                    idmen=moderator.idmnz.idmen).values_list('idobr', flat=True)
                obroci = Obrok.objects.exclude(idobr__in=obroci)
                obroci = list((o.idobr, o.naziv) for o in obroci)
                request.session['obrociI'] = obroci

                formDodaj = ModeratorAddMeal(initial={
                    'dan': dan,
                    'tip': tip,
                    'form_id': 'form_dodaj_o'
                }, choices=obroci)
                context['formDodajO'] = formDodaj

        elif form_id == 'form_ukloni':
            form = ModeratorChoiceForm(request.POST)
            if form.is_valid():
                dan = form.cleaned_data['dani']
                tip = form.cleaned_data['obroci']
                obroci = Obuhvatanje.objects.filter(danunedelji=dan, tip=tip,
                                                    idmen=moderator.idmnz.idmen).values_list('idobr', flat=True)
                obroci = Obrok.objects.filter(idobr__in=obroci)
                obroci = list((o.idobr, o.naziv) for o in obroci)
                request.session['obrociD'] = obroci

                formUkloni = ModeratorRemoveMeal(initial={
                    'dan': dan,
                    'tip': tip,
                    'form_id': 'form_ukloni_o'
                }, choices=obroci)
                context['formUkloniO'] = formUkloni

        elif form_id == 'form_dodaj_o':
            form = ModeratorAddMeal(request.POST, choices=request.session['obrociI'])
            # print(form.fields['obroci'].choices)
            if form.is_valid():
                dan = form.cleaned_data['dan']
                tip = form.cleaned_data['tip']
                id_obroka = form.cleaned_data['obroci']
                id_obroka = Obrok.objects.get(idobr=id_obroka)
                id_menija = moderator.idmnz.idmen
                obuhvatanje = Obuhvatanje(idmen=id_menija, danunedelji=dan, tip=tip, idobr=id_obroka)
                obuhvatanje.save()
        else:
            form = ModeratorRemoveMeal(request.POST, choices=request.session['obrociD'])
            if form.is_valid():
                dan = form.cleaned_data['dan']
                tip = form.cleaned_data['tip']
                id_obroka = form.cleaned_data['obroci']
                id_obroka = Obrok.objects.get(idobr=id_obroka)
                id_menija = moderator.idmnz.idmen
                obuhvatanje = Obuhvatanje.objects.filter(danunedelji=dan, tip=tip, idobr=id_obroka,
                                                         idmen=id_menija).first()
                if obuhvatanje is not None:
                    obuhvatanje.delete()
    else:
        
        form_ukloni_obroci = ModeratorRemoveMeal(initial={'form_id': 'form_ukloni_o', 'dan': '', 'tip': ''}, choices=[])
        form_dodaj_obroci = ModeratorAddMeal(initial={'form_id': 'form_dodaj_o', 'dan': '', 'tip': ''}, choices=[])

        context['formDodajO'] = form_dodaj_obroci
        context['formUkloniO'] = form_ukloni_obroci

    return render(request, "studassist/moderator_promena_menija.html", context)


def hello_there(request, name):
    """
    Display a hello there page.

    **Template:**

    :template:`studassist/hello_there.html`
    """
    # print(request.build_absolute_uri())  # optional
    return render(
        request,
        'studassist/hello_there.html',
        {
            'name': name,
            'date': datetime.now()
        }
    )
