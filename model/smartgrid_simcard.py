# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models, fields, api



class Simcard(models.Model):

    _name = "sg.simcard"
    _description = "Simcard"

    number=fields.Char(string="Phone number", required="True")

    provider_id = fields.Many2one('sg.simcard.provider', "Sim Provider")
    tariff_id = fields.Many2one('sg.simcard.tariff', "Sim Tariff")

    _sql_constraints = [('name_uniq', 'unique(number)', 'This Number already exists'),]

    @api.one
    def name_get(self):
        return self.id, self.number
