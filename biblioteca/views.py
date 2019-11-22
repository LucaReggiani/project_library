import random
import datetime
import re  # importo il modulo delle espressioni regolari
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from biblioteca.forms import *
from biblioteca.models import *
from django.conf import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth.decorators import login_required


books_found = []
codiceLibro = 0  # codice ISBN10 di un libro. Quando un utente vuole scrivere una recensione viene reindirizzato
# a un'altra pagina HTML e, quando questa viene ultimata e confermata, viene reindirizzato alla pagina
# precedente, per farlo devo tenere memorizzato il codice ISBN10 per usarlo come url.

notifiche = False


def send_email(utente, filtro, type):
    user = User.objects.get(username=utente)
    MY_ADDRESS = settings.EMAIL_HOST_USER
    PASSWORD = settings.EMAIL_HOST_PASSWORD
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)  # set up the SMTP server
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    if type == "avviso":
        message = "È disponibile il libro " + filtro.ISBN10.Titolo_Libro + " per cui sei in attesa, accedi e " \
                                                                           "prenotalo subito."

    elif type == "richiamo":
        message = "Scaduto il prestito di '" + filtro.Titolo_Libro + "', le raccomandiamo di restituire al più " \
                                                                     "presto il libro sopra citato per rispetto di " \
                                                                     "altri utenti che sono in attesa."

    else:
        message = "L'utente " + utente + " si è appena iscritto al sito! Di seguito i suoi dati:\n"
        message = message + "nome: " + user.first_name + ";\n"
        message = message + "cognome: " + user.last_name + ";\n"
        message = message + "email: " + user.email + ";\n"
        message = message + "username: " + user.username + ".\n"

    msg = MIMEMultipart()  # create a message

    # setup the parameters of the message
    msg['From'] = MY_ADDRESS
    if type == "avviso" or type == "richiamo":
        msg['To'] = user.email
    else:
        msg['To'] = filtro.email

    if type == "avviso":
        msg['Subject'] = "Libro disponibile!!"

    elif type == "richiamo":
        msg['Subject'] = "Prenotazione scaduta!!"

    else:
        msg['Subject'] = "Nuova iscrizione!!"

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # send the message via the server set up earlier.
    s.send_message(msg)
    del msg

    # Terminate the SMTP session and close the connection
    s.quit()


def inizializzazione_notifiche(user):
    global notifiche
    avvisi = Avvisi.objects.filter(Utente=user)  # oggetto di tipo Avviso allocato

    if (len(avvisi)) > 0:
        notifiche = True

    else:
        notifiche = False

    return avvisi, notifiche


def Ricerca(request):  # definizione della view contact
    if request.method == 'POST':  # If the form has been submitted...
        global books_found
        form = CercaForm(request.POST)
        # form bound ai dati contenuti nella richiesta POST
        if form.is_valid():  # Step di validazione dei dati
            search = form.cleaned_data['cerca']
            books_found = Libro.objects.filter(Titolo_Libro__icontains=search)
            return HttpResponseRedirect('/RisultatiRicerca/')  # Redirect after POST

    else:  # GET request: just visualize the form
        form = CercaForm()  # An unbound form
        if request.user.is_superuser:
            return render(request, 'ricerca_dipendente.html', {
                'form': form,
            })

        elif request.user.is_authenticated:

            avvisi, notifics = inizializzazione_notifiche(request.user)  # assegna le notifiche e segnala se ce ne sono
            num_libri_non_restituiti = len(avvisi)  # la uso per capire quante notifiche ho

            return render(request, 'ricercaLogin.html', {
                'form': form,
                'avvisi': avvisi,
                'notifics': notifics,
                'num_libri_non_restituiti': num_libri_non_restituiti
            })

        else:
            return render(request, 'ricerca.html', {
                'form': form,
            })


def RisultatiRicerca(request):
    qr = books_found
    if request.user.is_superuser:
        return render(request, 'risultati_ricerca_dipendenti.html', locals())

    elif request.user.is_authenticated:

        avvisi, notifics = inizializzazione_notifiche(request.user)  # assegna le notifiche e segnala se ce ne sono
        num_libri_non_restituiti = len(avvisi)

        return render(request, 'risultatiRicercaLogin.html', locals())

    else:
        return render(request, 'risultati_ricerca.html', locals())


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


