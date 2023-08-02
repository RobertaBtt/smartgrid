# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models, fields, api




class SmartmeterSimcard(models.Model):

    _name = "sg.smartmeter.simcard"
    _description = "Smartmeter Simcard relation"

    smartmeter_id = fields.Many2one('sg.smartmeter', "Smart Meter")
    simcard_id = fields.Many2one('sg.simcard', "Simcard")
    begin_date = fields.Date(string="Activation Simcard inside smartmeter")
    end_date = fields.Date(string="Simcard dismiss for the smartmeter")

    @api.one
    def name_get(self):
        return self.smartmeter_id, self.simcard_id