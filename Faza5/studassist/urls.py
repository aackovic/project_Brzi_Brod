# Andrej Ačković 0263/2021
# Ema Paunović 0028/2021
# Jelena Blagojević 0029/2021
# Zlatko Golubović 0089/2021
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

"""
Andrej Ačković - urls set up
"""

urlpatterns = [
    path("", homepage, name="homepage"),
    path("login/", login, name="login"),
    path("profilna/", profilna, name="profilna"),
    path("logout/", logout, name="logout"),
    path("menze/", menze, name="menze"),
    path("forum/", forum, name="forum"),
    path("registracija/", registracija, name="registracija"),
    path("menza/<naziv>", menza, name="menza"),
    path("podforum/<naziv>", podforum, name="podforum"),
    path("administrator/", administrator, name="administrator"),
    path("registracija_moderatora/", registracija_moderatora, name="registracija_moderatora"),
    path("brisanje_studenata/", brisanje_studenata, name="brisanje_studenata"),
    path("brisanje_moderatora/", brisanje_moderatora, name="brisanje_moderatora"),
    path("potvrdi_brisanje/<str:vrsta>/<str:akcija>/<str:naziv>", potvrdi_brisanje, name="potvrdi_brisanje"),
    path("student/", student, name="student"),
    path("uplata/", uplata, name="uplata"),
    path("kupovina_bonova/", kupovina_bonova, name="kupovina_bonova"),
    path("moderator/", moderator, name="moderator"),
    path("moderator_promena_menija/", moderator_promena_menija, name="moderator_promena_menija"),
    path("hello/<name>", hello_there, name="hello_there"),
    path('payment/execute', execute_payment_view, name='execute_payment'),
    path('payment/cancel', cancel_payment_view, name='cancel_payment'),
    path('refresh/<name>', dohvatiStanje, name="refresh"),
    path('azuriraj_tablu', moderator_promena_table, name='azuriraj_tablu'),
    path('menza_sort/<menza>/<sortVal>', menzaSort, name='menza_sort')
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
