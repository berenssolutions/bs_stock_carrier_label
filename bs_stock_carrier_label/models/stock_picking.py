# -*- coding: utf-8 -*-
import io
import base64
import logging

from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Schlüsselwörter zur Erkennung von Carrier-Label-Anhängen (Großschreibung).
# Ergänze hier weitere Carrier-Namen falls nötig.
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

CARRIER_LABEL_MIMETYPES = [
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/tiff',
]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_carrier_label_attachments(self):
        """
        Gibt alle Carrier-Label-Anhänge dieses Pickings zurück.
        Wirft UserError wenn keine gefunden werden.
        """
        self.ensure_one()

        all_attachments = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'stock.picking'),
            ('res_id', '=', self.id),
            ('mimetype', 'in', CARRIER_LABEL_MIMETYPES),
        ])

        carrier_attachments = all_attachments.filtered(
            lambda a: any(
                kw in (a.name or '').upper()
                for kw in CARRIER_LABEL_KEYWORDS
            )
        )

        if not carrier_attachments:
            raise UserError(_(
                'Keine Versandetiketten für %(picking)s gefunden.\n\n'
                'Bitte erstelle zunächst ein Versandetikett über den '
                'Zusteller (z.B. DHL-Connector → "Etikett erstellen").\n\n'
                'Erkannte Carrier-Keywords: %(keywords)s',
                picking=self.name,
                keywords=', '.join(CARRIER_LABEL_KEYWORDS),
            ))

        return carrier_attachments

    def _merge_carrier_label_pdfs(self):
        """
        Führt alle Carrier-Label-Anhänge zu einem einzigen PDF zusammen.
        Nutzt pypdf (Odoo 18 Standard-Dependency).

        Gibt das fertige PDF als bytes zurück.
        Wirft UserError wenn keine Labels vorhanden.
        Wirft Exception bei PDF-Verarbeitungsfehlern.
        """
        self.ensure_one()

        try:
            from pypdf import PdfWriter, PdfReader
        except ImportError:
            raise UserError(_(
                'pypdf ist nicht installiert. '
                'Bitte führe "pip install pypdf" auf dem Odoo-Server aus.'
            ))

        attachments = self._get_carrier_label_attachments()
        writer = PdfWriter()
        pages_added = 0

        for attachment in attachments:
            raw = base64.b64decode(attachment.datas or b'')
            if not raw:
                _logger.warning(
                    'Carrier-Label-Anhang %s (%s) ist leer, wird übersprungen.',
                    attachment.name, attachment.id
                )
                continue

            if attachment.mimetype == 'application/pdf':
                try:
                    reader = PdfReader(io.BytesIO(raw))
                    for page in reader.pages:
                        writer.add_page(page)
                        pages_added += 1
                except Exception as e:
                    _logger.error(
                        'Fehler beim Lesen von PDF-Anhang %s: %s',
                        attachment.name, str(e)
                    )
                    raise UserError(_(
                        'Das Versandetikett "%(name)s" konnte nicht gelesen werden: %(error)s',
                        name=attachment.name,
                        error=str(e),
                    ))
            else:
                # Bild-Anhänge (PNG/JPEG): als PDF-Seite einbetten
                try:
                    from pypdf import PageObject
                    from pypdf.generic import (
                        ArrayObject, FloatObject, NameObject,
                        IndirectObject, DictionaryObject,
                    )
                    # Bild-zu-PDF via reportlab wenn vorhanden, sonst überspringen
                    try:
                        from reportlab.lib.pagesizes import A6
                        from reportlab.platypus import SimpleDocTemplate, Image as RLImage
                        from reportlab.lib.units import mm
                        import PIL.Image

                        img = PIL.Image.open(io.BytesIO(raw))
                        img_w, img_h = img.size
                        # DHL A6: 105x148mm
                        page_w, page_h = 105 * mm, 148 * mm
                        ratio = min(page_w / img_w, page_h / img_h)

                        img_buf = io.BytesIO()
                        doc = SimpleDocTemplate(
                            img_buf,
                            pagesize=(page_w, page_h),
                            leftMargin=0, rightMargin=0,
                            topMargin=0, bottomMargin=0,
                        )
                        rl_img = RLImage(
                            io.BytesIO(raw),
                            width=img_w * ratio,
                            height=img_h * ratio,
                        )
                        doc.build([rl_img])
                        img_buf.seek(0)
                        reader = PdfReader(img_buf)
                        for page in reader.pages:
                            writer.add_page(page)
                            pages_added += 1
                    except ImportError:
                        _logger.warning(
                            'reportlab/PIL nicht verfügbar — Bild-Anhang %s wird übersprungen.',
                            attachment.name
                        )
                except Exception as e:
                    _logger.warning(
                        'Bild-Anhang %s konnte nicht eingebettet werden: %s',
                        attachment.name, str(e)
                    )

        if pages_added == 0:
            raise UserError(_(
                'Es konnten keine Seiten aus den Versandetiketten gelesen werden.'
            ))

        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()

    def action_print_carrier_labels(self):
        """
        Server-Action-Einstiegspunkt: Gibt eine act_url zurück, die das
        zusammengeführte Carrier-Label-PDF im Browser öffnet.

        Wird als ir.actions.server mit binding_model_id=stock.picking
        und binding_type=action registriert → erscheint im Zahnrad-Menü.

        Für IoT-Druck: Den Report "Versandetiketten" (ir.actions.report)
        in den IoT-Drucker-Einstellungen hinterlegen. Der Report nutzt
        denselben Controller-Endpunkt.
        """
        self.ensure_one()
        # Vorab prüfen ob Labels existieren → UserError sofort, nicht erst beim Download
        self._get_carrier_label_attachments()

        return {
            'type': 'ir.actions.act_url',
            'url': f'/bs/carrier_label/{self.id}',
            'target': 'new',
        }
