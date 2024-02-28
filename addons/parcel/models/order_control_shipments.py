# -*- coding: utf-8 -*-

from odoo import models, fields, api

class order_control_shipments(models.Model):
    _inherit = 'sale.order'

    name = fields.Char()

