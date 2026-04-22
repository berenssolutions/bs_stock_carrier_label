# bs_stock_carrier_label — Versandetiketten Drucken

**Autor:** Lennart Berens, Berens Solutions  
**Kontakt:** mail@berenssolutions.de  
**Odoo-Version:** 18.0  
**Lizenz:** LGPL-3  

---

## Was macht dieses Modul?

Fügt im Lieferauftrag (`stock.picking`) unter **Zahnrad → Drucken** einen neuen
Eintrag **"Versandetiketten"** hinzu — identisch positioniert wie "Lieferschein"
und "Kommissioniervorgänge".

Der Report ist ein vollwertiger `ir.actions.report` und damit:
- ✅ **IoT-Drucker-kompatibel** (Drucker-Auswahl-Dialog beim ersten Druck)
- ✅ Drucker-Verknüpfung wird pro Nutzer im Browser-Cache gespeichert
- ✅ Konfigurierbar unter Einstellungen → Technisch → Reports → IoT Device

---

## Voraussetzungen

- Odoo 18.0
- Module `stock` und `delivery` installiert
- Ein Carrier-Modul (z.B. `delivery_dhl`) muss installiert sein und
  Versandetiketten als `ir.attachment` am Picking anhängen

---

## Installation

1. Modul in den Addons-Pfad kopieren
2. Odoo neu starten
3. In Odoo: Apps → Suche nach "Versandetiketten" → Installieren

---

## Konfiguration

### IoT-Drucker einrichten
1. IoT App → Geräte → Deinen Label-Drucker öffnen
2. Im Report-Bereich: "Versandetiketten" hinzufügen
3. Beim ersten Druck aus dem Lieferauftrag erscheint der Drucker-Auswahl-Dialog

### Carrier-Keywords anpassen
Falls dein Carrier-Label-Anhang keines der Standard-Keywords im Namen enthält,
ergänze es in `models/stock_picking.py`:

```python
CARRIER_LABEL_KEYWORDS = [
    'LABEL', 'DHL', 'UPS', 'DPD', 'HERMES', 'GLS', 'FEDEX', 'TNT',
    'SCHENKER', 'DACHSER',
    'MEIN_CARRIER',  # ← hier ergänzen
]
```

---

## Technische Details

### Wie erkennt das Modul Carrier-Labels?
Die Methode `get_carrier_label_attachments()` in `stock.picking` sucht nach
`ir.attachment`-Datensätzen, die:
1. Am Picking hängen (`res_model=stock.picking`)
2. Ein unterstütztes Mimetype haben (PDF, PNG, JPEG, GIF, TIFF)
3. Einen Carrier-Keyword im Dateinamen enthalten

### Papierformat
Standardmäßig wird **A6 (105×148mm)** verwendet — das DHL-Standardformat.
Das Papierformat kann unter Einstellungen → Technisch → Papierformate
auf dein Etikett angepasst werden.

### PDF-Labels vs. Bild-Labels
- **Bild-Labels (PNG/JPEG):** Werden direkt eingebettet, optimale Qualität
- **PDF-Labels (DHL Standard):** Werden über `<object>`-Tag eingebettet.
  wkhtmltopdf hat hier systembedingte Einschränkungen — falls die Qualität
  nicht ausreicht, den PDF-Download direkt aus dem Chatter nutzen.

---

## Debugging

Prüfe in der Odoo-Shell, welche Anhänge an deinem Picking hängen:

```python
picking = env['stock.picking'].browse(PICKING_ID)
attachments = env['ir.attachment'].search([
    ('res_model', '=', 'stock.picking'),
    ('res_id', '=', picking.id),
])
for a in attachments:
    print(f"{a.name} | {a.mimetype} | ID: {a.id}")
```

---

## Changelog

### 18.0.1.0.0 (Initial Release)
- Report "Versandetiketten" im Drucken-Menü des Lieferauftrags
- IoT-Drucker-Unterstützung
- Automatische Erkennung von Carrier-Labels via Dateinamen-Keywords
- Papierformat A6 für DHL-Standard-Labels
