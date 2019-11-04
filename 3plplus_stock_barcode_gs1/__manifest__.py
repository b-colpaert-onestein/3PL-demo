# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': '3PL+ - Stock Barcode GS1',
    'summary': '3PL+ - Stock Barcode GS1',
    'author': 'Onestein',
    'website': 'https://www.onestein.eu',
    'category': 'Technical Settings',
    'version': '12.0.1.0.0',
    'depends': [
        'stock_barcode',
        'base_gs1_barcode',
        'stock_barcodes',
        'product_expiry',  # for field date in lot
    ],
    'demo': [
        'demo/product_product_demo.xml',
    ],
    'data': [
        'views/stock_picking.xml',
        'wizards/stock_barcodes_read_picking.xml',
    ],
    'installable': True,
}
