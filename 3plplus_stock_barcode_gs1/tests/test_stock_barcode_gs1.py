# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.tests.common import TestStockCommon
from odoo.tests import Form


class TestStockBarcodeGS1(TestStockCommon):

    def setUp(self):
        super().setUp()

        self.picking_in = self.PickingObj.create({
            'partner_id': self.partner_delta_id,
            'picking_type_id': self.picking_type_in,
            'location_id': self.supplier_location,
            'location_dest_id': self.stock_location})
        Wizard = self.env['wiz.stock.barcodes.read.picking'].with_context(
            default_picking_id=self.picking_in.id,
        )
        self.wizard_form = Form(Wizard)

    def test_01(self):
        self.wizard_form._barcode_scanned = '020400017702045637000081'
        self.assertFalse(self.wizard_form._barcode_scanned)
        self.assertTrue(self.wizard_form.product_id)
        self.assertFalse(self.wizard_form.lot_string)
        self.assertFalse(self.wizard_form.package_id)
        self.wizard_form._barcode_scanned = '15200814101187948'
        self.assertFalse(self.wizard_form._barcode_scanned)
        self.assertTrue(self.wizard_form.product_id)
        self.assertTrue(self.wizard_form.lot_string)
        self.assertFalse(self.wizard_form.package_id)
        self.wizard_form._barcode_scanned = '00340001770391591833'
        self.assertFalse(self.wizard_form._barcode_scanned)
        self.assertFalse(self.wizard_form.product_id)
        self.assertFalse(self.wizard_form.lot_string)
        self.assertFalse(self.wizard_form.package_id)

        self.wizard_form._barcode_scanned = '020400017702045637000081'
        self.assertFalse(self.wizard_form._barcode_scanned)
        self.assertTrue(self.wizard_form.product_id)
        self.assertFalse(self.wizard_form.lot_string)
        self.assertFalse(self.wizard_form.package_id)
        self.wizard_form._barcode_scanned = '15200814101187948'
        self.assertFalse(self.wizard_form._barcode_scanned)
        self.assertTrue(self.wizard_form.product_id)
        self.assertTrue(self.wizard_form.lot_string)
        self.assertFalse(self.wizard_form.package_id)
        self.wizard_form._barcode_scanned = '00340001770391591833'
        self.assertFalse(self.wizard_form._barcode_scanned)
        self.assertFalse(self.wizard_form.product_id)
        self.assertFalse(self.wizard_form.lot_string)
        self.assertFalse(self.wizard_form.package_id)

        wizard = self.wizard_form.save()
        picking = wizard.picking_id
        moves = picking.move_lines
        move_lines = picking.move_line_ids
        self.assertEqual(len(moves), 2)
        self.assertEqual(len(move_lines), 2)
        move_line1 = move_lines[0]
        move_line2 = move_lines[1]
        self.assertTrue(move_line1.move_id)
        self.assertTrue(move_line2.move_id)
