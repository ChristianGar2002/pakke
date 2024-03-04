# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

# Define the logger
_logger = logging.getLogger(__name__)

class parcel_pakke(models.Model):
    _name= 'parcel.pakke'
    _description = 'parcel.pakke'

    name_shipments = fields.Char(string="Nombre del registro")
    courier_code = fields.Char(string="Codigo de mensajeria")
    name = fields.Char(string="Nombre de mensajeria")
    courier_service_id = fields.Char(string="Id del servicio de mensajeria")
    courier_service_name = fields.Char(string="Nombre del servicio de mensajeria")
    delivery_days = fields.Char(string="Días de entrega")
    coupon_code = fields.Char(string="Codigo de cupon")
    discount_amount = fields.Char(string="Importe de descuento")
    total_price = fields.Char(string="Precio total")
    estimated_delivery_date = fields.Char(string="Fecha estimada de entrega")
    best_option = fields.Char(string="Mejor opción")
    
    id_shipments = fields.Many2one("sale.order")