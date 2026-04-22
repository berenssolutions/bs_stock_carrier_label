# -*- coding: utf-8 -*-
import io
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """
        Override nur für unseren Carrier-Label-Report.
        Anstatt wkhtmltopdf zu nutzen, holen wir das echte Carrier-PDF
        direkt via pypdf aus den ir.attachment-Datensätzen.

        Für alle anderen Reports: normales Verhalten (super()).
        """
        report = self._get_report(report_ref)

        if report.report_name != 'bs_stock_carrier_label.report_carrier_label':
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        # Unser Report: Carrier-Labels direkt als PDF zusammenführen
        if not res_ids:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        try:
            from pypdf import PdfWriter
        except ImportError:
            _logger.error('pypdf nicht installiert — Fallback auf Standard-Render')
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        writer = PdfWriter()
        pickings = self.env['stock.picking'].browse(res_ids)

        for picking in pickings:
            try:
                pdf_bytes = picking._merge_carrier_label_pdfs()
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(pdf_bytes))
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                _logger.error(
                    'Carrier-Label für Picking %s konnte nicht geladen werden: %s',
                    picking.name, str(e)
                )
                raise

        output = io.BytesIO()
        writer.write(output)
        pdf_content = output.getvalue()

        # Rückgabe: (pdf_bytes, 'pdf') — identisch zum Standard-Return
        return pdf_content, 'pdf'
