# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import base64 #Para los pdf
from odoo.exceptions import ValidationError#Para las alertas de usuario
#Para hacer peticiones
import requests
import json

# Define the logger
_logger = logging.getLogger(__name__)

class order_control_shipments_pakke(models.Model):
    _inherit = "sale.order"

    courier_code = fields.Char(string="Codigo de mensajeria", compute="quote_table_data")
    courier_service_id = fields.Char(string="Id del servicio de mensajeria", compute="quote_table_data")
    reseller_reference = fields.Char(string="Referencia personalizada del paquete",compute="get_data_shipments", readonly=False)#Para darle valor a los demas campos de manera automatica
    reseller_reference_parcel = fields.Char(string="Referencia personalizada del paquete", required=True)
    content = fields.Char(string="Contenido del paquete", required=True)
    coupon_code = fields.Char(string="Codigo de cupón")
    insured_amount = fields.Float(string="Valor declarado del paquete", required=True, help="Precio del contenido del paquete")
    
    #Campos para la parte del Dirección​ ​de​ ​Envío
    address_from_zipcode = fields.Char(string="Código Postal", required=True)
    address_from_state = fields.Char(string="Estado", required=True)
    address_from_city = fields.Char(string="Ciudad", required=True)
    address_from_neighborhood = fields.Char(string="Vecindario", required=True, help="Colonia")
    address_from_address1 = fields.Char(string="Dirección", required=True, help="Ingresa calle y número")
    address_from_address2 = fields.Char(string="Referencias de dirección", required=True, help="Ingresa datos adicionales sobre la dirección (Negocios cercanos, etc)")
    address_from_residential = fields.Boolean(string="Residencial", required=True, help="Selecciona si es un departamento, condominio, etc...")
    
    #Campos para la parte del Dirección de entrega
    address_to_zipcode = fields.Char(string="Código Postal", required=True)
    address_to_state = fields.Char(string="Estado", required=True)
    address_to_city = fields.Char(string="Ciudad", required=True)
    address_to_neighborhood = fields.Char(string="Vecindario", required=True, help="Colonia")
    address_to_address1 = fields.Char(string="Dirección", required=True, help="Ingresa calle y número")
    address_to_address2 = fields.Char(string="Referencias de dirección", required=True, help="Ingresa datos adicionales sobre la dirección (Negocios cercanos, etc)")
    address_to_residential = fields.Boolean(string="Residencial", required=True, help="Selecciona si es un departamento, condominio, etc...")
    
    #Campos para la parte del paquete
    parcel_length = fields.Integer(string="Longitud (cm)", required=True, default=1)
    parcel_width = fields.Integer(string="Ancho (cm)", required=True, default=1)
    parcel_height = fields.Integer(string="Altura (cm)", required=True, default=1)
    parcel_weight = fields.Float(string="Peso (kg)", required=True, default=1, help="Utiliza la sintaxis de la coma para los kilos con gramos (1,20) 1 kilo y 200 gramos")
    
    #Campos para la parte del remitente
    sender_name = fields.Char(string="Nombre", required=True)
    sender_phone1 = fields.Char(string="Telefono", required=True)
    sender_phone2 = fields.Char(string="Telefono adicional", required=True)
    sender_email = fields.Char(string="Correo electronico", required=True)
    
    #Campos para la parte del destinatario
    recipient_name = fields.Char(string="Nombre", required=True)
    recipient_company_name = fields.Char(string="Nombre de la empresa", required=True)
    recipient_phone1 = fields.Char(string="Telefono", required=True)
    recipient_email = fields.Char(string="Correo electronico", required=True)
    
    #Campos relacionados con quote_couriers
    id_couriers_selection = fields.Many2one("parcel.couriers_quote_pakke", string="Selecciona al mensajero", domain="[('name_shipments', '=', name_orders)]")
    id_couriers_table = fields.One2many("parcel.couriers_quote_pakke", "id_shipments", string="Tabla de cotización")
    name_orders = fields.Char(string="Nombre del pedido")#Campo para filtrar por nombre de pedidos
    test_table_pdf = fields.One2many("parcel.test", "id_shipments", string="Tabla de pdfs")
    
    #Credencial oficial de la api de PAKKE
    api_key_pakke = fields.Char(string="Api", compute="get_data_shipments")
    
    #Campos relacionados package_dimensions
    id_packages = fields.Many2one("parcel.package_dimensions", string="Selecciona una medida de paquete")
    
    #Campo para validar si ya se realizo la guia de envio
    validation_guide = fields.Boolean(default=False)
    
    @api.onchange("sender_phone1", "sender_phone2", "recipient_phone1")
    def validation_number(self):#Funcion para validar que los campos de telefono solo se han numericos
        
        for field_number in self:
            
            if field_number.sender_phone1 and not field_number.sender_phone1.isdigit():
                
                raise ValidationError(("El campo 'Telefono' del remitente es de solo números"))
            
            elif field_number.sender_phone2 and not field_number.sender_phone2.isdigit():
                
                raise ValidationError(("El campo 'Telefono adicional' del remitente es de solo números"))
            
            elif field_number.recipient_phone1 and not field_number.recipient_phone1.isdigit():
                
                raise ValidationError(("El campo 'Telefono' del destinatario es de solo números"))
    
    @api.onchange("name")
    def get_data_shipments(self):#Funcion para obtener los datos que ya estan registrados
        if not self.env['parcel.check'].search([('name', '=', self.name)], limit=1):#Busco si el registro actual de sale.order ya esta registrado    
            self.reseller_reference_parcel = self.partner_id.name
            self.content = self.user_id.name
            self.coupon_code = self.team_id.name

            self.env['parcel.check'].create({'name': self.name})#Si no esta lo creo
        
        Param = self.env['ir.config_parameter']#Creo una instancia del modelo de los parametros del sistema
        api_key = Param.get_param('APIKEY_PAKKE', default='')#Obtengo la api key de la instancia anterior
        
        self.api_key_pakke = api_key
            
        self.data_package_dimension()
        
    @api.onchange("partner_id")
    def get_data_shipments_update(self):#Funcion para actualizar los datos obtenidos
        
        self.reseller_reference_parcel = self.partner_id.name
    
    def data_package_dimension(self):#Funcion para registrar medidas estandar de packetes
        
        new_dimension = []
        dimensions = [{'name':'Pequeño (25x15x5)', 'length':25, 'width':15, 'height':5}, {'name':'Mediano (40x30x20)', 'length':40, 'width':30, 'height':20}, {'name':'Grande (55x45x35)', 'length':55, 'width':45, 'height':35}]
        
        for dimension in dimensions:#Recorro la lista de las medidas estandar para capturar los datos
            
            dimension_name=dimension['name']
            dimension_length=dimension['length']
            dimension_width=dimension['width']
            dimension_height=dimension['height']
            
            search_dimension = self.env['parcel.package_dimensions'].search([('name', '=', dimension_name), ('length', '=', dimension_length), ('width', '=', dimension_width), ('height', '=', dimension_height)], limit=1)#Busco para saber si existe un registro ya
            
            if not search_dimension:  # Si la medida no existe
                new_dimension.append({  # Agrego la nueva medida a la lista
                    'name': dimension_name,
                    'length': dimension_length,
                    'width': dimension_width,
                    'height': dimension_height,
                })
                
        if new_dimension:  # Si hay nuevas medidas
            with self.env.cr.savepoint():  # Crea un punto de guardado en la transacción de base de datos actual, ayuda a que si hay un error no realize nada para tener consistencia de datos
                self.env['parcel.package_dimensions'].create(new_dimension)  # Crea nuevas medidas

    @api.onchange("id_packages")
    def data_dimensions_parcel(self):#Funcion que coloca los datos cuando se selecciona una medida de id_packages
        
        self.parcel_length = self.id_packages.length
        self.parcel_width = self.id_packages.width
        self.parcel_height = self.id_packages.height
        
    @api.onchange("id_couriers_selection")
    def couriers_selection_reverse(self):#Funcion para actualizar el campo id_couriers_table si se elije directamente el courier desde el campo id_courier_selection
        
        id_courier_selection = (f"NewId_{self.id_couriers_selection.id}")#Convierto en string el id del registro actual del id_couriers_selection
        
        for record_quote in self.id_couriers_table:#Recorro cada registro del One2many del id_couriers_table
            
            record_quote.record_selection = False#Vuelvo False a todos los record_selection del id_couriers_table
            
            if id_courier_selection == f"{record_quote.id}":#Busco si el registro seleccionado del id_couriers_selection es igual al que esta en el One2many de id_couriers_table
                
                record_quote.record_selection = True#Si es asi, le coloco True al record_selection del registro pertinente del campo One2many de id_couriers_table
   
        
    def quote(self):#Funcion para cotizar la api de pakke
        #Almaceno el nombre de cada registro del modelo
        name_shipments = self.name
        new_quotes = []
        #Consulta a la pai de pakke para cotizar
        url = "https://seller.pakke.mx/api/v1/Shipments/rates"#Endpoint para generar envios
    
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.api_key_pakke}",
            "Accept": "application/json"
        }
        body = {
                "ZipCodeFrom": self.address_from_zipcode,
                "ZipCodeTo": self.address_to_zipcode,
                "Parcel": {
                    "Weight": self.parcel_weight,
                    "Width": self.parcel_width,
                    "Height": self.parcel_height,
                    "Length": self.parcel_length
                },
                "CouponCode": self.coupon_code,
                "InsuredAmount": self.insured_amount
            }
        
        try:
            json_body = json.dumps(body)#Se convierte a json

            #Se realiza la petición
            response = requests.post(url, headers=headers, data=json_body)
            
            #Si la petición es correcta
            quotes_data = response.json()#Obtengo la respuesta de la peticion
            _logger.info(f"Cotizaciones {quotes_data}")
            #Obtengo los datos de la api
            # quotes_data = [{'CourierCode':'STF', 'CourierName':'Estafeta', 'CourierServiceId':'ESTAFETA_TERRESTRE_CONSUMO', 'CourierServiceName':'Terrestre Consumo', 'DeliveryDays':'2-5 días hab.', 'CouponCode':None, 'DiscountAmount':0, 'TotalPrice':85.83, 'EstimatedDeliveryDate':'2019-07-04','BestOption':True},
            # {'CourierCode':'FDX', 'CourierName':'FedEx', 'CourierServiceId':'FEDEX_EXPRESS_SAVER', 'CourierServiceName':'Express Saver', 'DeliveryDays':'3 días hab.', 'CouponCode':None, 'DiscountAmount':0, 'TotalPrice':134.75, 'EstimatedDeliveryDate':'2019-07-04','BestOption':False},{'CourierCode':'STF', 'CourierName':'Estafeta', 'CourierServiceId':'ESTAFETA_TERRESTRE_CONSUMO', 'CourierServiceName':'Terrestre Consumo', 'DeliveryDays':'2-3 días hab.', 'CouponCode':None, 'DiscountAmount':0, 'TotalPrice':70.83, 'EstimatedDeliveryDate':'2023-07-04','BestOption':True}]
            
            # Itera sobre los datos de la cotizacion de la api de pakke, y capturar sus datos
            for quote_data in quotes_data['Pakke']:  
                quote_courier_code = quote_data['CourierCode']
                quote_courier_name = quote_data['CourierName']
                quote_courier_service_id = quote_data['CourierServiceId']
                quote_courier_service_name = quote_data['CourierServiceName']
                quote_delivery_days = quote_data['DeliveryDays']
                quote_coupon_code = quote_data['CouponCode']
                quote_discount_amount = quote_data['DiscountAmount']
                quote_total_price = quote_data['TotalPrice']
                quote_estimated_delivery_date = quote_data['EstimatedDeliveryDate']
                quote_best_option = quote_data['BestOption']
                
                #Buscar si ya existe esa cotización
                quote_couriers = self.env['parcel.couriers_quote_pakke'].search([('name_shipments', '=', name_shipments), ('courier_code', '=', quote_courier_code), ('name', '=', quote_courier_name), ('courier_service_id', '=', quote_courier_service_id), ('courier_service_name', '=', quote_courier_service_name), ('delivery_days', '=', quote_delivery_days), ('coupon_code', '=', quote_coupon_code), ('discount_amount', '=', quote_discount_amount), ('total_price', '=', quote_total_price), ('estimated_delivery_date', '=', quote_estimated_delivery_date), ('best_option', '=', quote_best_option)], limit=1)  # 
                
                if not quote_couriers:  # Si la cotizacion no existe
                    new_quotes.append({  # Agrega la nueva cotizacion a la lista
                        'name_shipments': name_shipments,
                        'courier_code': quote_courier_code,
                        'name': quote_courier_name,
                        'courier_service_id': quote_courier_service_id,
                        'courier_service_name': quote_courier_service_name,
                        'delivery_days': quote_delivery_days,
                        'coupon_code': quote_coupon_code,
                        'discount_amount': quote_discount_amount,
                        'total_price': quote_total_price,
                        'estimated_delivery_date': quote_estimated_delivery_date,
                        'best_option': quote_best_option,
                    })
                    
                else:
                    
                    _logger.info("La cotización ya existe")
                    
            if new_quotes:  # Si hay nuevas cotizaciones
                with self.env.cr.savepoint():  # Crea un punto de guardado en la transacción de base de datos actual, ayuda a que si hay un error no realize nada para tener consistencia de datos
                    self.env['parcel.couriers_quote_pakke'].create(new_quotes)  # Crea nuevas cotizaciones
                #_logger.info(f"Cotizaciones {new_quotes}")
        
        except requests.exceptions.RequestException as e:
            
            raise ValidationError((f"No se pudo realizar la cotización {e}"))    
        
        self.name_orders = name_shipments #Para filtrar por el nombre del pedido

        self.message_post(body="Cotización realizada exitosamente", subject="Aviso")

    @api.onchange("id_couriers_selection")
    def quote_table_data(self):#Funcion para colocar la información en el One2many y del mensajero que se elija
        
        for quote_many_data in self:
            
            name_shipments=quote_many_data.name
        
            pakkes = self.env['parcel.couriers_quote_pakke'].search([('name_shipments', '=', name_shipments)])#Buscar los registros con el nombre del registro del modelo
            
            # Actualiza el campo One2many con los registros obtenidos
            self.id_couriers_table = [(6, 0, pakkes.ids)]
            
            #Colocar los datos del mensajero
            quote_many_data.courier_code = quote_many_data.id_couriers_selection.courier_code
            
            quote_many_data.courier_service_id = quote_many_data.id_couriers_selection.courier_service_id
        
            
    def pdf_shipping_guide(self):#Funcion para generar la guia de envio en pdf
        
        if self.id_couriers_selection:#Para validar si se ha seleccionado un mensajero
            
            if self.api_key_pakke == "0XSyUfbeuEGWjOmKjRHHeNBE4H41gPI4bD3zlL51zK47bbcruKzRRX9t3m44sWYp":#Si la apikey es de prueba
                
                #Datos a pasar al informe PDF
                data = {
                    'name_order': self.name,
                }
                #_logger.error(f"Imprimiendo{data['name_order']}")
                
                #Se obtiene la referencia del reporte
                xml_id = 'parcel.parcel_action'

                #Se genera el reporte accion
                action = self.env.ref(xml_id).report_action(self, data=data)
                
                #Id del reporte
                report = self.env.ref('parcel.parcel_action')#Busco el reporte en la base de datos
                
                #Renderizo el reporte
                pdf, _ = self.env['ir.actions.report']._render_qweb_pdf(report.id, data=data)
                
                #Codifico el pdf en b64
                data_pdf_shipping_guide = base64.b64encode(pdf)
                
                ShipmentId = "123_prueba"
                
                name_pdf_shipping_guide = f"Guia_envio_{self.name}_{ShipmentId}.pdf"
                
            elif self.api_key_pakke == "iNTi4G90zDc50sI9hLuNYAGKhNRqtsIFB92yzzFFSdoBWocp7lDIRm43DangOADY":#Si la api key es oficial
                
                #Creación de la guia de envio
                
                ShipmentId = self.create_shipping_guide()
                
                # #Obtener el pdf de la guia codificado en b64
                
                data_pdf_shipping_guide = self.get_data_shipping_guide(ShipmentId)
                
                name_pdf_shipping_guide = f"Guia_envio_{self.name}_{ShipmentId}_{self.courier_service_id}.pdf"
                
            #Codigo para relacionar el pdf al modelo parcel_test
            self.env['parcel.test'].create({'name': self.name, 'test_pdf': data_pdf_shipping_guide, 'file_name':name_pdf_shipping_guide})
            
            test = self.env['parcel.test'].search([('name', '=', self.name)])
                
            # Actualiza el campo One2many con los registros obtenidos
            self.test_table_pdf = [(6, 0, test.ids)]
            
            
            #Para verificar si el proceso de guia de envio ha sido realizado con exito
            
            id_courier_selection = (f"NewId_{self.id_couriers_selection.id}")#Convierto en string el id del registro actual del id_couriers_selection
        
            for record_guide in self.id_couriers_table:#Recorro cada registro del One2many del id_couriers_table
                
                record_guide.validation_guide = True#Vuelvo False a todos los record_selection del id_couriers_table
            
            self.validation_guide = True
            
            
            #Codigo para mandar la alerta al chatter del pdf
            attachment = self.env['ir.attachment'].create({
                    'name': name_pdf_shipping_guide,
                    'type': 'binary',
                    'datas': data_pdf_shipping_guide,
                    'res_name': name_pdf_shipping_guide,
                    'res_model': 'sale.order',
                    'res_id': self.id,
                })
            self.message_post(
                body=f"Guia de envio {ShipmentId} de la orden {self.name} generada exitosamente",
                message_type='notification',
                attachment_ids=[attachment.id]
            )
            
        else:
            
            raise ValidationError(("No haz seleccionado ningun mensajero"))
        
        
    def create_shipping_guide(self):#Funcion ara crear la guia de envio
        
        url = "https://seller.pakke.mx/api/v1/Shipments"#Endpoint para generar envios
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.api_key_pakke}",
            "Accept": "application/json"
        }
        body = {
            "CourierCode": self.courier_code,
            "CourierServiceId": self.courier_service_id,
            "ResellerReference": self.reseller_reference_parcel,
            "Content": self.content,
            "AddressFrom": {
                "ZipCode": self.address_from_zipcode,
                "State": self.address_from_state,
                "City": self.address_from_city,
                "Neighborhood": self.address_from_neighborhood,
                "Address1": self.address_from_address1,
                "Address2": self.address_from_address2,
                "Residential": self.address_from_residential
            },
                "AddressTo": {
                    "ZipCode": self.address_to_zipcode,
                    "State": self.address_to_state,
                    "City": self.address_to_city,
                    "Neighborhood": self.address_to_neighborhood,
                    "Address1": self.address_to_address1,
                    "Address2": self.address_to_address2,
                    "Residential": self.address_to_residential
            },
                "Parcel": {
                    "Length": self.parcel_length,
                    "Width": self.parcel_width,
                    "Height": self.parcel_height,
                    "Weight": self.parcel_weight
            },
                "Sender": {
                    "Name": self.sender_name,
                    "Phone1": self.sender_phone1,
                    "Phone2": self.sender_phone2,
                    "Email": self.sender_email
            },
                "Recipient": {
                    "Name": self.recipient_name,
                    "CompanyName": self.recipient_company_name,
                    "Phone1": self.recipient_phone1,
                    "Email": self.recipient_email
            }
        }
        
        try:

            json_body = json.dumps(body)#Se convierte a json

            #Se realiza la petición
            response = requests.post(url, headers=headers, data=json_body)
                
            ShipmentId = response.json()#Obtengo la respuesta de la peticion
            
            _logger.info(f"Id del envio{ShipmentId['ShipmentId']}")
            
            return ShipmentId['ShipmentId']#Obtengo el id del envio
        
        except requests.exceptions.RequestException as e:
            
            raise ValidationError((f"No se pudo realizar el envio {e}"))              
    
    def get_data_shipping_guide(self, ShipmentId):#Funcion para obtener la gui de envio
        
        url = f"https://seller.pakke.mx/api/v1/Shipments/{ShipmentId}/label"  # URL de la etiqueta de guia
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.api_key_pakke}",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)  # Realiza la solicitud a la API
                
            data_pdf_shipping_guide = response.json()  # Obtiene los datos de los estados de la respuesta de la API
            
            _logger.info(f"PDF{data_pdf_shipping_guide['data']}")
            
            return data_pdf_shipping_guide['data']
        
        except requests.exceptions.RequestException as e:
            
            raise ValidationError((f"No se pudo obtener el id del envio {e}"))
   
       
