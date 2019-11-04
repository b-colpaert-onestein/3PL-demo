# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = ['barcodes.barcode_events_mixin', 'stock.picking']
    _name = 'stock.picking'

    def action_barcode_scan(self):
        action = self.env.ref(
            '3plplus_stock_barcode_gs1.action_stock_barcodes_read_picking').read()[0]
        action['context'] = {
            'default_location_id': self.location_id.id,
            'default_product_id': self.product_id.id,
            'default_partner_id': self.partner_id.id,
            'default_picking_id': self.id,
            'default_res_model_id':
                self.env.ref('stock.model_stock_picking').id,
            'default_res_id': self.id,
        }
        return action
