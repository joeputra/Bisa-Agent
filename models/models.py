# -*- coding: utf-8 -*-

from odoo import models, fields, api


class bisa_agent(models.Model):
    _name = 'bisa_agent.phonecall'
    _description = 'Bisa Agent'

    name = fields.Char('Call Name', required=True)
    call_date = fields.Datetime('Call Date')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.uid)
    partner_id = fields.Many2one('res.partner', 'Contact')
    note = fields.Html('Note')
    duration = fields.Float('Duration', help="Duration in minutes.")
    waiting_time = fields.Float('Waiting', help="Duration in minutes.")
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    start_time = fields.Float("Start time")
    start_talk = fields.Float("Start talk")
    state = fields.Selection([
        ('pending', 'Not Held'),
        ('cancel', 'Cancelled'),
        ('open', 'To Do'),
        ('done', 'Held'),
        ('rejected', 'Rejected'),
        ('missed', 'Missed')
    ], string='Status', default='open',
        help='The status is set to To Do, when a call is created.\n'
             'When the call is over, the status is set to Held.\n'
             'If the call is not applicable anymore, the status can be set to Cancelled.')
    phonecall_type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing')
    ], string='Type', default='outgoing')

    def init_call(self):
        self.ensure_one()
        self.call_date = fields.Datetime.now()
        self.start_time = time.time()

    def start_talking(self):
        self.start_talk = time.time()

    def hangup_call(self):
        self.ensure_one()
        waiting_time = (self.start_talk - self.start_time)
        duration = (time.time() - self.start_talk)
        note = False
        self.write({
            'state': 'done',
            'duration': duration/60,
            'waiting_time': waiting_time/60,
            'note': note,
        })
        return

    def canceled_call(self):
        self.ensure_one()
        waiting_time = (time.time() - self.start_time)
        self.write({
            'state': 'pending',
            'waiting_time': waiting_time/60,
        })

    def _get_info(self):
        infos = []
        for record in self:
            info = {
                'id': record.id,
                'name': record.name,
                'state': record.state,
                'call_date': record.call_date,
                'duration': record.duration,
                'phone': record.phone,
                'mobile': record.mobile,
                'note': record.note,
            }
            if record.partner_id:
                ir_model = record.env['ir.model'].search([('model', '=', 'res.partner')])
                info.update({
                    'partner_id': record.partner_id.id,
                    'activity_model_name': ir_model.display_name,
                    'partner_name': record.partner_id.name,
                    'partner_image': record.partner_id.image_small,
                    'partner_email': record.partner_id.email
                })
            infos.append(info)
        return infos

    @api.model
    def _create_and_init(self, vals):
        phonecall = self.create(vals)
        phonecall.init_call()
        return phonecall._get_info()[0]

    def _update_and_init(self, vals):
        self.ensure_one()
        self.update(vals)
        return self._get_info()[0]

    @api.model
    def create_from_contact(self, partner_id):
        partner = self.env['res.partner'].browse(partner_id)
        vals = {
            'name': partner.name,
            'phone': partner.phone,
            'mobile': partner.phone,
            'partner_id': partner_id,
        }
        return self._create_and_init(vals)

    @api.model
    def create_call(self, number, incoming):
        partner = self.env['res.partner'].search(['|', ('phone', 'ilike', number), ('mobile', 'ilike', number)], limit=1)
        if incoming:
            return self.create_from_incoming_call(number, partner and partner.id or False)
        elif partner:
            return self.create_from_contact(partner.id)
        else:
            return self.create_from_number(number)

    @api.model
    def create_from_number(self, number):
        vals = {
            'name': _('Call to %s') % number,
            'phone': number,
        }
        return self._create_and_init(vals)

    def create_from_missed_call(self, number, partner_id=False):
        self.ensure_one()
        vals = {
            'name': _('Missed Call from %s') % number,
            'phone': number,
            'state': 'missed',
            'direction': 'incoming',
            'partner_id': partner_id,
        }
        return self._update_and_init(vals)

    def create_from_rejected_call(self, number, partner_id=False):
        self.ensure_one()
        vals = {
            'name': _('Rejected Incoming Call from %s') % number,
            'phone': number,
            'direction': 'incoming',
            'state': 'rejected',
            'partner_id': partner_id,
        }
        return self._update_and_init(vals)

    def create_from_incoming_call_accepted(self, number, partner_id=False):
        self.ensure_one()
        vals = {
            'name': _('Incoming call from %s') % number,
            'phone': number,
            'state': 'done',
            'direction': 'incoming',
            'partner_id': partner_id,
        }
        return self._update_and_init(vals)

    @api.model
    def create_from_incoming_call(self, number, partner_id=False):
        if partner_id:
            name = _('Incoming call from %s') % self.env['res.partner'].browse([partner_id]).display_name
        else:
            name = _('Incoming call from %s') % number
        vals = {
            'name': name,
            'phone': number,
            'direction': 'incoming',
            'partner_id': partner_id,
        }
        return self._create_and_init(vals)

    @api.model
    def create_from_phone_widget(self, model, res_id, number):
        partner_id = False
        if model == 'res.partner':
            partner_id = res_id
        else:
            record = self.env[model].browse(res_id)
            fields = self.env[model]._fields.items()
            partner_field_name = [k for k, v in fields if v.type == 'many2one' and v.comodel_name == 'res.partner'][0]
            if len(partner_field_name):
                partner_id = record[partner_field_name].id
        vals = {
            'name': _('Call to %s') % number,
            'phone': number,
            'partner_id': partner_id,
        }
        return self._create_and_init(vals)

