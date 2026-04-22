# -*- coding: utf-8 -*-
{
    'name': 'Versandetiketten Drucken',
    'version': '18.0.1.1.0',
    'category': 'Inventory/Reporting',
    'summary': 'Carrier-Versandetiketten (DHL etc.) im Drucken-Menü mit IoT-Drucker-Unterstützung',
    'description': """
Versandetiketten Drucken
========================

Fügt "Versandetiketten" ins Drucken-Menü des Lieferauftrags ein.

- Zahnrad → Drucken → Versandetiketten (IoT-kompatibel, wie Lieferschein)
- Zahnrad → Aktionen → Versandetiketten (PDF-Download) als Direktlink
- Nutzt pypdf um DHL-PDFs direkt durchzureichen (kein wkhtmltopdf-Rendering)
- Unterstützt mehrere Labels pro Picking (werden zusammengeführt)
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
        'report/carrier_label_action.xml',
        'report/carrier_label_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
