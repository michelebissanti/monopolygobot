# RISOLUZIONE PROBLEMA: Bot Non Legge i Dati

## 🚨 Problema

Il bot:
- ❌ Non tira i dadi automaticamente
- ❌ Non cambia il moltiplicatore  
- ❌ Non apre il menu costruzioni
- ✅ Funziona SOLO se attivi manualmente tutto prima

## 🔍 Causa Principale

Il bot dipende dall'immagine **`images/in-home-icon.png`** per sapere che sei nella schermata home.

**Se questa immagine non viene trovata:**
- `in_home_status` = False
- Il bot pensa che NON sei nella home
- NON legge rolls, money, multiplier
- NON attiva nessun handler automatico

## 🧪 Diagnosi

Esegui lo script di debug:

```powershell
python debug_player_info.py
```

Lo script ti dirà:
1. ✅/❌ Se trova l'icona in-home
2. ✅/❌ Se legge correttamente rolls, money, multiplier
3. 💡 Cosa devi fare per risolvere

## 🔧 Soluzione

### Passo 1: Trova un'Icona Sempre Visibile

Nella schermata HOME del gioco, trova un'icona che è **SEMPRE** visibile:
- Icona menu (☰)
- Icona impostazioni (⚙️)
- Logo del gioco
- Icona profilo
- Qualsiasi elemento FISSO nella home

### Passo 2: Cattura Screenshot dell'Icona

1. **Apri il gioco** in fullscreen sulla schermata HOME
2. **Usa lo strumento di cattura Windows** (Win + Shift + S)
3. **Cattura SOLO l'icona** (piccola area, circa 50x50 pixel)
4. **Salva come**: `images/in-home-icon.png` (sovrascrivi quello esistente)

**IMPORTANTE**: 
- ✅ Cattura SOLO l'icona, senza sfondo extra
- ✅ Deve essere un'icona che non cambia MAI
- ✅ Deve essere SEMPRE visibile nella home

### Passo 3: Testa

```powershell
python debug_player_info.py
```

Dovrebbe dire: `✅ IN-HOME ICON TROVATA!`

### Passo 4: Verifica Coordinate OCR

Se l'icona in-home è OK ma i valori sono sbagliati, probabilmente le coordinate OCR sono sbagliate per la tua risoluzione.

**Lo script debug_player_info.py salva le immagini:**
- `ocr_rolls_processed.png` - Vedi cosa legge per i rolls
- `ocr_money_raw.png` - Vedi cosa legge per il denaro
- `ocr_multiplier_processed.png` - Vedi cosa legge per il moltiplicatore

**Se le immagini sono sbagliate** (mostrano la parte sbagliata dello schermo):
- Le coordinate percentuali in `player_info.py` vanno aggiustate per la tua risoluzione
- Dovresti vedere i NUMERI chiaramente in quelle immagini

## 📋 Checklist Completa

- [ ] Gioco aperto in fullscreen
- [ ] Sei nella schermata HOME
- [ ] Hai catturato un'icona sempre visibile
- [ ] L'hai salvata come `images/in-home-icon.png`
- [ ] Eseguito `python debug_player_info.py`
- [ ] Mostra "✅ IN-HOME ICON TROVATA!"
- [ ] Legge correttamente rolls, money, multiplier
- [ ] Riavviato il bot principale

## 🎯 Dopo la Correzione

Una volta che `in-home-icon.png` funziona:

1. Il bot leggerà automaticamente:
   - ✅ Rolls disponibili
   - ✅ Denaro
   - ✅ Moltiplicatore

2. Attiverà automaticamente:
   - ✅ Autoroll quando necessario
   - ✅ Cambio moltiplicatore
   - ✅ Costruzioni quando rolls = 0

## 🆘 Se Ancora Non Funziona

1. **Controlla log.txt** - Cerca errori
2. **Verifica Tesseract** sia installato: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. **Verifica coordinate** - Le percentuali potrebbero essere sbagliate per la tua risoluzione
4. **Monitor multipli** - Sposta il gioco sul monitor primario
5. **Esegui debug** con le immagini generate per vedere cosa vede il bot

## 📊 File di Debug Generati

Dopo `python debug_player_info.py`:

| File | Contenuto |
|------|-----------|
| `playerinfo_screenshot.png` | Screenshot completo della finestra |
| `ocr_rolls_processed.png` | Area rolls processata per OCR |
| `ocr_money_raw.png` | Area denaro catturata |
| `ocr_multiplier_processed.png` | Area moltiplicatore processata |

Questi file ti aiutano a capire cosa vede il bot e se le coordinate sono corrette.
