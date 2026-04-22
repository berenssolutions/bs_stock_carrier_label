# -*- coding: utf-8 -*-
import io
import base64
import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class ReportCarrierLabel(models.AbstractModel):
    """
    Odoo-Standard-Pattern für Custom-Reports:
    Ein AbstractModel mit _name='report.<module>.<report_name>'
    wird automatisch vom Report-Framework aufgerufen.

    _get_report_values() liefert den Render-Kontext für das QWeb-Template.
    Wir nutzen es zusätzlich, um das fertige PDF via pypdf zusammenzuführen
    und im Kontext bereitzustellen.

    Der eigentliche PDF-Bypass passiert über _render_qweb_pdf auf
    ir.actions.report — aber NUR für unseren spezifischen Report,
    identifiziert über den _name des AbstractModels.
    """
    _name = 'report.bs_stock_carrier_label.report_carrier_label'
    _description = 'Report: Versandetiketten'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Wird vom QWeb-Framework aufgerufen um Template-Variablen zu liefern.
        Hier geben wir die Picking-Records und vorberechnete Label-Daten zurück.
        """
        pickings = self.env['stock.picking'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': pickings,
            'data': data,
        }


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """
        Override: Für unseren Carrier-Label-Report das DHL-PDF direkt
        via pypdf durchreichen, ohne wkhtmltopdf zu nutzen.

        Für alle anderen Reports: Standard-Verhalten (super()).
        """
        # Report-Objekt ermitteln — _get_report() akzeptiert report_ref
        # als XML-ID-String, Datenbank-ID oder ir.actions.report-Record
        try:
            report = self._get_report(report_ref)
        except Exception:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        if report.report_name != 'bs_stock_carrier_label.report_carrier_label':
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        # Ab hier: unser Carrier-Label-Report
        if not res_ids:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        try:
            from pypdf import PdfWriter, PdfReader
        except ImportError:
            _logger.error('pypdf nicht installiert — Fallback auf Standard-Render')
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        pickings = self.env['stock.picking'].browse(res_ids)
        writer = PdfWriter()

        for picking in pickings:
            pdf_bytes = picking._merge_carrier_label_pdfs()
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        return output.getvalue(), 'pdf'
