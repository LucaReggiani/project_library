from django.db import models


class Libro(models.Model):  # models di Libro
    Autore = models.CharField(max_length=50)
    Titolo_Libro = models.CharField(max_length=100, null=False)
    Descrizione = models.CharField(max_length=20)
    Numero_Copie = models.IntegerField(null=False)
    Casa_Editrice = models.CharField(max_length=20)
    NumeroPagine = models.IntegerField(null=False)
    ISBN10 = models.IntegerField(primary_key=True)
    Genere = models.CharField(max_length=20, null=False)
    image = models.CharField(max_length=100)
    Durata_Prestito = models.IntegerField(null=False)
    Condizioni_Estensione = models.CharField(max_length=1000)


class Recensione(models.Model):  # models di Recensioni
    ISBN10 = models.ForeignKey(Libro, on_delete=models.CASCADE)
    Valutazione = models.IntegerField(null=False)
    Recensione = models.CharField(max_length=5000)
    Utente = models.CharField(max_length=30)


class Prestito(models.Model):
    Utente = models.CharField(max_length=30)
    ISBN10 = models.ForeignKey(Libro, on_delete=models.CASCADE)
    Prenotato = models.BooleanField()  # flag booleano che è True se il libro è prenotato, altrimenti
                                       # l'utente è in lista di attesa

    DataPrenotazione = models.CharField(max_length=30)
    Estensione = models.BooleanField(default=False)  # True se la prenotazione è stata estesa, False altrimenti
    DataRestituzione = models.CharField(max_length=30, default='')


class Avvisi(models.Model):
    Descrizione = models.CharField(max_length=100)
    ISBN10 = models.ForeignKey(Libro, on_delete=models.CASCADE)
    Utente = models.CharField(max_length=30)
