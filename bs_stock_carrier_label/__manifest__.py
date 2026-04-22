# -*- coding: utf-8 -*-
{
    'name': 'Versandetiketten Drucken',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Reporting',
    'summary': 'Carrier-Versandetiketten (DHL etc.) im Drucken-Menü des Lieferauftrags mit IoT-Drucker-Unterstützung',
    'description': """
Versandetiketten Drucken
========================

Dieses Modul ergänzt den Lieferauftrag (stock.picking) um einen
"Versandetiketten"-Eintrag im Drucken-Untermenü (Zahnrad → Drucken).

Features:
- Erscheint im selben Drucken-Menü wie "Lieferschein" und "Kommissioniervorgänge"
- Vollständig IoT-Drucker-kompatibel (Drucker-Auswahl wie bei allen anderen Reports)
- Erkennt automatisch alle Carrier-Label-Anhänge am Picking (DHL, UPS, DPD, GLS, ...)
- Unterstützt PDF- und Bild-Anhänge
- Klare Fehlermeldung wenn noch kein Versandetikett erstellt wurde

Voraussetzung:
- Das DHL-/Carrier-Modul muss installiert sein und Labels am Picking anhängen
- Für IoT-Druck: IoT Box muss konfiguriert sein
    """,
    'author': 'Lennart Berens, Berens Solutions',
    'website': 'https://berenssolutions.de',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'delivery',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/carrier_label_report.xml',
        'report/carrier_label_action.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
