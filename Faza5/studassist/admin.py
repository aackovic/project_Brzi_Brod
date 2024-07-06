# Andrej Ačković 0263/2021
from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Aktivnatabla)
admin.site.register(Kategorija)
admin.site.register(Korisnik)
admin.site.register(Meni)
admin.site.register(Menza)
admin.site.register(Moderator)
admin.site.register(Obrok)
admin.site.register(Obuhvatanje)
admin.site.register(Odgovor)
admin.site.register(Recenzija)
admin.site.register(Student)
admin.site.register(Tema)
admin.site.register(Verifikacionipin)