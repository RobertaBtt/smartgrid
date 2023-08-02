# -*- coding: utf-8 -*-

from openerp.tools.translate import _
from openerp import models, fields, api, SUPERUSER_ID


class ResGroups(models.Model):
    _inherit = 'res.groups'

    zones_id = fields.One2many('sg.zone', 'smart_grid_group', string='Zones', readonly=True)