def aggiungi_notifica(filtro, type, utente):  # type indica il tipo di notifica: richiamo a restituire o
    # avviso di disponibilità

    if type == "avviso":
        s = "È disponibile il libro " + filtro.ISBN10.Titolo_Libro + " per cui sei in attesa"
        filtro.ISBN10.avvisi_set.create(Descrizione=s, Utente=utente)
    else:
        s = "Scaduto il prestito di " + filtro.Titolo_Libro
        filtro.avvisi_set.create(Descrizione=s, Utente=utente)


def check_notifiche(utente):
    global notifiche
    libri_presi = Prestito.objects.filter(Utente=utente,
                                          Prenotato=True)  # libri prenotati da user
    libri_non_restituiti_totali = []
    vecchi_libri_non_restituiti = []
    for i in libri_presi:
        date_str = i.DataRestituzione
        format_str = '%d/%m/%Y'  # The format
        data_restituzione = datetime.datetime.strptime(date_str,
                                                       format_str)  # converte la data di restituzione da
        # stringa a oggetto datatime.datatime
        if data_restituzione < datetime.datetime.today():
            libri_non_restituiti_totali.append(i.ISBN10)  # lista dei libri scaduti

    notifics = Avvisi.objects.filter(Utente=utente)
    for i in notifics:
        vecchi_libri_non_restituiti.append(i.ISBN10)

    nuovi_libri_non_restituiti = set(libri_non_restituiti_totali) - set(vecchi_libri_non_restituiti)

    for i in nuovi_libri_non_restituiti:
        aggiungi_notifica(i, "richiamo", utente)
        send_email(utente, i, "richiamo")


def aggiungi_libro(request):
    global errori_aggiunta_libro
    if request.method == 'POST':  # If the form has been submitted...
        formAggiungiLibro = AggiungiLibroForm(request.POST, request.FILES)
        # form bound ai dati contenuti nella richiesta POST
        if formAggiungiLibro.is_valid():  # Step di validazione dei dati
            Autore = formAggiungiLibro.cleaned_data['Autore']
            Titolo_Libro = formAggiungiLibro.cleaned_data['Titolo_Libro']
            Descrizione = formAggiungiLibro.cleaned_data['Descrizione']
            Numero_Copie = formAggiungiLibro.cleaned_data['Numero_Copie']
            Casa_Editrice = formAggiungiLibro.cleaned_data['Casa_Editrice']
            NumeroPagine = formAggiungiLibro.cleaned_data['NumeroPagine']
            ISBN10 = formAggiungiLibro.cleaned_data['ISBN10']
            Genere = formAggiungiLibro.cleaned_data['Genere']
            image = formAggiungiLibro.cleaned_data['image']
            image = '/copertina libri/' + str(image)
            Durata_Prestito = formAggiungiLibro.cleaned_data['Durata_Prestito']
            Condizioni_Estensione = "È possibile estendere il prestito per altri "\
                                    + str(formAggiungiLibro.cleaned_data['Condizioni_Estensione']) + " giorni"
            try:
                libro = Libro.objects.create(Autore=Autore, Titolo_Libro=Titolo_Libro, Descrizione=Descrizione,
                                             Numero_Copie=Numero_Copie, Casa_Editrice=Casa_Editrice,
                                             NumeroPagine=NumeroPagine,
                                             ISBN10=ISBN10, Genere=Genere, image=image, Durata_Prestito=Durata_Prestito,
                                             Condizioni_Estensione=Condizioni_Estensione)
            except IntegrityError as IE:
                return render(request, 'aggiungi_libri_fallimento.html', {
                    'formAggiungiLibro': formAggiungiLibro
                })
            else:
                libro.save()
            return HttpResponseRedirect('/')  # Redirect after POST
        else:
            return render(request, 'aggiungi_libri.html', {
                'formAggiungiLibro': formAggiungiLibro
            })
    else:  # GET request: just visualize the form
        formAggiungiLibro = AggiungiLibroForm()  # An unbound form
        return render(request, 'aggiungi_libri.html', {
            'formAggiungiLibro': formAggiungiLibro
        })


