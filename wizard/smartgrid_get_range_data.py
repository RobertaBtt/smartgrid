# -*- coding: utf-8 -*-


from openerp import fields, models, api, _, SUPERUSER_ID
from openerp.addons.energy_people.model.ep_contract import PROFILE



from ..model.smartgrid_smartmeter import PHASES
from ..api import SmartgridApi

import logging

_logger = logging.getLogger(__name__)


class SmartgridGetData(models.TransientModel):

    _name = "sg.get.data.wizard"

    smartmeter_id = fields.Many2one('sg.smartmeter',  string="Smartmeter")
    data_da = fields.Date(string="Da:" )
    data_a = fields.Date(string="A:" )
    partner_id = fields.Many2one('res.partner', 'Cliente', domain=[('customer','=',True), ('has_smartmeter', '=', True)])
    contract_id = fields.Many2one('ep.contract',  string="Contratto", required=True, domain=[('active', '=', True)])

    type = fields.Selection(PROFILE, string='Tipo smartmeter',  related='smartmeter_id.type', store=True, readonly=True, copy=False)
    phases = fields.Selection(PHASES, string="Fasi smartmeter",  related='smartmeter_id.phases', store=True, readonly=True, copy=False)

    measurement_ts = fields.Char(string="Measurement_ts")
    sender_id = fields.Char(string="Sender_id")
    energia_attiva_prelievo = fields.Char(string="Lettura")

    @api.one
    def name_get(self):
        return self.id, self.partner_id.name



    @api.multi
    def getData(self):

        #richiama get data del model vero

        values = self.env['sg.meter_readings'].get_meter_data(self.smartmeter_id)

        wizard_vals = {}

        if 'data' in values and len(values['data']) > 0:
            wizard_vals['sender_id'] = self.smartmeter_id.name
            if 'measurement_ts' in values['data']:
                wizard_vals['measurement_ts'] = values['data']['measurement_ts']
            if 'valore' in values['data']:
                wizard_vals['energia_attiva_prelievo'] = values['data']['valore']

        self.write(wizard_vals)


        this = self.browse(self._ids[0])

        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': this._name,
                'context': self._context,
                'domain': [],
            }


