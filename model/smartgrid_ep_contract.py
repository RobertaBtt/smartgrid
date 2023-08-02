# -*- coding: utf-8 -*-
from openerp.tools.translate import _
from openerp import models, fields, api


class Contract(models.Model):

    _inherit = "ep.contract"
    _description = "Contract Smartmeter"


    @api.one
    @api.depends('smartmeter_contract_ids')
    def _has_smartmeter(self):
        if not isinstance(self.id, models.NewId):
            relazioni_smartmeter =  self.smartmeter_contract_ids

            if relazioni_smartmeter is not None:
                if len(relazioni_smartmeter) == 0:
                    self.has_smartmeter = False
                    return False
                else:
                    self.has_smartmeter = True
                    return True
            else:
                self.has_smartmeter = False
                return False

        else:
            self.has_smartmeter = False
            return False

    smartmeter_contract_ids = fields.One2many('sg.smartmeter.contract', "contract_id", "Smartmeters Contracts")
    zone_ids = fields.Many2many('sg.zone', string='Zones', compute='_get_zone_ids', store=True)
    has_smartmeter = fields.Boolean(string="Has smartmeter", compute="_has_smartmeter")




    @api.one
    @api.depends('smartmeter_contract_ids')
    def _get_zone_ids(self):
        # Return all zones for this contract
        zones = []
        for smartmeter_contract in self.smartmeter_contract_ids:
            sm_zones = smartmeter_contract.smartmeter_id.zone_ids
            for zone in sm_zones:
                if zone.id not in zones:
                    zones.append(zone.id)
        self.zone_ids = zones

