
========================
3PL+ - Stock Barcode GS1
========================

This module is compatible with the latest version of "stock_barcodes".

Configuration
=============

Enable:
 - Barcode Scanner
 - Delivery Packages
 - Expiration Dates
 - Consignment
 - Lots & Serial Numbers
 - Storage Locations

In Picking Type Receipt: enable "Show Detailed Operations".

Products must be set with Tracking= By Lots.

To be verified:
 - Field SELL_BY_DATE is in lot, with name "alert_date" and defined in module product_expiry.

Usage
=====

Create a receipt picking in draft.
Click on Scan GS1.
Scan the three GS1 barcodes, with the following order:

- Product ad Quantity.
- Sell date and Lot.
- NVE (SSCC)

Once all the three GS1 barcodes are scanned, the picking line is created.


Roadmap
=======

The AI's implemented are 00(SSCC), 02(Product), 37(Quantity), 15(Sell Date),
17(Expiration Date) and 10(Lots).
