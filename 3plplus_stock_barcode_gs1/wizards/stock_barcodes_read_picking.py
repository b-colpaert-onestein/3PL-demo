# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class WizStockBarcodesReadPicking(models.TransientModel):
    _name = 'wiz.stock.barcodes.read.picking'
    _inherit = 'wiz.stock.barcodes.read'
    _description = 'Wizard to read barcode on pickings'

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        readonly=True,
    )
    owner_id = fields.Many2one('res.partner')
    sell_date = fields.Date()
    expiration_date = fields.Date()
    lot_string = fields.Char('Lot')
    package_id = fields.Many2one('stock.quant.package')
    scan_log_ids = fields.Many2many(
        comodel_name='stock.barcodes.read.log',
        compute='_compute_scan_log_ids',
    )
    picking_line_ids = fields.One2many(
        'stock.move.line',
        related='picking_id.move_line_ids',
    )

    def name_get(self):
        return [
            (rec.id, '{} - {} - {}'.format(
                _('Barcode reader'),
                rec.picking_id.name, self.env.user.name)) for rec in self]

    def on_barcode_scanned(self, barcode):
        self.barcode = barcode
        self.process_barcode(barcode)
        self._add_read_log()
        self._check_confirm_line()

    def process_barcode(self, barcode):
        self._set_messagge_info('success', _('Barcode read correctly'))
        if not self.process_barcode_gs1(barcode):
            self._set_messagge_info('not_found', _('Barcode not found'))

    def process_barcode_gs1(self, barcode):
        try:
            gs1_barcode = self.env['gs1_barcode'].decode(barcode)
        except Exception:
            return False
        if gs1_barcode.get('00'):
            # is SSCC
            self.is_gs1_sscc_decode(gs1_barcode.get('00'))
        if gs1_barcode.get('02'):
            self.is_gs1_content_gtin_decode(gs1_barcode.get('02'))
        if gs1_barcode.get('37'):
            self.is_gs1_content_qty_decode(gs1_barcode.get('37'))
        if gs1_barcode.get('15'):
            self.is_gs1_sell_date_decode(gs1_barcode.get('15'))
        if gs1_barcode.get('17'):
            self.is_gs1_expiration_date_decode(gs1_barcode.get('17'))
        if gs1_barcode.get('10'):
            self.is_gs1_lot_decode(gs1_barcode.get('10'))
        return True

    def _check_confirm_line(self):
        if self.picking_id and self.product_id and self.lot_string and self.package_id:
            self._add_move_in_picking()
            self.clean_all()

    def clean_all(self):
        self.product_id = False
        self.product_qty = False
        self.owner_id = False
        self.lot_string = False
        self.sell_date = False
        self.expiration_date = False
        self.package_id = False

    def is_gs1_sscc_decode(self, sscc):
        extension_digit = sscc[0]
        if extension_digit == '3':
            # is SSCC ((Nummer der Versandeinheit NVE)
            prfx = sscc[1:3]
            if prfx == '40':
                company_prefix = sscc[1:8]  # 7 characters, is the company
                logistic_unit = sscc[8:17]  # 9 characters, is the container
                # GTIN should be company_prefix + 'xxxxx' + 'x'
            elif prfx == '42':
                company_prefix = sscc[1:9]  # 8 characters
                logistic_unit = sscc[9:17]  # 8 characters
                # GTIN should be company_prefix + 'xxxx' + 'x'
            elif prfx == '43':
                company_prefix = sscc[1:10]  # 9 characters
                logistic_unit = sscc[10:17]  # 7 characters
                # GTIN should be company_prefix + 'xxx' + 'x'
        elif extension_digit == '0':
            # is package
            company_prefix = sscc[1:8]  # 7 characters, is the company
            logistic_unit = sscc[8:17]  # 9 characters, is the container
        else:
            return False

        package = self.env['stock.quant.package'].search([('name', '=', sscc)], limit=1)
        if not package:
            package = self.env['stock.quant.package'].create({
                'name': sscc,
            })
        self.package_id = package
        owner = self.env['res.partner'].search([('barcode', '=', company_prefix)], limit=1)
        if owner:
            if self.product_id and self.owner_id:
                if self.owner_id != owner:
                    self._set_messagge_info('not_found', _('Owner not corresponding to the selected product.'))
            else:
                self.owner_id = owner
        if not self.product_id:
            self._set_messagge_info('info', _('Waiting product and quantity'))
        return True

    def is_gs1_content_gtin_decode(self, code):
        prfx = code[0:2]
        if prfx == '00':
            # GTIN-12
            gtin = code[2:]
            company_prefix = gtin[:7]  # 7 characters, is the company
            ean_product = gtin[7:12]
        elif prfx[0] == '0':
            # GTIN-13
            gtin = code[1:]
            company_prefix = gtin[:7]  # 7 characters, is the company
            ean_product = gtin[7:13]
        else:
            # GTIN-14
            gtin = code
            company_prefix = gtin[:7]  # 7 characters, is the company
            ean_product = gtin[7:14]
        owner = self.env['res.partner'].search([('barcode', '=', company_prefix)], limit=1)
        if owner:
            self.owner_id = owner
        # Logic for products
        product = self.env['product.product'].search(['|', ('barcode', '=', gtin), ('default_code', '=', gtin)], limit=1)
        if product:
            self.product_id = product
        else:
            product = self.env['product.product'].search(['|', ('barcode', '=', code), ('default_code', '=', code)], limit=1)
            if product:
                self.product_id = product
        if not self.product_id:
            self._set_messagge_info('not_found', _('Barcode for product not found'))
            return False
        return True

    def is_gs1_content_qty_decode(self, product_qty):
        qty = int(product_qty)
        self.product_qty = qty
        return True

    def is_gs1_sell_date_decode(self, date):
        format_date = self._gs1_date_decode(date)
        self.sell_date = format_date
        return True

    def is_gs1_expiration_date_decode(self, date):
        format_date = self._gs1_date_decode(date)
        self.expiration_date = format_date
        return True

    def _gs1_date_decode(self, date):
        if len(date) == 10:
            format_date = date
        else:
            year = '20' + date[:2]
            month = date[2:4]
            day = date[4:6]
            format_date = '-'.join([year, month, day])
        return format_date

    def is_gs1_lot_decode(self, lot_string):
        if not self.product_id:
            self._set_messagge_info('info', _('Waiting product and quantity'))
        self.lot_string = lot_string
        return True

    def _add_create_lot(self):
        if not self.product_id:
            return
        lot_string = self.lot_string
        lot = self.env['stock.production.lot'].search([
            ('name', '=', lot_string),
            ('product_id', '=', self.product_id.id)
        ], limit=1)
        if not lot:
            lot = self.env['stock.production.lot'].create({
                'name': lot_string,
                'ref': lot_string,
                'product_id': self.product_id.id,
            })
        if self.sell_date:
            lot.alert_date = fields.Datetime.to_datetime(self.sell_date)
        if self.expiration_date:
            lot.use_date = fields.Datetime.to_datetime(self.expiration_date)
        self.lot_id = lot

    def _add_move_in_picking(self):
        self.ensure_one()
        if not self.picking_id:
            self._set_messagge_info('not_found', _('Corresponding picking not found! Select a picking first.'))
            return
        if not self.product_id:
            self._set_messagge_info('not_found', _('No product found in the system. Waiting product and quantity.'))
            return
        self._add_create_lot()

        if self.picking_id.state == 'draft':
            self.picking_id.action_confirm()
        self._create_picking_move_ready()

    def _create_picking_move_ready(self):
        picking = self.picking_id
        product = self.product_id
        qty = self.product_qty
        move_line = picking.move_line_ids_without_package.filtered(lambda ml: ml.product_id == product and ml.qty_done == 0.0)
        if not move_line:
            move_line = picking.move_line_ids.create({
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'qty_done': qty,
                'product_uom_qty': qty,
                'date': fields.datetime.now(),
                'picking_id': picking.id,
                'result_package_id': self.package_id.id,
                'owner_id': self.owner_id.id,
                'lot_id': self.lot_id.id,
            })
            picking.move_line_ids_without_package += move_line
        else:
            move_line.write({
                'result_package_id': self.package_id.id,
                'owner_id': self.owner_id.id,
                'lot_id': self.lot_id.id,
                'qty_done': qty,
            })

        if not move_line.move_id:
            move = self.env['stock.move'].create({
                'name': _('New Move:') + move_line.product_id.display_name,
                'product_id': move_line.product_id.id,
                'product_uom_qty': qty,
                'product_uom': move_line.product_uom_id.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'picking_id': picking.id,
            })
            move.move_line_ids += move_line
            move_line.write({'move_id': move.id})

    def action_done(self):
        result = super().action_done()
        if result:
            self._add_move_in_picking()
            self.clean_all()
        return result

    def action_manual_entry(self):
        if not self.picking_id:
            self._set_messagge_info('not_found', _('Corresponding picking not found! Select a picking first.'))
            return
        result = super().action_manual_entry()
        if result:
            self.action_done()
        return result

    @api.depends('picking_id', 'lot_string', 'sell_date', 'package_id')
    def _compute_scan_log_ids(self):
        logs = self.env['stock.barcodes.read.log'].search([
            ('res_model_id', '=', self.res_model_id.id),
            ('res_id', '=', self.picking_id.id),
        ], limit=10)
        self.scan_log_ids = logs
