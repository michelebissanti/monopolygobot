# Guida al Debug - Problemi con l'Autoroll

## Problema: Lo script non tira automaticamente i dadi

### Possibili Cause

1. **Setup con due monitor**: Le coordinate della finestra potrebbero essere negative o sbagliate
2. **Finestra non rilevata correttamente**: Il titolo della finestra potrebbe non corrispondere
3. **Immagine GO non corrisponde**: La risoluzione o l'aspetto del pulsante è diverso
4. **OCR non funziona**: Problemi con il template matching

---

## Soluzione: Script di Debug

### Come Usare lo Script di Debug

1. **Assicurati che il gioco sia aperto** nella schermata home (dove si vede il pulsante GO)

2. **Apri il terminale PowerShell** nella cartella del progetto:
   ```powershell
   cd C:\Users\genie\Documents\GitHub\monopolygobot
   ```

3. **Attiva l'ambiente virtuale** (se non già attivo):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Esegui lo script di debug**:
   ```powershell
   python debug_vision.py
   ```

5. **Controlla l'output** nel terminale - ti dirà:
   - Se la finestra è stata trovata
   - Le coordinate della finestra
   - Se ci sono problemi con multi-monitor
   - Se il pulsante GO è stato trovato

6. **Controlla la cartella `debug_screenshots/`** - contiene:
   - `1_finestra_completa.png` - Screenshot di tutta la finestra catturata
   - `2_finestra_annotata.png` - Screenshot con coordinate e bordi rossi
   - `3_template_go.png` - L'immagine GO che sta cercando
   - `4_heatmap_matching.png` - Mappa termica della ricerca (se GO non trovato)
   - `5_go_button_trovato.png` - Posizione del pulsante GO (se trovato)

---

## Problemi Comuni e Soluzioni

### 1. Coordinate Negative (Setup Multi-Monitor)

**Sintomo**: Il terminale mostra coordinate negative (es. `Left: -1920`)

**Causa**: La finestra è su un monitor secondario a sinistra del primario

**Soluzione**:
- **Opzione A**: Sposta la finestra del gioco sul monitor primario
- **Opzione B**: Imposta il monitor del gioco come primario in Windows

### 2. Pulsante GO Non Trovato

**Sintomo**: Il debug mostra "❌ PULSANTE GO NON TROVATO!"

**Possibili cause**:

#### A. Finestra non nella schermata home
- **Soluzione**: Assicurati di essere nella schermata home prima di eseguire il debug

#### B. Risoluzione diversa
- **Verifica**: Confronta `3_template_go.png` con `1_finestra_completa.png`
- **Soluzione**: Se il pulsante nel gioco è più grande/piccolo, rifai lo screenshot:
  1. Apri il gioco in fullscreen
  2. Vai alla schermata home
  3. Usa uno strumento di cattura schermo per catturare SOLO il pulsante GO
  4. Salva come `images/go.png` (sovrascrivi il vecchio)

#### C. Aspetto diverso del pulsante
- **Verifica**: Il pulsante GO nel gioco ha colori/stile diversi dal template
- **Soluzione**: Cattura un nuovo screenshot del pulsante GO dal tuo gioco

#### D. Soglia di confidence troppo alta
- **Verifica**: Controlla `4_heatmap_matching.png` - se ci sono zone gialle/arancioni vicino al pulsante GO
- **Soluzione**: Nel file `utils/ocr_utils.py`, riga ~50, cambia:
  ```python
  threshold = 0.75  # Prova con 0.65 o 0.70
  ```

### 3. Finestra Non Trovata

**Sintomo**: Il debug mostra "❌ ERRORE: Nessuna finestra trovata"

**Causa**: Il titolo della finestra nel `.env` non corrisponde

**Soluzione**:
1. Guarda l'elenco delle finestre disponibili nell'output
2. Trova il titolo corretto della finestra del gioco
3. Aggiorna il file `.env`:
   ```env
   WINDOW_TITLE="Nome Corretto Finestra"
   ```

---

## Verifica Finale

Dopo aver risolto i problemi, verifica che:

1. ✅ Lo script di debug trova la finestra
2. ✅ Le coordinate sono positive (o hai spostato la finestra)
3. ✅ Il pulsante GO viene trovato con confidence >= 0.75
4. ✅ La posizione del pulsante GO nell'immagine `5_go_button_trovato.png` è corretta

Se tutto è OK, prova a riavviare il bot principale.

---

## Test Rapido

Dopo le correzioni, esegui questo test rapido:

```powershell
# 1. Attiva ambiente
.\venv\Scripts\Activate.ps1

# 2. Esegui debug
python debug_vision.py

# 3. Controlla output e immagini in debug_screenshots/

# 4. Se tutto OK, avvia il bot
python main.py
```

---

## Altre Verifiche

### Verifica OCR di Player Info

Se l'autoroll parte ma non legge correttamente i dati (rolls, money):

1. Controlla che Tesseract sia installato:
   ```powershell
   Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

2. Se restituisce `False`, installa Tesseract:
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Installa in `C:\Program Files\Tesseract-OCR\`

### Log del Bot

Per vedere cosa sta facendo il bot in tempo reale:

1. Apri `log.txt` nella cartella del progetto
2. Cerca messaggi come:
   - `[AUTOROLL] AutoRoll is not active. AutoRolling...`
   - `[AUTOROLL] Exiting autoroll...`

---

## Supporto Aggiuntivo

Se il problema persiste:

1. **Esegui il debug** e salva l'output del terminale
2. **Controlla le immagini** in `debug_screenshots/`
3. **Verifica il log** in `log.txt`
4. **Controlla** che tutti i prerequisiti siano installati (requirements.txt)

### Informazioni Utili da Raccogliere

- Risoluzione del gioco
- Sistema operativo e versione
- Numero e disposizione monitor
- Output completo di `debug_vision.py`
- Screenshot dalla cartella `debug_screenshots/`
