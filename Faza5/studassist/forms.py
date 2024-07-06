# Andrej Ačković 0263/2021
# Ema Paunović 0028/2021
# Jelena Blagojević 0029/2021
# Zlatko Golubović 0089/2021
from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import password_validation
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import Menza, Verifikacionipin, Moderator

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label=('Ime'),
        max_length=20,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'autofocus': '',
                'required': ''
            }
        )
    )
    last_name = forms.CharField(
        label=('Prezime'),
        max_length=20,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'required': ''
            }
        )
    )
    email = forms.EmailField(
        label=('Email'),
        max_length=320,
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'required': ''
            }
        )
    )
    address = forms.CharField(
        label=('Adresa'),
        min_length=1,
        max_length=500,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': '',
                'autocomplete': 'off'
            }
        )
    )
    birthdate = forms.DateField(
        label=('Datum rođenja'),
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )
    telnum = PhoneNumberField(
        label=('Broj telefona'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'tel',
                'autocomplete': 'off'
            }
        )
    )
    username = forms.CharField(
        label='Korisničko ime',
        max_length=20,
        required=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'required': ''
            }
        )
    )
    password1 = forms.CharField(
        label=('Lozinka'),
        max_length=20,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'pattern': '(?=.*\\d)(?=.*[\\W_])(?=.*[a-z])(?=.*[A-Z]).{8,}',
                'title': 'Lozinka treba da ima najmanje 8 karaktera. Barem po jednu cifru, malo slovo, veliko slovo i '
                         'specijalni znak.',
                'required': ''
            }
        ),
        help_text=password_validation.password_validators_help_text_html()
    )
    password2 = forms.CharField(
        label=('Ponovljenja lozinka'),
        max_length=20,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': ''
            }
        ),
        help_text='Unesite ponovljenu lozinku.'
    )
    profile_picture = forms.ImageField(
        label=('Profilna slika'),
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'address', 'birthdate', 'telnum', 'profile_picture')


class RegistrationStudentForm(RegisterForm):
    cardNumber = forms.CharField(
        label=('Broj kartice'),
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'pattern': '(\\d{4}-){3}(\\d{4})',
                'title': 'Broj treba biti u formi XXXX-XXXX-XXXX-XXXX',
                'required': '',
                'autocomplete': 'off'
            }
        )
    )
    PIN = forms.CharField(
        label=('PIN'),
        min_length=20,
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': '',
                'autocomplete': 'off',
                'type': 'password'
            }
        )
    )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        cardNumber = cleaned_data.get('cardNumber', None)
        PIN = cleaned_data.get('PIN', None)

        if Verifikacionipin.objects.filter(brojstudkartice=cardNumber, pin=PIN, student=None).exists():
            return cleaned_data
        
        raise forms.ValidationError("Podaci o kartici su nekorektni.")

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'address', 'birthdate', 'telnum',
            'cardNumber', 'PIN')


class RegistrationModeratorForm(RegisterForm):
    # canteen_name = forms.CharField(
    #     label=('Naziv menze'),
    #     max_length=20,
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-control',
    #             'required': '',
    #             'autocomplete': 'off'
    #         }
    #     )
    # )

    canteen_name = forms.ChoiceField(
        label=('Naziv menze'),
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    # def clean_canteen_name(self):
    #     canteen_name = self.cleaned_data['canteen_name']
    #     if Menza.objects.filter(naziv=canteen_name).exists():
    #         return canteen_name
    #     raise forms.ValidationError("Menza ne postoji.")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        choices = kwargs.pop('choices', [])
        super(RegistrationModeratorForm, self).__init__(*args, **kwargs)
        self.fields['canteen_name'].choices = choices

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'address', 'birthdate', 'telnum',
            'canteen_name')