def index(request):
    if request.user.is_superuser:
        p = Prestito.objects.filter(Prenotato=True).values_list('ISBN10', flat=True).distinct()
        a = Prestito.objects.filter(Prenotato=False).values_list('ISBN10', flat=True).distinct()
        prestiti = []
        attese = []
        for i in p:
            prestiti.append(Libro.objects.get(pk=i))

        for i in a:
            attese.append(Libro.objects.get(pk=i))
        return render(request, 'index_dipendenti.html', locals())

    elif request.user.is_authenticated:

        # il seguente codice filtra i libri che verranno poi rappresentati in home
        booked = False
        wait = False

        avvisi, notifics = inizializzazione_notifiche(request.user)  # assegna le notifiche e segnala se ce ne sono
        num_libri_non_restituiti = len(avvisi)

        libri_presi = Prestito.objects.filter(Utente=request.user, Prenotato=True)  # libri prenotati da user
        waiting_list = Prestito.objects.filter(Utente=request.user, Prenotato=False)  # coda di attesa di user

        if len(libri_presi) > 0:
            booked = True

        if len(waiting_list) > 0:
            wait = True

        lista_libri = Libro.objects.all()
        libri_estratti = []
        while len(libri_estratti) < 12:
            num = random.randrange(0, len(lista_libri))  # estraggo un libro randomicamente
            if lista_libri[num] not in libri_estratti and \
                    lista_libri[num] not in libri_presi and \
                    lista_libri[num] not in waiting_list:  # se questo non è nella lista di librin attesa
                # o prenotati lo aggiunge in lista.

                libri_estratti.append(lista_libri[num])

        return render(request, 'index1.html', locals())
    else:
        lista_libri = Libro.objects.all()
        libri_estrapolati = []
        while len(libri_estrapolati) < 12:
            num = random.randrange(0, len(lista_libri))  # estraggo un libro randomicamente
            libri_estrapolati.append(lista_libri[num])
        return render(request, 'index.html', locals())


def kinds(num):  # metodo usato per implementare lo switch-case
    switcher = {
        1: 'avventura',
        2: 'comico',
        3: 'fantascienza',
        4: 'fantasy',
        5: 'giallo',
        6: 'horror',
        7: 'romantico'
    }
    return switcher.get(num, "ERRORE!!")


def libri_per_genere(request, num):
    kind = kinds(num)  # richiamo il metodo kinds, che restituisce una stringa (che è il genere selezionato)
    lista_libri = Libro.objects.filter(Genere=kind)  # tutti i libri del genere scelto sono messi in lista_libri
    if request.user.is_superuser:
        return render(request, 'elenco_generi_dipendenti.html', locals())
    elif request.user.is_authenticated:
        avvisi, notifics = inizializzazione_notifiche(request.user)  # assegna le notifiche e segnala se ce ne sono
        num_libri_non_restituiti = len(avvisi)
        return render(request, 'elenco_generiLogin.html', locals())

    else:
        return render(request, 'elenco_generi.html', locals())


@login_required(login_url='/Accedi/')
def formRecensions(request):
    if request.method == 'POST':  # If the form has been submitted...
        form_Recensione = RecensioneForm(request.POST)
        # form bound ai dati contenuti nella richiesta POST
        if form_Recensione.is_valid():  # Step di validazione dei dati
            valutazione = form_Recensione.cleaned_data['valutazione']
            recensione = form_Recensione.cleaned_data['recensione']

            filtro = Libro.objects.get(pk=codiceLibro)  # variabile che memorizza tutte le informazioni del
                                                        # libro appena recensito, filtrandolo per ISBN10
            filtro.recensione_set.create(Valutazione=valutazione, Recensione=recensione, Utente=request.user)
            return HttpResponseRedirect('/SchedaLibro/' + str(codiceLibro))  # Redirect after POST

    else:  # GET request: just visualize the form
        form_Recensione = RecensioneForm()  # An unbound form
        avvisi, notifics = inizializzazione_notifiche(request.user)  # assegna le notifiche e segnala se ce ne sono
        num_libri_non_restituiti = len(avvisi)
        return render(request, 'scrivi_recensioneLogin.html', {
            'form_Recensione': form_Recensione,
            'avvisi': avvisi,
            'notifics': notifics,
            'num_libri_non_restituiti': num_libri_non_restituiti
        })


