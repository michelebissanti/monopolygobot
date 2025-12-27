# Documentazione Handlers - MonopolyGoBot

## Indice
1. [Panoramica Sistema](#panoramica-sistema)
2. [Handler Principali](#handler-principali)
   - [State Handler](#state-handler)
   - [Autoroll Handler](#autoroll-handler)
   - [Autoroller](#autoroller)
   - [Disable Autoroller](#disable-autoroller)
   - [Autoroll Monitor](#autoroll-monitor)
   - [Building Handler](#building-handler)
   - [Building Monitor](#building-monitor)
   - [Multiplier Handler](#multiplier-handler)
   - [Multiplier Monitor](#multiplier-monitor)
   - [UI Handler](#ui-handler)
   - [Bank Heist Handler](#bank-heist-handler)
   - [Shut Down Handler](#shut-down-handler)
   - [Idle Handler](#idle-handler)
   - [Destruction Handler](#destruction-handler)
3. [Sistema di Sincronizzazione](#sistema-di-sincronizzazione)
4. [Flusso di Esecuzione](#flusso-di-esecuzione)

---

## Panoramica Sistema

MonopolyGoBot è un bot automatizzato per il gioco Monopoly GO che utilizza un'architettura multi-threaded per gestire diverse attività simultaneamente. Il sistema si basa su:

- **OCR (Optical Character Recognition)**: Per rilevare elementi del gioco sullo schermo
- **Threading**: Per eseguire operazioni parallele
- **Shared State**: Per sincronizzare lo stato tra diversi thread
- **Conditions & Locks**: Per coordinare le azioni tra thread

---

## Handler Principali

### State Handler

**File**: `handlers/state_handler.py`

**Scopo**: Gestore centrale che coordina l'avvio e l'arresto di tutti gli altri handler.

**Funzionamento**:
- Funge da punto di ingresso per tutti gli handler
- Gestisce la creazione e il ciclo di vita dei thread per ogni handler
- Implementa il metodo `_toggle_handler()` generico per avviare/arrestare qualsiasi handler
- Fornisce metodi specifici per ogni handler (es. `toggle_autoroll_handler()`, `toggle_building_monitor()`)

**Metodi Principali**:
- `start_player_info()`: Avvia il thread per raccogliere informazioni sul giocatore
- `start_set_console_title()`: Avvia il thread per impostare il titolo della console
- `start_autoroll_handler()`: Inizializza l'autoroll handler
- `start_autoroll_monitor()`: Inizializza il monitor dell'autoroll
- `start_building_monitor()`: Inizializza il monitor degli edifici
- `start_multiplier_monitor()`: Inizializza il monitor del moltiplicatore
- `_toggle_handler()`: Metodo generico per avviare/arrestare handler

**Tasti di scelta rapida (definiti in main.py)**:
- `F1`: Toggle Autoroll Handler
- `F2`: Toggle Bank Heist Handler
- `F3`: Toggle Shut Down Handler
- `F4`: Toggle UI Handler
- `F5`: Toggle Building Monitor
- `F6`: Toggle Multiplier Monitor
- `F7`: Toggle Autoroll Monitor
- `F8`: Toggle Destruction Handler
- `Page Up`: Avvia tutti gli handler
- `F12`: Esci e salva la cache

---

### Autoroll Handler

**File**: `handlers/autoroll_handler.py`

**Scopo**: Gestisce il coordinamento tra l'autoroller e il disable_autoroller, controllando quando avviare/arrestare questi componenti.

**Funzionamento**:
- Mantiene lo stato di `autoroller_running` e `disable_autoroller_running`
- Coordina l'avvio e l'arresto dei thread autoroller e disable_autoroller
- Utilizza condition variables per sincronizzare le operazioni
- Notifica altri thread quando lo stato cambia

**Metodi Principali**:
- `initialize()`: Inizializza i flag di stato
- `set_autoroller_running(bool)`: Imposta lo stato dell'autoroller e notifica
- `set_disable_autoroller_running(bool)`: Imposta lo stato del disable_autoroller
- `start_autoroller()`: Avvia il thread autoroller
- `stop_autoroller()`: Ferma il thread autoroller
- `start_disable_autoroller()`: Avvia il thread disable_autoroller
- `stop_disable_autoroller()`: Ferma il thread disable_autoroller
- `run()`: Loop principale che aggiorna continuamente lo stato

**Relazioni**:
- Controllato da: State Handler, Building Monitor, Multiplier Monitor
- Controlla: Autoroller, Disable Autoroller

---

### Autoroller

**File**: `handlers/autoroller.py`

**Scopo**: Clicca automaticamente sul pulsante "GO" per attivare l'autoroll quando non è attivo nel gioco.

**Funzionamento**:
1. Attende che `autoroller_running` sia True
2. Verifica di essere nella schermata home (`in_home_status`)
3. Cerca l'immagine del pulsante "GO" sullo schermo usando OCR
4. Se trovato:
   - Muove il mouse sul pulsante GO rilevato
   - Clicca sulla posizione esatta del pulsante
   - Muove il mouse al centro dello schermo
   - Attende 10 secondi per permettere al gioco di iniziare
5. Attende che il giocatore finisca di tirare prima di ripetere

**Condizioni di esecuzione**:
- `autoroller_running` deve essere True
- `in_home_status` deve essere True
- `rolling_status` deve essere False

**Immagini utilizzate**:
- `images/go.png`: Pulsante GO per lanciare i dadi

![Pulsante GO](images/go.png)

**Note importanti**:
- Clicca direttamente sulla posizione rilevata del pulsante GO
- Non usa pressione di tasti ma click del mouse sulle coordinate esatte
- Se il pulsante non viene trovato, attende 1 secondo e riprova

---

### Disable Autoroller

**File**: `handlers/disable_autoroller.py`

**Scopo**: Disattiva l'autoroll nel gioco quando è attivo ma non dovrebbe esserlo (es. durante upgrade edifici).

**Funzionamento**:
1. Attende che `disable_autoroller_running` sia True
2. Verifica di essere nella schermata home
3. Cerca l'immagine del pulsante "autoroll" attivo sullo schermo
4. Se trovato, clicca su di esso per disattivarlo
5. Attende che il giocatore inizi a tirare prima di ripetere

**Condizioni di esecuzione**:
- `disable_autoroller_running` deve essere True
- `in_home_status` deve essere True
- Cerca di disattivare l'autoroll quando è attivo nel gioco

**Immagini utilizzate**:
- `images/autoroll.png`: Pulsante autoroll attivo

![Pulsante Autoroll](images/autoroll.png)

---

### Autoroll Monitor

**File**: `handlers/autoroll_monitor.py`

**Scopo**: Monitora il numero di tiri disponibili e gestisce automaticamente l'autoroller in base alle soglie configurate.

**Funzionamento**:
1. Attende che builder e multiplier handler non siano in esecuzione
2. Monitora continuamente il numero di tiri (`shared_state.rolls`)
3. Se i tiri scendono sotto `AR_MINIMUM_ROLLS`:
   - Ferma l'autoroller
   - Avvia il disable_autoroller
4. Se i tiri raggiungono `AR_RESUME_ROLLS`:
   - Ferma il disable_autoroller
   - Avvia l'autoroller
5. Attende cambiamenti nel numero di tiri prima di rivalutare

**Soglie configurabili** (da `.env`):
- `AR_MINIMUM_ROLLS`: Soglia minima sotto la quale si ferma l'autoroller
- `AR_RESUME_ROLLS`: Soglia per riavviare l'autoroller

**Dipendenze**:
- Riceve istanza di `AutoRollHandler` per controllare autoroller
- Verifica che `builder_event` e `multiplier_handler_event` non siano attivi
- Si coordina con Building Monitor e Multiplier Monitor

---

### Building Handler

**File**: `handlers/building_handler.py`

**Scopo**: Gestisce automaticamente l'upgrade degli edifici nel gioco, raccogliendo dati sui costi e aggiornando un file JSON.

**Funzionamento**:
1. Entra nel menu di costruzione cliccando sull'icona build
2. Rileva il nome della board corrente usando OCR
3. Per ogni edificio (5 totali):
   - Estrae il costo dell'upgrade usando OCR
   - Salva il costo nel file JSON
   - Clicca sull'edificio per upgradarlo
   - Incrementa il livello di upgrade
4. Ripete fino a quando tutti gli edifici sono al livello massimo (6 livelli)
5. Calcola il costo totale della board e lo salva
6. Esce automaticamente quando completato

**Struttura dati edifici**:
Ogni edificio ha:
- Nome (`building1` - `building5`)
- Coordinate percentuali (x, y, right, bottom) relative alla finestra
- Livello di upgrade corrente
- Costi per ogni livello (upgrade0 - upgrade6)

**File JSON generato**:
- Nome: `{WINDOW_TITLE}_game_data.json`
- Contiene dati per ogni board:
  - `board_number`: Numero progressivo della board
  - `board_name`: Nome della board
  - `building1` - `building5`: Array dei costi per livello
  - `total_cost`: Costo totale della board

**Immagini utilizzate**:
- `images/build.png`: Icona per entrare nel menu build

![Icona Build](images/build.png)

- `images/build-exit.png`: Pulsante per uscire dal menu

![Pulsante Exit Build](images/build-exit.png)

- `images/building-finished.png`: Indica edificio completato

![Edificio Completato](images/building-finished.png)

**Metodi principali**:
- `load_data()`: Carica dati da JSON
- `save_data()`: Salva dati su JSON
- `gather_board_name()`: Estrae nome board con OCR
- `enter_build_menu()`: Naviga al menu build
- `check_menu_status()`: Verifica se nel menu build
- `extract_and_convert_cost()`: Converte testo OCR in valore numerico (es. "1.5M" → 1500000)
- `create_new_board()`: Crea nuova entry board
- `update_and_append_board_data()`: Aggiorna o aggiunge dati board
- `calculate_total_cost()`: Calcola costo totale board
- `run()`: Loop principale

---

### Building Monitor

**File**: `handlers/building_monitor.py`

**Scopo**: Monitora i tiri disponibili e avvia il Building Handler quando non è più possibile tirare i dadi.

**Funzionamento**:
1. Monitora continuamente `shared_state.rolls` e `shared_state.money`
2. Quando rolls == 0 (nessun tiro disponibile) E money >= denaro minimo (1000):
   - Imposta `builder_event` per bloccare altri handler
   - Ferma l'autoroller se in esecuzione
   - Avvia il disable_autoroller
   - Acquisisce i lock per impedire interferenze
   - Avvia Building Handler in un nuovo thread
   - Attende che Building Handler completi
   - Rilascia i lock
3. Riavvia l'autoroller dopo il completamento

**Condizioni di avvio build**:
```python
rolls == 0 AND money >= 1000
```
- Il build inizia solo quando non ci sono più tiri disponibili
- È richiesto un minimo di denaro per evitare build inutili

**Coordinamento**:
- Attende che Multiplier Handler non sia attivo
- Blocca avvio/arresto autoroller durante costruzione
- Imposta eventi per notificare altri thread

---

### Multiplier Handler

**File**: `handlers/multiplier_handler.py`

**Scopo**: Cambia il moltiplicatore di scommessa nel gioco cliccando sul selettore fino a raggiungere il valore corretto.

**Funzionamento**:
1. Riceve il moltiplicatore corretto da raggiungere come parametro
2. Attende di essere nella schermata home
3. Calcola le coordinate del selettore moltiplicatore (regione 61%-71% larghezza, 70.5%-73.3% altezza)
4. Clicca ripetutamente sul selettore
5. Verifica dopo ogni click se il moltiplicatore è quello corretto
6. Si ferma quando:
   - Il moltiplicatore corretto è raggiunto, OPPURE
   - Timeout di 30 secondi scaduto

**Coordinamento**:
- Imposta `multiplier_handler_event` durante l'esecuzione
- Notifica `multiplier_handler_finished_condition` al completamento
- Muove il mouse al centro dello schermo al termine

**Timeout**: 30 secondi (configurabile nel costruttore)

---

### Multiplier Monitor

**File**: `handlers/multiplier_monitor.py`

**Scopo**: Calcola il moltiplicatore ottimale in base ai tiri disponibili e agli eventi attivi, avviando il Multiplier Handler quando necessario.

**Funzionamento**:
1. Rileva se l'evento "High Roller" è attivo cercando l'immagine
2. Calcola il moltiplicatore corretto basandosi su:
   - Numero di tiri disponibili
   - Se evento High Roller è attivo o meno
3. Se il moltiplicatore corrente è inferiore a quello corretto:
   - Ferma l'autoroller
   - Avvia il disable_autoroller
   - Avvia il Multiplier Handler con il valore corretto
   - Attende che completi
4. Riavvia l'autoroller dopo il completamento

**Tabella moltiplicatori (senza High Roller)**:
| Tiri | Moltiplicatore |
|------|----------------|
| < 50 | 3 |
| < 100 | 5 |
| < 300 | 10 |
| < 1000 | 20 |
| < 2000 | 50 |
| ≥ 2000 | 100 |

**Tabella moltiplicatori (con High Roller)**:
| Tiri | Moltiplicatore |
|------|----------------|
| < 50 | 3 |
| < 100 | 5 |
| < 300 | 10 |
| < 1000 | 200 |
| < 5000 | 500 |
| ≥ 5000 | 1000 |

**Immagini utilizzate**:
- `images/high-roller.png`: Icona evento High Roller

![Evento High Roller](images/high-roller.png)

**Coordinamento**:
- Attende che builder non sia attivo
- Blocca autoroller durante cambio moltiplicatore
- Si coordina con Autoroll Handler

---

### UI Handler

**File**: `handlers/ui_handler.py`

**Scopo**: Gestisce automaticamente popup e elementi UI indesiderati cliccando su pulsanti di chiusura.

**Funzionamento**:
1. Scansiona continuamente la directory `images/ui/`
2. Per ogni immagine nella directory:
   - Cerca l'immagine sullo schermo usando OCR
   - Se trovata, clicca su di essa
   - Muove il mouse al centro dello schermo
3. Si mette in pausa quando `idle_event` è attivo
4. Ritardo di 0.5 secondi tra le scansioni

**Directory immagini**: `images/ui/`
- Deve contenere immagini dei pulsanti/elementi UI da cliccare
- Supporta sottodirectory (es. `ui/community-chest/`, `ui/quickwins/`)

**Esempi di immagini UI utilizzate**:

![Chiudi Pubblicità](images/ui/ad-close-2.png)
![OK Button](images/ui/ok.png)
![Skip Button](images/ui/skip.png)
![Board Complete](images/ui/boardcomplete.png)

**Pausa automatica**:
- Si ferma quando Idle Handler sta lavorando
- Riprende automaticamente quando `idle_event` viene cleared

**Utilizzo tipico**:
- Chiudere popup pubblicitari
- Chiudere finestre di ricompensa automatiche
- Gestire notifiche che bloccano il gioco

---

### Bank Heist Handler

**File**: `handlers/bank_heist_handler.py`

**Scopo**: Rileva automaticamente l'evento "Bank Heist" e partecipa cliccando direttamente sulla porta.

**Funzionamento**:
1. Cerca continuamente l'immagine della porta del Bank Heist
2. Quando rilevata:
   - Stampa messaggio di conferma con coordinate
   - Muove il mouse sulla porta rilevata
   - Clicca sulla porta per partecipare
   - Muove il mouse al centro dello schermo
   - Attende 5 secondi prima di cercare di nuovo
3. Se non trovata, attende 1 secondo e riprova

**Immagini utilizzate**:
- `images/bank-heist-door.png`: Porta dell'evento Bank Heist

![Bank Heist Door](images/bank-heist-door.png)

**Caratteristiche**:
- Esecuzione continua in background
- Non interferisce con altri handler
- Click diretto sulla porta rilevata
- Prevenzione click multipli con timeout di 5 secondi

**Debug**:
Per verificare che il Bank Heist venga rilevato correttamente:
```powershell
python debug_bank_heist.py
```
Lo script mostrerà dove viene rilevata la porta e dove cliccherà il bot.

---

### Shut Down Handler

**File**: `handlers/shut_down_handler.py`

**Scopo**: Gestisce l'evento "Shut Down" cliccando automaticamente sui marker che appaiono sullo schermo.

**Funzionamento**:
1. Cerca due varianti del marker Shut Down:
   - Marker verso l'alto (`sd-marker-up.png`)
   - Marker verso il basso (`sd-marker-down.png`)
2. Quando ne trova uno:
   - Muove il mouse sul marker
   - Clicca
   - Attende 0.2 secondi
   - Muove il mouse al centro
3. Ritardo di 1 secondo tra le scansioni

**Immagini utilizzate**:
- `images/sd-marker-up.png`: Marker Shut Down verso l'alto

![Marker Shut Down Up](images/sd-marker-up.png)

- `images/sd-marker-down.png`: Marker Shut Down verso il basso

![Marker Shut Down Down](images/sd-marker-down.png)

**Velocità**:
- Scansione rapida per non perdere marker
- Reazione immediata quando trovato

---

### Idle Handler

**File**: `handlers/idle_handler.py`

**Scopo**: Gestisce lo stato di inattività del bot, controllando se ci sono ricompense da riscuotere dal menu inviti quando il bot è fermo.

**Funzionamento**:
1. Monitora continuamente:
   - Tiri disponibili (`rolls < AR_RESUME_ROLLS`)
   - Denaro disponibile (`money < BUILD_START_AMOUNT`)
   - Stato di altri handler (builder, autoroller, multiplier)
2. Quando tutte le condizioni indicano inattività:
   - Imposta `idle_event` per fermare UI Handler
   - Naviga al menu amici
   - Clicca sul pulsante invita
   - Legge il conteggio inviti con OCR (formato "X/50")
   - Se il conteggio non è 5, 15, 30 o 50 (soglie reward):
     - Esce dal menu
   - Se raggiunge una soglia, rimane nel menu (il giocatore deve riscuotere manualmente)
3. Muove il mouse al centro e rilascia `idle_event`
4. Attende 45 secondi prima di ricontrollare

**Coordinate pulsanti**:
- Friends button: 83.8% larghezza, 90.7% altezza
- Exit button: 47.4% larghezza, 96.8% altezza

**Regione OCR conteggio inviti**:
- X: 36.5% - 58.6%
- Y: 68.6% - 71.1%

**Immagini utilizzate**:
- `images/share_button.png`: Pulsante condividi nel menu inviti

![Share Button](images/share_button.png)

- `images/invite-button.png`: Pulsante invita

![Invite Button](images/invite-button.png)

**Soglie ricompense**: 5, 15, 30, 50 inviti

**Condizioni di attivazione**:
```python
rolls < AR_RESUME_ROLLS AND
money < 1000 AND  # Denaro minimo per build
NOT builder_running AND
NOT autoroller_running AND
NOT multiplier_handler_running
```

---

### Destruction Handler

**File**: `handlers/destruction_handler.py`

**Scopo**: Gestisce la modalità distruzione rilevando e cliccando automaticamente sui mirini (target) che appaiono sullo schermo.

**Funzionamento**:
1. Cerca continuamente l'immagine del mirino (`target.png`)
2. Quando trovato:
   - Stampa messaggio con coordinate
   - Muove il mouse sul mirino
   - Clicca
   - Memorizza l'ultimo target cliccato
   - Muove il mouse al centro
   - Attende 1 secondo
3. Si mette in pausa se `idle_event` è attivo
4. Ritardo di 2 secondi tra le scansioni

**Immagini utilizzate**:
- `images/target.png`: Mirino da cliccare durante eventi distruzione

![Target/Mirino](images/target.png)

**Gestione errori**:
- Verifica che il file immagine esista
- Gestisce eccezioni durante la ricerca
- Log di warning/error appropriati

**Velocità**:
- Scansione ogni 2 secondi
- Pausa di 1 secondo dopo ogni click riuscito

---

## Sistema di Sincronizzazione

### Shared State

Il sistema utilizza una classe `SharedState` centralizzata che mantiene:

#### Variabili di stato
- **Denaro**: `money` - Denaro disponibile
- **Tiri**: `rolls` - Tiri disponibili
- **Moltiplicatore**: `multiplier` - Moltiplicatore attuale
- **Stati handler**: Flag booleani per ogni handler (`*_running`)
- **Stati UI**: `rolling_status`, `in_home_status`

#### Condition Variables
Usate per sincronizzare thread:
- `money_condition`: Notifica cambiamenti denaro
- `rolls_condition`: Notifica cambiamenti tiri
- `multiplier_condition`: Notifica cambiamenti moltiplicatore
- `builder_running_condition`: Notifica stato builder
- `autoroller_running_condition`: Notifica stato autoroller
- E molte altre per ogni handler

#### Lock
Usati per accesso esclusivo a risorse:
- `moveTo_lock`: Blocca movimenti mouse
- `press_lock`: Blocca pressione tasti
- `start_autoroller_lock`: Blocca avvio autoroller
- `stop_autoroller_lock`: Blocca arresto autoroller
- `start_disable_autoroller_lock`
- `stop_disable_autoroller_lock`

#### Events
Eventi per segnalare stati speciali:
- `multiplier_handler_event`: Multiplier handler attivo
- `builder_event`: Builder attivo
- `idle_event`: Sistema in idle

#### Barrier
- `thread_barrier`: Barrier con 9 partecipanti per sincronizzare l'avvio di tutti i thread

### Meccanismo di Coordinamento

1. **Barriera iniziale**: Tutti i thread attendono alla barriera prima di iniziare
2. **Condition Wait**: I thread attendono notifiche su condition variables
3. **Lock Acquisition**: I thread acquisiscono lock prima di operazioni critiche
4. **Event Set/Clear**: Eventi settati/cleared per comunicare stati
5. **Notifiche**: `notify()` o `notify_all()` per svegliare thread in attesa

---

## Flusso di Esecuzione

### Avvio Sistema

```
main.py
  ├─> Inizializza cache immagini
  ├─> Crea StateHandler
  ├─> Avvia PlayerInfo thread (OCR valori gioco)
  ├─> Avvia SetConsoleTitle thread
  └─> Attende input tastiera (keyboard.Listener)
```

### Avvio Handler (esempio con Page Up)

```
Pressione Page Up
  ├─> toggle_autoroll_handler()
  │     └─> Avvia autoroll_handler thread
  │           ├─> Attende alla barrier
  │           ├─> Inizializza stati
  │           └─> Loop aggiornamento stato
  │
  ├─> toggle_building_monitor()
  │     └─> Avvia building_monitor thread
  │           ├─> Attende alla barrier
  │           ├─> Calcola BUILD_START_AMOUNT
  │           └─> Loop monitoraggio denaro
  │
  ├─> toggle_bank_heist_handler()
  │     └─> Avvia bank_heist thread
  │           ├─> Attende alla barrier
  │           └─> Loop rilevamento evento
  │
  [... altri handler ...]
  │
  └─> Tutti i thread attendono alla barrier (9 thread)
        └─> Barrier rilasciata → Tutti i thread iniziano
```

### Ciclo Autoroll

```
Autoroll Monitor
  ├─> Verifica rolls < AR_MINIMUM_ROLLS
  │     ├─> Ferma autoroller
  │     └─> Avvia disable_autoroller
  │           └─> Cerca "autoroll.png"
  │                 └─> Se trovato: clicca sulla posizione per disattivare
  │
  └─> Verifica rolls >= AR_RESUME_ROLLS
        ├─> Ferma disable_autoroller
        └─> Avvia autoroller
              └─> Cerca "go.png"
                    └─> Se trovato: clicca sulla posizione del pulsante GO
```

### Ciclo Building

```
Building Monitor
  ├─> rolls == 0 AND money >= 1000?
  │     ├─> Imposta builder_event (blocca altri handler)
  │     ├─> Ferma autoroller
  │     ├─> Acquisisce lock
  │     └─> Avvia Building Handler
  │           ├─> Entra menu build
  │           ├─> Legge nome board
  │           ├─> Per ogni edificio (5):
  │           │     ├─> OCR costo upgrade
  │           │     ├─> Salva in JSON
  │           │     ├─> Clicca per upgrade
  │           │     └─> Incrementa livello
  │           ├─> Calcola costo totale
  │           ├─> Salva JSON
  │           └─> Notifica completamento
  │
  └─> Rilascia lock
      ├─> Clear builder_event
      └─> Riavvia autoroller
```

### Ciclo Multiplier

```
Multiplier Monitor
  ├─> Rileva High Roller event?
  ├─> Calcola multiplier corretto (tabella)
  └─> multiplier < correct_multiplier?
        ├─> Ferma autoroller
        ├─> Avvia Multiplier Handler
        │     ├─> Calcola coordinate selettore
        │     ├─> Loop (max 30s):
        │     │     ├─> Clicca selettore
        │     │     ├─> Verifica multiplier
        │     │     └─> Esci se corretto
        │     └─> Notifica completamento
        │
        └─> Riavvia autoroller
```

### Gestione Idle

```
Idle Handler
  ├─> Verifica condizioni idle:
  │     ├─> rolls < AR_RESUME_ROLLS
  │     ├─> money < 1000 (denaro minimo per build)
  │     ├─> NOT builder_running
  │     ├─> NOT autoroller_running
  │     └─> NOT multiplier_handler_running
  │
  ├─> Se tutte vere:
  │     ├─> Set idle_event (pausa UI handler)
  │     ├─> Naviga menu amici
  │     ├─> Clicca invita
  │     ├─> OCR conteggio inviti
  │     └─> Esce se non è soglia reward
  │
  └─> Clear idle_event
      └─> Attende 45s prima di ricontrollare
```

---

## Note Tecniche

### OCR e Rilevamento Immagini

Tutti gli handler utilizzano `OCRUtils` per:
- **Template Matching**: `ocr_utils.find(image)` cerca un'immagine sullo schermo
- **Text Recognition**: `ocr_utils.ocr_to_str()` estrae testo da regioni specifiche

### Gestione Finestre

- Coordinate calcolate in percentuali della finestra
- Supporta ridimensionamento finestra
- `moveto_center()` riporta mouse al centro dopo azioni

### Cache Immagini

- Sistema di caching per velocizzare caricamento immagini
- `shared_state.load_image(path)` carica da cache o da disco
- Cache salvata in `image_cache.pkl`

### Threading Best Practices

- Tutti i thread sono daemon (terminano con il programma principale)
- Uso estensivo di condition variables per evitare polling
- Lock per proteggere risorse condivise (mouse, tastiera)
- Barrier per sincronizzare avvio multipli thread

### Configurazione (.env)

Variabili chiave:
```env
AR_MINIMUM_ROLLS=50        # Soglia minima tiri
AR_RESUME_ROLLS=100        # Soglia ripresa autoroll
WINDOW_TITLE="BlueStacks"  # Titolo finestra gioco
```

**Nota**: La variabile `BUILD_START_AMOUNT` è stata rimossa. Il build ora inizia automaticamente quando `rolls == 0` e c'è almeno 1000 di denaro disponibile.

---

## Diagramma Dipendenze

```
State Handler (Coordinatore centrale)
    │
    ├─> Autoroll Handler
    │     ├─> Autoroller (esegue autoroll)
    │     └─> Disable Autoroller (disattiva autoroll)
    │
    ├─> Autoroll Monitor
    │     └─> Controlla Autoroll Handler
    │
    ├─> Building Monitor
    │     ├─> Controlla Autoroll Handler
    │     └─> Avvia Building Handler
    │
    ├─> Multiplier Monitor
    │     ├─> Controlla Autoroll Handler
    │     └─> Avvia Multiplier Handler
    │
    ├─> UI Handler (indipendente)
    ├─> Bank Heist Handler (indipendente)
    ├─> Shut Down Handler (indipendente)
    ├─> Destruction Handler (indipendente)
    └─> Idle Handler (osserva stato globale)
```

---

## Conclusioni

Il sistema MonopolyGoBot è altamente modulare e sincronizzato, con ogni handler responsabile di un aspetto specifico del gameplay. La coordinazione avviene tramite `SharedState` e meccanismi di sincronizzazione threading avanzati. Questo permette al bot di:

1. **Reagire rapidamente** agli eventi di gioco
2. **Ottimizzare le risorse** (tiri, denaro, moltiplicatore)
3. **Raccogliere dati** sui costi degli upgrade
4. **Operare autonomamente** per lunghi periodi
5. **Evitare conflitti** tra operazioni simultanee

Il design modulare facilita l'aggiunta di nuovi handler e la manutenzione del codice esistente.
