# -*- coding: utf-8 -*-
import io
import base64
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class CarrierLabelController(http.Controller):
    """
    Controller der alle Carrier-Label-PDFs eines Pickings zu einem
    einzigen PDF zusammenführt und direkt zurückgibt.

    Route: /bs/carrier_label/<int:picking_id>

    Wird von der ir.actions.act_url Server-Action aufgerufen.
    Der Download-Response verhält sich wie ein normaler Report-Download.
    IoT-Drucken: Läuft über den standard Odoo report-Mechanismus,
    siehe models/stock_picking.py → action_print_carrier_labels()
    """

    @http.route(
        '/bs/carrier_label/<int:picking_id>',
        type='http',
        auth='user',
        methods=['GET'],
    )
    def download_carrier_labels(self, picking_id, **kwargs):
        picking = request.env['stock.picking'].sudo().browse(picking_id)

        if not picking.exists():
            return Response('Lieferauftrag nicht gefunden.', status=404)

        # Zugriffsprüfung: Nutzer muss Lesezugriff auf das Picking haben
        picking_user = request.env['stock.picking'].browse(picking_id)
        if not picking_user.exists():
            return Response('Zugriff verweigert.', status=403)

        try:
            pdf_bytes = picking.sudo()._merge_carrier_label_pdfs()
        except Exception as e:
            _logger.error(
                'Fehler beim Zusammenführen der Carrier-Labels für Picking %s: %s',
                picking.name, str(e)
            )
            return Response(
                f'Fehler: {str(e)}',
                status=500,
                content_type='text/plain; charset=utf-8',
            )

        filename = f'Versandetikett-{picking.name or picking_id}.pdf'

        return Response(
            pdf_bytes,
            status=200,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'inline; filename="{filename}"'),
                ('Content-Length', str(len(pdf_bytes))),
            ],
        )
