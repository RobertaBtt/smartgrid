# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models, fields, api





class SimcardTariff(models.Model):

    _name = "sg.simcard.tariff"
    _description = "Simcard Tariff"

    label=fields.Char(string="Tariff", required="True")

    _sql_constraints = [('label_uniq', 'unique(label)', 'This Tariff already exists'),]

    @api.one
    def name_get(self):
        return self.id, self.label