@login_required(login_url='/Accedi/')
def prenotazione(request):
    filtro = Libro.objects.get(pk=codiceLibro)
    date_object = datetime.date.today()  # istanzio un oggetto di tipo data con la data di oggi
    limite = date_object + datetime.timedelta(
        days=filtro.Durata_Prestito)  # indica la data in cui va riconsegnato il libro
    if filtro.Numero_Copie > 0:
        nuovo_num_copie = filtro.Numero_Copie - 1
        Libro.objects.filter(ISBN10__exact=codiceLibro).update(Numero_Copie=nuovo_num_copie)
        if len(filtro.prestito_set.filter(Utente=request.user)) > 0:  # significa che l'utente è gia memorizzato
            # nel DB ed è in attesa
            filtro.prestito_set.filter(Utente=request.user).update(Prenotato=True,
                                                                   DataPrenotazione=date_object.strftime('%d/%m/%Y'),
                                                                   DataRestituzione=limite.strftime('%d/%m/%Y'))
        else:
            filtro.prestito_set.create(Utente=request.user, Prenotato=True,
                                       DataPrenotazione=date_object.strftime('%d/%m/%Y'),
                                       Estensione=False, DataRestituzione=limite.strftime('%d/%m/%Y'))

            # cancello dal DB le notifiche riguardo il libro disponibile SE ce ne sono
            notific = filtro.avvisi_set.filter(Descrizione__icontains="disponibile")
            notific.delete()

    else:
        filtro.prestito_set.create(Utente=request.user, Prenotato=False, Estensione=False)
    return HttpResponseRedirect('/SchedaLibro/' + str(codiceLibro))  # Redirect after POST


def restituzione_libro(request):
    global notifiche
    filtro = Libro.objects.get(pk=codiceLibro)
    # aggiorno il numero di copie disponibili nella tabella Libro e cancello la prenotazione dell'utente in Prestito
    nuovo_num_copie = filtro.Numero_Copie + 1
    Libro.objects.filter(ISBN10__exact=codiceLibro).update(Numero_Copie=nuovo_num_copie)
    c = filtro.prestito_set.filter(Utente=request.user)
    c.delete()

    # individuo tutti gli utenti in lista di attesa per il libro appena restituito e, se ce ne sono, a ognuno di loro
    # viene mandata una notifica (memorizzo questa cosa nella tabella Notifica del DB)
    tmp = filtro.prestito_set.filter(Prenotato=False)
    for i in tmp:
        aggiungi_notifica(i, "avviso", i.Utente)
        send_email(i.Utente, i, "avviso")

    # cancello dal DB le notifiche riguardo il prestito scaduto SE il libro appena restituito era scaduto
    notific = filtro.avvisi_set.filter(Descrizione__icontains="Scaduto", Utente=request.user)
    notific.delete()

    return HttpResponseRedirect('/SchedaLibro/' + str(codiceLibro))  # Redirect after POST


def annulla_attesa(request):
    filtro = Libro.objects.get(pk=codiceLibro)
    c = filtro.prestito_set.filter(Utente=request.user)
    c.delete()

    # cancello la notifica
    notific = filtro.avvisi_set.filter(Utente=request.user)
    notific.delete()
    return HttpResponseRedirect('/SchedaLibro/' + str(codiceLibro))  # Redirect after POST


def estendi_prestito(request):
    filtro = Libro.objects.get(pk=codiceLibro)
    num_giorni_estensione = re.findall('\d+', filtro.Condizioni_Estensione)
    num_giorni_estensione = num_giorni_estensione[0]
    prestito = filtro.prestito_set.filter(Utente=request.user)
    date_str = prestito[0].DataRestituzione
    format_str = '%d/%m/%Y'  # The format
    data_restituzione = datetime.datetime.strptime(date_str, format_str)
    data_restituzione = data_restituzione + datetime.timedelta(days=int(num_giorni_estensione))
    filtro.prestito_set.filter(Utente=request.user).update(Estensione=True,
                                                           DataRestituzione=data_restituzione.strftime('%d/%m/%Y'))

    return HttpResponseRedirect('/SchedaLibro/' + str(codiceLibro))  # Redirect after POST


