from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField


class CercaForm(forms.Form):
    cerca = forms.CharField(max_length=100)


class AccediForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class RegistratiForm(forms.Form):
    nome = forms.CharField(max_length=100)
    cognome = forms.CharField(max_length=100)
    email = forms.EmailField()
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class RecensioneForm(forms.Form):
    valutazione = forms.IntegerField(min_value=1, max_value=5)
    recensione = forms.CharField(max_length=5000)


class AccediBibliotecariForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class AggiungiLibroForm(forms.Form):
    GENERE_1 = 'horror'
    GENERE_2 = 'avventura'
    GENERE_3 = 'fantascienza'
    GENERE_4 = 'fantasy'
    GENERE_5 = 'giallo'
    GENERE_6 = 'comico'
    GENERE_7 = 'romantico'

    SCELTA1 = 30
    SCELTA2 = 60
    SCELTA3 = 90

    SCELTA_GENERI = (
        (GENERE_1, u"horror"),
        (GENERE_2, u"avventura"),
        (GENERE_3, u"fantascienza"),
        (GENERE_4, u"fantasy"),
        (GENERE_5, u"giallo"),
        (GENERE_6, u"comico"),
        (GENERE_7, u"romantico")
    )

    SCELTA_ESTENSIONE = (
        (SCELTA1, 30),
        (SCELTA2, 60),
        (SCELTA3, 90)
    )

    Autore = forms.CharField(max_length=100)
    Titolo_Libro = forms.CharField(max_length=100, label='Titolo del libro:')
    Descrizione = forms.CharField(max_length=10000, label='Descrizione:')
    Numero_Copie = forms.IntegerField(min_value=1, label='Numero_copie:')
    Casa_Editrice = forms.CharField(max_length=1000, label='Casa editrice:')
    NumeroPagine = forms.IntegerField(min_value=1, label='Numero di pagine:')
    ISBN10 = forms.IntegerField(min_value=10, label='Codice isbn UNIVOCO:')
    Genere = forms.ChoiceField(choices=SCELTA_GENERI, label='Genere:')
    image = forms.ImageField(label='Immagine di copertina:')
    Durata_Prestito = forms.IntegerField(min_value=1, label='Durata del prestito (numero di giorni):')
    Condizioni_Estensione = forms.ChoiceField(choices=SCELTA_ESTENSIONE, label='Giorni di estensione del prestito:')
