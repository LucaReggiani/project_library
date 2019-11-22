var flag = false;
var flagTendina = false;
function apriTendina(){
    if(flag==false) {
        document.getElementById('content').style.transition="all 0.5s";
        document.getElementById('content').style.marginLeft="-20px";
        document.getElementById('menu2').style.background="rgba(0,0,0,0.6)";
        flag = true;
    }
    else {
        document.getElementById('content').style.transition="all 0.5s";
        document.getElementById('content').style.marginLeft="-500px";
        document.getElementById('menu2').style.background="transparent";
        document.getElementById('menu2').style.opacity="1";
        flag = false;
    }
}

function cerca() {
  window.location.assign("http://127.0.0.1:8000/Ricerca");
}

function apriNotifiche() {
    if(flagTendina==false) {
        document.getElementById('notices').style.transition="all 0.5s";
        document.getElementById('notices').style.marginLeft="690px";
        document.getElementById('notifics').style.background="rgba(0,0,0,0.6)";
        flagTendina = true;
    }
    else {
        document.getElementById('notices').style.transition="all 0.5s";
        document.getElementById('notices').style.marginLeft="-500px";
        document.getElementById('notifics').style.background="transparent";
        document.getElementById('notifics').style.opacity="1";
        flagTendina = false;
    }
}

function scrivi() {
  window.location.assign("http://127.0.0.1:8000/scrivi_recensione");
}

function prendi(disponibile) {
    var domanda = confirm("Confermi di voler prenotare il libro?");
    if (domanda == true) {
        if(disponibile == 0) {
            alert('Libro prenotato!');
            window.location.assign("http://127.0.0.1:8000/PrenotazioneInCorso/");
        }
        else {
            var domanda2 = confirm("Libro non prenotato, non ci sono abbastanza copie disponibili. Verrai messo in lista di attesa, confermi?");
            if (domanda2 == true) {
                alert('Sei stato messo in lista di attesa!');
                window.location.assign("http://127.0.0.1:8000/PrenotazioneInCorso/");
            }
        }
    }
}

function rendi() {

    var domanda = confirm("Confermi di voler restituire il libro?");
    if (domanda == true) {

        alert('Libro restituito!');
        window.location.assign("http://127.0.0.1:8000/Restituzione/");
    }
}

function cancella() {

    var domanda = confirm("Confermi di voler cancellare la richiesta? Non sarai più in lista di attesa");
    if (domanda == true) {

        alert('Non sei più in coda!');
        window.location.assign("http://127.0.0.1:8000/AnnullaAttesa/");
    }
}

function estendi(estensione,  num) {

    var domanda = confirm("Confermando, prolungherai la durata del prestito, confermi?");
    if (domanda == true) {
        if (estensione == 0) {
            alert('Prestito non esteso! Non è possibile estendere lo stesso prestito più volte');
            window.location.assign("http://127.0.0.1:8000/SchedaLibro/"+ num.toString());
        }
        else {
            alert('Prestito esteso con successo!');
            window.location.assign("http://127.0.0.1:8000/EstendiPrestito/");
        }
    }
}

function registrati() {
  window.location.assign("http://127.0.0.1:8000/Registrati");
}

function aggiungiCopiaLibro() {
    window.location.assign("http://127.0.0.1:8000/AggiungiCopia");
}

function rimuoviCopiaLibro(num_copie, num) {
    if (num_copie <= 0) {
        alert("Impossibile ridurre le copie disponibili");
        window.location.assign("http://127.0.0.1:8000/SchedaLibro/"+ num.toString());
    }
    else {
        window.location.assign("http://127.0.0.1:8000/RimuoviCopia");
    }

}

function aggiungi_libro() {
    window.location.assign("http://127.0.0.1:8000/AggiungiLibro");
}

function rimuoviLibro (cancella, num){
    var domanda = confirm("Sicuro di voler cancellare questo libro? Gli utenti non potranno più prenotarlo");
    if (domanda == true) {
        if (cancella == false) {
            alert('Il libro è prenotato o ha utenti in attesa, aspetta che lo restituiscano e procedi');
            window.location.assign("http://127.0.0.1:8000/SchedaLibro/"+ num.toString());
        }
        else {
            alert('Libro rimosso con successo!');
            window.location.assign("http://127.0.0.1:8000/RimuoviLibro");
        }
    }
}

function rimuovi_libro() {
    window.location.assign("http://127.0.0.1:8000/Ricerca");
}