class UserSuspensionDeletion(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput())
    users = forms.ChoiceField(widget=forms.Select, label='Odaberi moderatora')

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        label = kwargs.pop('label', '')
        super(UserSuspensionDeletion, self).__init__(*args, **kwargs)
        self.fields['users'].choices = choices
        self.fields['users'].label = 'Odaberite ' + label

    class Meta:
        fields = ('form_id', 'users')


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=('Korisničko ime/Broj kartice'),
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'off',
                'required': '',
                'autofocus': ''
            }
        )
    )
    password = forms.CharField(
        label=('Lozinka'),
        max_length=20,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': ''
            }
        )
    )

    # card_number = forms.CharField(
    #     label=('Broj kartice (opciono umesto korisničkog imena)'),
    #     max_length=20,
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-control',
    #             'autocomplete': 'off'
    #         }
    #     ),
    #     required=False
    # )

    def clean(self):
        cleaned_data = self.cleaned_data
        username_or_card_number = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username_or_card_number and password:
            try:
                user = User.objects.get(username=username_or_card_number)
                if not user.is_active:
                    raise forms.ValidationError("Blokirani ste.")
                else:
                    pass
            except User.DoesNotExist:
                pass
            user = authenticate(request=self.request, username=username_or_card_number, password=password)
            if user is None:
                user = authenticate(request=self.request, card_number=username_or_card_number, password=password)
                
            if user is None:
                raise forms.ValidationError("Nekorektni kredencijali.")
            
            if not user.is_active:
                raise forms.ValidationError("Blokirani ste.")

            self.user_cache = user
        else:
            raise forms.ValidationError("Molimo Vas unesite korisničko ime/broj kartice i lozinku.")

        # print(cleaned_data)
        return cleaned_data

    class Meta:
        fields = ('username', 'password')


class UserPasswordForm(forms.Form):
    password = forms.CharField(
        label=('Lozinka'),
        max_length=20,
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta:
        fields = ('password')


class StudentTokenForm(forms.Form):
    submit = forms.CharField(widget=forms.HiddenInput(), initial='submit')


class StudentBuyMealForm(forms.Form):
    # submit = forms.CharField(widget=forms.HiddenInput(), initial='submit')
    form_id = forms.CharField(widget=forms.HiddenInput(), initial='form_id')


class StudentDepositMoneyForm(forms.Form):
    amount = forms.DecimalField(label='Količina novca', max_digits=8, decimal_places=2, required=True, initial=1000.00)


class StudentCardForm(forms.Form):
    id_kartice = forms.CharField(label='Broj studentske kartice', max_length=45)
    form_id = forms.CharField(widget=forms.HiddenInput())


class ModeratorMealForm(forms.Form):
    OPTIONS = [
        ('D', 'Doručak'),
        ('R', 'Ručak'),
        ('V', 'Večera'),
    ]
    tip = forms.ChoiceField(
        choices=OPTIONS,
        widget=forms.RadioSelect,
        label='Izaberi tip obroka'
    )
    form_id = forms.CharField(widget=forms.HiddenInput())


class ModeratorCloseRestaurant(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput())


class OdgovorForm(forms.Form):
    naslov = forms.CharField(label='Naslov', max_length=100)
    comment = forms.CharField(label='Komentar', max_length=1000)
    picture = forms.ImageField(label='Slika', required=False)

class RecenzijaForm(forms.Form):
    descr = forms.CharField(label= 'Opis', max_length=200)
    comment = forms.CharField(label= 'Komentar', max_length=500, required=False)
    rating = forms.IntegerField(label= 'Rejting')


class ModeratorAddMeal(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput())
    obroci = forms.ChoiceField(widget=forms.Select, label='Odaberi obrok')
    dan = forms.CharField(widget=forms.HiddenInput(), required=False)
    tip = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        super(ModeratorAddMeal, self).__init__(*args, **kwargs)
        self.fields['obroci'].choices = choices


class ModeratorChoiceForm(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput())
    MEAL_CHOICES = [
        ('D', 'Doručak'),
        ('R', 'Ručak'),
        ('V', 'Večera'),
    ]
    obroci = forms.ChoiceField(widget=forms.Select, choices=MEAL_CHOICES, label='Odaberi obrok')
    DAYS_OF_WEEK_CHOICES = [
        ('PON', 'Ponedeljak'),
        ('UTO', 'Utorak'),
        ('SRE', 'Sreda'),
        ('ČET', 'Četvrtak'),
        ('PET', 'Petak'),
        ('SUB', 'Subota'),
        ('NED', 'Nedelja'),
    ]

    dani = forms.ChoiceField(widget=forms.Select, choices=DAYS_OF_WEEK_CHOICES, label='Odaberi dan u nedelji')


class ModeratorRemoveMeal(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput())
    obroci = forms.ChoiceField(widget=forms.Select, label='Odaberi obrok')
    dan = forms.CharField(widget=forms.HiddenInput(), required=False)
    tip = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        super(ModeratorRemoveMeal, self).__init__(*args, **kwargs)
        self.fields['obroci'].choices = choices
