# -*- coding: utf-8 -*-


from openerp import models, fields, api, _, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class Zone(models.Model):
    """
    Represents the Zone for the Smart Grid
    """
    _name = "sg.zone"

    name = fields.Char(string='Zone ID', index=True, readonly=False,  required=True)
    description = fields.Text(string='Description')
    smartmeter_ids = fields.Many2many('sg.smartmeter',  string='Smart Meters')

    smart_grid_group = fields.Many2one('res.groups', 'Smart Grid Group', required=True)
    user_ids = fields.Many2many('res.users', string='Allowed Users', compute='_get_user_ids', store=True)
    yellow_zone_start = fields.Integer(string="Yellow Zone Start (KW)", default=100000)
    yellow_zone_stop = fields.Integer(string="Yellow Zone Stop (KW)", default=150000)

    target_value = fields.Float(string="Target Value", required=False, default=4.1)
    threshold_min = fields.Float(string="Min Threshold", required=False, default=-1.0)
    threshold_max = fields.Float(string="Max Threshold", required=False, default=1.0)
    # contract_number = fields.Integer(string='Total Number of Contracts',
    #                                  store=False,
    #                                  readonly=True,
    #                                  compute='_get_number_contracts')
    # online_smartmeters_number = fields.Integer(string='Total Number of online Smartmeters',
    #                    store=False,
    #                    readonly=True,
    #                    default=10)
    #                    # compute='_get_number_online_smartmeters')
    # offline_smartmeters_number = fields.Integer(string='Total Number of offline Smartmeters',
    #                    store=False,
    #                    readonly=True,
    #                    default=5)
    #                    # compute='_get_number_offline_smartmeters')
    # alarms_number = fields.Integer(string='Total Number of Active Alarms',
    #                    store=False,
    #                    readonly=True,
    #                    default=7)
    #                    # compute='_get_number_active_alarms')


    @api.one
    @api.depends('smart_grid_group.users')
    def _get_user_ids(self):
        # Return all users having access to this zone
        self.user_ids = self.smart_grid_group.users

    # @api.one
    # def _get_number_contracts(self):
    #     self._cr.execute("""select count(distinct sc.contract_id)
    #     from sg_smartmeter_contract sc join sg_smartmeter sm
    #     on sc.smartmeter_id = sm.id
    #     where sm.zone_id = %s
    #     """ % self.id)
    #     self.contract_number = self._cr.fetchone()[0] or 0

    # @api.one
    # def _get_number_online_smartmeters(self):
    #     self._cr.execute("""select count(distinct sc.contract_id)
    #     from sg_smartmeter_contract sc join sg_smartmeter sm
    #     on sc.smartmeter_id = sm.id
    #     where sm.zone_id = %s
    #     """ % self.id)
    #     self.online_smartmeters_number = self._cr.fetchone()[0] or 0

    # @api.one
    # def _get_number_offline_smartmeters(self):
    #     self._cr.execute("""select count(distinct sc.contract_id)
    #     from sg_smartmeter_contract sc join sg_smartmeter sm
    #     on sc.smartmeter_id = sm.id
    #     where sm.zone_id = %s
    #     """ % self.id)
    #     self.offline_smartmeters_number = self._cr.fetchone()[0] or 0

    # @api.one
    # def _get_number_active_alarms(self):
    #     self._cr.execute("""select count(distinct sc.contract_id)
    #     from sg_smartmeter_contract sc join sg_smartmeter sm
    #     on sc.smartmeter_id = sm.id
    #     where sm.zone_id = %s
    #     """ % self.id)
    #     self.alarms_number = self._cr.fetchone()[0] or 0

    _sql_constraints = [ ('name_uniq', 'unique(name)', 'Zone ID must be unique!'), ]
