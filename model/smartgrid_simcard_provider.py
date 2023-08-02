# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models, fields, api



class SimcardProvider(models.Model):

    _name = "sg.simcard.provider"
    _description = "Simcard Provider"

    label=fields.Char(string="Provider", required="True")

    _sql_constraints = [('label_uniq', 'unique(number)', 'This Provider already exists'),]

    @api.one
    def name_get(self):
        return self.id, self.label

