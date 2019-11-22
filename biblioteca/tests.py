from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from django.test.client import Client
from biblioteca.views import *
from django.contrib.auth.models import User


class TestUrls(SimpleTestCase):

    def test_index_url_is_resolves(self):
        url = reverse('index')
        self.assertEqual(resolve(url).func, index)

    def test_accesso_url_is_resolves(self):
        url = reverse('Accesso')
        self.assertEqual(resolve(url).func, Accesso)

    def test_registrazione_url_is_resolves(self):
        url = reverse('Registrazione')
        self.assertEqual(resolve(url).func, Registrazione)

    def test_area_bibliotecari_url_is_resolves(self):
        url = reverse('Area_Bibliotecari')
        self.assertEqual(resolve(url).func, Area_Bibliotecari)

    def test_elenco_per_genere_url_is_resolves(self):
        url = reverse('generi', args=[1])
        self.assertEqual(resolve(url).func, libri_per_genere)

    def test_ricerca_url_is_resolves(self):
        url = reverse('ricerca')
        self.assertEqual(resolve(url).func, Ricerca)

    def test_risultati_ricerca_url_is_resolves(self):
        url = reverse('RisultatiRicerca')
        self.assertEqual(resolve(url).func, RisultatiRicerca)

    def test_scheda_libro_url_is_resolves(self):
        url = reverse('SchedaLibro', args=[8820357534])
        self.assertEqual(resolve(url).func, SchedaLibro)

    def test_form_recensioni_url_is_resolves(self):
        url = reverse('recensione')
        self.assertEqual(resolve(url).func, formRecensions)

    def test_logout_url_is_resolves(self):
        url = reverse('Logout')
        self.assertEqual(resolve(url).func, logout_view)

    def test_prenotazione_url_is_resolves(self):
        url = reverse('Prenotazione')
        self.assertEqual(resolve(url).func, prenotazione)

    def test_restituzione_url_is_resolves(self):
        url = reverse('Restituzione')
        self.assertEqual(resolve(url).func, restituzione_libro)

    def test_annulla_attesa_url_is_resolves(self):
        url = reverse('AnnullaAttesa')
        self.assertEqual(resolve(url).func, annulla_attesa)

    def test_estendi_prestito_url_is_resolves(self):
        url = reverse('EstendiPrestito')
        self.assertEqual(resolve(url).func, estendi_prestito)

    def test_aggiungi_copia_url_is_resolves(self):
        url = reverse('AggiungiCopia')
        self.assertEqual(resolve(url).func, aggiungi_copia)

    def test_rimuovi_copia_url_is_resolves(self):
        url = reverse('RimuoviCopia')
        self.assertEqual(resolve(url).func, rimuovi_copia)

    def test_aggiungi_libro_url_is_resolves(self):
        url = reverse('AggiungiLibro')
        self.assertEqual(resolve(url).func, aggiungi_libro)

    def test_rimuovi_libro_url_is_resolves(self):
        url = reverse('RimuoviLibro')
        self.assertEqual(resolve(url).func, rimuovi_libro)


class BibliotecaViewsTestCase(TestCase):

    def setUp(self):
        self.clientLogged = Client()
        self.clientSuperuser = Client()
        self.clientUnlogged = Client()
        self.usrLogin = User.objects.create(username='user', password='user')
        self.usrDip = User.objects.create(username='super', password='super')
        self.usrDip.is_superuser = True
        self.clientLogged.login(username=self.usrLogin.username, password=self.usrLogin.password)
        self.clientSuperuser.login(username=self.usrDip.username, password=self.usrDip.password)
        self.url_risultati_ricerca = reverse('RisultatiRicerca')
        self.url_registrazione = reverse('Registrazione')
        self.url_ricerca = reverse('ricerca')

    def test_risultati_ricerca(self):
        response = self.clientSuperuser.get(self.url_risultati_ricerca)
        self.assertEqual(response.status_code, 200)

    def test_registrazione(self):
        resp = self.clientUnlogged.get(self.url_registrazione)
        self.assertEqual(resp.status_code, 200)

    def test_ricerca(self):
        respAnonimo = self.clientUnlogged.get(self.url_ricerca)
        self.assertEqual(respAnonimo.status_code, 200)

        respLogged = self.clientLogged.get(self.url_ricerca)
        self.assertEqual(respLogged.status_code, 200)

        respDipendente = self.clientSuperuser.get(self.url_ricerca)
        self.assertEqual(respDipendente.status_code, 200)


class TestUser(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@test.test', password='12test34')

    def test_username(self):
        self.assertEqual(self.user.username, 'testuser')

    def test_email(self):
        self.assertEqual(self.user.email, 'testuser@test.test')


class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', password='user')
        self.libro = Libro.objects.create(
            ISBN10=1234567897,
            Titolo_Libro='testing',
            Genere='horror',
            Numero_Copie=5,
            NumeroPagine=50,
            Durata_Prestito=30
        )

        self.recensione = self.libro.recensione_set.create(
            Valutazione='5',
            Recensione='test',
            Utente='user'
        )

    def test_aggiunta_recensione(self):
        self.assertEqual(self.recensione.ISBN10.Titolo_Libro, 'testing')

    def test_aggiunta_libro(self):
        self.assertEqual(self.libro.ISBN10, 1234567897)

