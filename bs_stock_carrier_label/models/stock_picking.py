# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError

# Schlüsselwörter zur Erkennung von Carrier-Label-Anhängen.
# Ergänze hier weitere Carrier-Namen falls nötig (Großschreibung, wird mit .upper() verglichen).
CARRIER_LABEL_KEYWORDS = [
    'LABEL',
    'DHL',
    'UPS',
    'DPD',
    'HERMES',
    'GLS',
    'FEDEX',
    'TNT',
    'SCHENKER',
    'DACHSER',
]

# Unterstützte Mimetypes für Carrier-Label-Anhänge
CARRIER_LABEL_MIMETYPES = [
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/tiff',
]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_carrier_label_attachments(self):
        """
        Gibt alle Carrier-Label-Anhänge dieses Pickings als Recordset zurück.

        Wird vom QWeb-Report-Template aufgerufen.
        Sucht in ir.attachment nach Anhängen, die:
          1. Am Picking hängen (res_model=stock.picking, res_id=self.id)
          2. Ein unterstütztes Mimetype haben (PDF oder Bild)
          3. Einen Carrier-Keyword im Namen enthalten (DHL, UPS, LABEL, ...)

        Wirft UserError wenn keine Labels vorhanden sind, damit der
        Nutzer eine klare Rückmeldung bekommt statt eines leeren PDFs.
        """
        self.ensure_one()

        all_attachments = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'stock.picking'),
            ('res_id', '=', self.id),
            ('mimetype', 'in', CARRIER_LABEL_MIMETYPES),
        ])

        carrier_attachments = all_attachments.filtered(
            lambda a: any(
                keyword in (a.name or '').upper()
                for keyword in CARRIER_LABEL_KEYWORDS
            )
        )

        if not carrier_attachments:
            raise UserError(_(
                'Keine Versandetiketten für %(picking)s gefunden.\n\n'
                'Bitte erstelle zunächst ein Versandetikett über den Zusteller '
                '(z.B. DHL-Connector → "Etikett erstellen").\n\n'
                'Falls du ein Etikett erwartest, prüfe ob der Dateiname eines '
                'der folgenden Schlüsselwörter enthält:\n%(keywords)s',
                picking=self.name,
                keywords=', '.join(CARRIER_LABEL_KEYWORDS),
            ))

        return carrier_attachments

    @api.model
    def _get_carrier_label_keywords(self):
        """Gibt die Liste der Carrier-Keywords zurück (für das Template nutzbar)."""
        return CARRIER_LABEL_KEYWORDS