def aggiungi_copia(request):  # aggiunge una copia del libro
    filtro = Libro.objects.get(pk=codiceLibro)
    nuovo_num_copie = filtro.Numero_Copie + 1
    Libro.objects.filter(ISBN10__exact=codiceLibro).update(Numero_Copie=nuovo_num_copie)

    # individuo tutti gli utenti in lista di attesa per il libro appena restituito e, se ce ne sono, a ognuno di loro
    # viene mandata una notifica (memorizzo questa cosa nella tabella Notifica del DB)

    tmp = filtro.prestito_set.filter(Prenotato=False)
    for i in tmp:
        f = filtro.avvisi_set.filter(Utente=i.Utente)  # estrapolo le notifiche di quell'utente per quel libro
        if len(f) == 0:  # significa che non gli è ancora arrivata la notifica
            aggiungi_notifica(i, "avviso", i.Utente)
            send_email(i.Utente, i, "avviso")

    return HttpResponseRedirect('/SchedaLibro/' + str(codiceLibro))


def rimuovi_copia(request):
    filtro = Libro.objects.get(pk=codiceLibro)
    nuovo_num_copie = filtro.Numero_Copie - 1
    Libro.objects.filter(ISBN10__exact=codiceLibro).update(Numero_Copie=nuovo_num_copie)

    if nuovo_num_copie == 0:
        # cancello dal DB le notifiche riguardo il prestito scaduto SE il libro appena restituito era scaduto
        notific = filtro.avvisi_set.filter(Descrizione__icontains="disponibile")
        notific.delete()

    return HttpResponseRedirect('/SchedaLibro/' + str(codiceLibro))


def rimuovi_libro(request):
    libro = Libro.objects.get(pk=codiceLibro)
    libro.delete()
    return HttpResponseRedirect('/')


def SchedaLibro(request, num):
    global codiceLibro
    try:
        libro = Libro.objects.get(pk=num)
    except ObjectDoesNotExist as NE:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    else:

        prestiti = Prestito.objects.filter(Utente=request.user)  # guardo se l'utente ha dei libri in prestito
        # o è in attesa di qualche libro.
        libri_presi = []
        for i in prestiti:
            if i.Prenotato:  # se il metodo ritorna True allora il libro in questione è prenotato, altrimenti
                # l'utente loggato è in attesa di quel libro

                libri_presi.append(i)

        libri_non_restituiti = []
        for i in libri_presi:
            date_str = i.DataRestituzione
            format_str = '%d/%m/%Y'  # The format
            data_restituzione = datetime.datetime.strptime(date_str, format_str)
            if data_restituzione < datetime.datetime.today():
                libri_non_restituiti.append(i)  # lista dei libri scaduti

        est = True  # variabile booleana che indica True se il prestito può essere esteso, False se il libro è scaduto

        for i in libri_non_restituiti:
            if libro == i.ISBN10:
                est = False

        codiceLibro = libro.ISBN10
        recensioni_libro = libro.recensione_set.all()  # filtro selezionando tutte le recensioni del libro interessato

        if request.user.is_superuser:
            lista_prenotati = libro.prestito_set.filter(Prenotato=True)
            lista_attesa = libro.prestito_set.filter(Prenotato=False)

            # controllo che sia possibile cancellare un libro: si può solo se nessuno ce l'ha in prestito o è in attesa
            num_libri_prenotati = len(libro.prestito_set.all())
            if num_libri_prenotati > 0:
                cancella = False

            else:
                cancella = True

            return render(request, 'scheda_libroDipendente.html', locals())

        elif request.user.is_authenticated:
            avvisi, notifics = inizializzazione_notifiche(request.user)  # assegna le notifiche e segnala se ce ne sono
            num_libri_non_restituiti = len(avvisi)

            if libro.Numero_Copie > 0:
                disponibile = 0  # variabile flag che mi memorizza lo stato della richiesta di prenotazione: 0 se c'è
                # almeno un libro disponibile, in tal caso si procede con la prenotazione, 1 nel
                # caso il libro non sia disponibile, in tal caso l'utente viene messo in lista di attesa.
            else:
                disponibile = 1

            try:
                dettagli_prenotazione = libro.prestito_set.get(
                    Utente=request.user)  # prenotazione del libro da parte dell'utente
            except ObjectDoesNotExist as NE:
                booked = False
                wait = False
            else:
                if not dettagli_prenotazione.Prenotato:
                    wait = True
                    booked = False
                else:
                    booked = True
                    wait = False

                if dettagli_prenotazione.Estensione:
                    esteso = 0

                else:
                    esteso = 1

            num_giorni_estensione = re.findall('\d+', libro.Condizioni_Estensione)
            num_giorni_estensione = num_giorni_estensione[0]

            return render(request, 'scheda_libroLogin.html', locals())

        else:
            return render(request, 'scheda_libro.html', locals())


