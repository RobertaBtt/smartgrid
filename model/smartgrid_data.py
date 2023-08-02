# -*- coding: utf-8 -*-


from openerp import models, fields, api, _, SUPERUSER_ID

import logging

_logger = logging.getLogger(__name__)




class SmartgridData(models.Model):

    _name = "sg.data"

    measurement_ts = fields.Char(string="Timestamp misura")
    sender_id = fields.Char(string="Numero seriale smartmeter")
    energia_attiva_prelievo = fields.Char(string="Energia attiva prelievo") #tabella smartgrid sg#21
    potenza_attiva = fields.Char(string="Potenza attiva")
    count = fields.Char(string="Count")
    #partner_id = fields.String(compute="_get_partner", string="Cliente")

