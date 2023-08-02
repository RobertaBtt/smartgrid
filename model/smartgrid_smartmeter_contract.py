# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models, fields, api


class SmartmeterContract(models.Model):

    _name = "sg.smartmeter.contract"

    _description = "Contract Smartmeter"

    smartmeter_id = fields.Many2one('sg.smartmeter', "Smart Meter")
    contract_id = fields.Many2one('ep.contract', "Contract")
    begin_date = fields.Date(string="Begin date smart meter")
    end_date = fields.Date(string="End date smart meter")

    @api.one
    def name_get(self):
        return self.id, self.smartmeter_id.name

SmartmeterContract()