def Accesso(request):
    if request.method == 'POST':  # If the form has been submitted...
        formAccedi = AccediForm(request.POST)
        # form bound ai dati contenuti nella richiesta POST
        if formAccedi.is_valid():  # Step di validazione dei dati
            username = formAccedi.cleaned_data['username']
            password = formAccedi.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:  # password verified for the user
                if user.is_superuser:
                    return HttpResponseRedirect('/Area_Bibliotecari/')  # Redirect after POST
                else:
                    if user.is_active:
                        login(request, user)

                        # controllo notifiche dell'utente ed eventuale aggiornamento del DB

                        check_notifiche(request.user)
            else:  # the authentication system was unable to verify
                return HttpResponseRedirect('/Accedi/')  # Redirect after POST

            return HttpResponseRedirect('/')  # Redirect after POST

    else:  # GET request: just visualize the form
        form_Accedi = AccediForm()  # An unbound form
        return render(request, 'accedi.html', {
            'form_Accedi': form_Accedi
        })


def Registrazione(request):
    if request.method == 'POST':  # If the form has been submitted...
        formRegistrati = RegistratiForm(request.POST)
        # form bound ai dati contenuti nella richiesta POST
        if formRegistrati.is_valid():  # Step di validazione dei dati
            nome = formRegistrati.cleaned_data['nome']
            cognome = formRegistrati.cleaned_data['cognome']
            email = formRegistrati.cleaned_data['email']
            username = formRegistrati.cleaned_data['username']
            password = formRegistrati.cleaned_data['password']
            for i in User.objects.all():
                if i.email == email:
                    form_Registrati = RegistratiForm()  # An unbound form
                    return render(request, 'registrati_email_ripetuta.html', {
                        'form_Registrati': form_Registrati
                    })
            try:
                user = User.objects.create_user(username=username, password=password, email=email,
                                                first_name=nome, last_name=cognome)
            except IntegrityError as IE:
                form_Registrati = RegistratiForm()  # An unbound form
                return render(request, 'registrati_username_ripetuto.html', {
                    'form_Registrati': form_Registrati
                })
            else:
                user.save()
            u = User.objects.filter(is_superuser=True)
            for i in u:
                send_email(user.username, i, "iscrizione")
            return HttpResponseRedirect('/')  # Redirect after POST
    else:  # GET request: just visualize the form
        form_Registrati = RegistratiForm()  # An unbound form
        return render(request, 'registrati.html', {
            'form_Registrati': form_Registrati
        })


def Area_Bibliotecari(request):
    if request.method == 'POST':  # If the form has been submitted...
        formAccedi = AccediForm(request.POST)
        # form bound ai dati contenuti nella richiesta POST
        if formAccedi.is_valid():  # Step di validazione dei dati
            username = formAccedi.cleaned_data['username']
            password = formAccedi.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:  # password verified for the user
                if user.is_superuser:
                    if user.is_active:
                        login(request, user)

                else:
                    return HttpResponseRedirect('/Accedi/')  # Redirect after POST
            else:  # the authentication system was unable to verify
                return HttpResponseRedirect('/Area_Bibliotecari/')  # Redirect after POST

            return HttpResponseRedirect('/')  # Redirect after POST

    else:  # GET request: just visualize the form
        form_accesso_bibliotecari = AccediBibliotecariForm()  # An unbound form
        return render(request, 'area_bibliotecari.html', {
            'form_accesso_bibliotecari': form_accesso_bibliotecari
        })
