from django.urls import path
from . import views


urlpatterns = [
    path('',  views.index, name='index'),
    path('Accedi/', views.Accesso, name='Accesso'),
    path('Registrati/', views.Registrazione, name='Registrazione'),
    path('Area_Bibliotecari/', views.Area_Bibliotecari, name='Area_Bibliotecari'),
    path('kind_of_books/<int:num>', views.libri_per_genere, name='generi'),
    path('Ricerca/', views.Ricerca, name='ricerca'),
    path('RisultatiRicerca/', views.RisultatiRicerca, name='RisultatiRicerca'),
    path('SchedaLibro/<int:num>', views.SchedaLibro, name='SchedaLibro'),
    path('scrivi_recensione/', views.formRecensions, name='recensione'),
    path('logout/', views.logout_view, name='Logout'),
    path('PrenotazioneInCorso/', views.prenotazione, name='Prenotazione'),
    path('Restituzione/', views.restituzione_libro, name='Restituzione'),
    path('AnnullaAttesa/', views.annulla_attesa, name='AnnullaAttesa'),
    path('EstendiPrestito/', views.estendi_prestito, name='EstendiPrestito'),
    path('AggiungiCopia/', views.aggiungi_copia, name='AggiungiCopia'),
    path('RimuoviCopia/', views.rimuovi_copia, name='RimuoviCopia'),
    path('AggiungiLibro/', views.aggiungi_libro, name='AggiungiLibro'),
    path('RimuoviLibro/', views.rimuovi_libro, name='RimuoviLibro'),
]