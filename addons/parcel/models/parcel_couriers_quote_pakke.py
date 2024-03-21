# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from  odoo.exceptions import ValidationError#Para las alertas de usuario

# Define the logger
_logger = logging.getLogger(__name__)

class parcel_couriers_quote_pakke(models.Model):
    _name= 'parcel.couriers_quote_pakke'
    _description = 'parcel.couriers_quote_pakke'

    #Campos para la cotizacion de la api de pakke
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
    best_option = fields.Boolean(string="Mejor opción")
    
    id_shipments = fields.Many2one("sale.order")
    
    record_selection = fields.Boolean(default=False)#Para saber si ya un registro fue seleccionado
    
    validation_guide = fields.Boolean(default=False)#Para validar si ya se realizo la guia de envio
    
    #Funcion para selecionar un registro
    def couriers_selection(self):
        for record in self.id_shipments.id_couriers_table:#Primero vuelvo False a todos los registros de la tabla del One2many
            
            record.record_selection = False
        
        self.record_selection = True #Aqui vuelvo True al registro que seleccione
        
        self.id_shipments.id_couriers_selection = self#Y le paso al valor selecionado al many2one
        