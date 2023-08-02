# -*- coding: utf-8 -*-


from openerp.tools.translate import _
from openerp import models, fields, api, SUPERUSER_ID


class ResUser(models.Model):
    _inherit = 'res.users'

    @api.one
    @api.depends('groups_id.zones_id')
    def _get_zone_ids(self):
        # Return all smartgrid zones the user has access to
        self.zone_ids = self.env['sg.zone']
        for zone in self.env['sg.zone'].search([]):
            if zone.smart_grid_group in self.groups_id:
                self.zone_ids += zone

    zone_ids = fields.Many2many('sg.zone', string='Allowed Smartgrid Zones', compute='_get_zone_ids')

    @api.one
    def _has_smartmeter(self):
        hasSmartmeter = False

        if not isinstance(self.id, models.NewId):
            self.has_smartmeter = False
        else:
            contracts = self.contract_ids
            for contract in contracts:
                if contract.has_smartmeter:
                    hasSmartmeter = True


            else: self.has_smartmeter = hasSmartmeter

        for smartmeter_contract in self.name.smartmeter_contract_ids:
            if smartmeter_contract.smartmeter_id.type in ('w', 'e'):
                # returns only the first sm found
                self.withdrawal_id = smartmeter_contract.smartmeter_id
                return True
        self.withdrawal_id = False
