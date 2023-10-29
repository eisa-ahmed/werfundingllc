# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import random


def _generate_fake_email():
    names = ["alice", "bob", "charlie", "david", "ella"]
    domains = ["gmail", "yahoo", "hotmail", "outlook", "thunderbird"]
    return f"{random.choice(names)}{random.randint(10, 99)}@{random.choice(domains)}.com"


def _generate_fake_phone():
    return f"+1{random.randint(1000000000, 9999999999)}"


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    business_owner = fields.Boolean(string='Is Business Owner?')
    credit_application_id = fields.Many2one('credit.application', string='Company')
    last_name = fields.Char(string='Last Name')
    ownership_percent = fields.Float(string='% Ownership', tracking=True)
    credit_score_estimate = fields.Integer(string='Credit Score (Estimate)', tracking=True)
    social_security_no = fields.Char(string='Social Security No', tracking=True)
    birth_date = fields.Date(string='Date of Birth')
    fake_email = fields.Char(string='Fake Email')
    fake_phone = fields.Char(string='Fake Phone')

    @api.constrains('ownership_percent')
    def _check_ownership_percent(self):
        for record in self:
            if record.ownership_percent > 100 or record.ownership_percent < 0:
                raise ValidationError(_("Ownership percent should be between 0 and 100."))

    @api.constrains('birth_date')
    def _check_birth_date(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(_("Date of Birth cannot be in the future."))

    @api.model
    def create(self, vals):
        vals['fake_email'] = _generate_fake_email()
        vals['fake_phone'] = _generate_fake_phone()
        return super().create(vals)


class Landlord(models.Model):
    _name = 'landlord.landlord'
    _description = 'Landlord'

    name = fields.Char(string='Landlord Name')
    phone = fields.Char(string='Landlord Phone')


class CreditApplication(models.Model):
    _inherit = 'crm.lead'
    _description = 'Credit Application'

    fake_business_phone = fields.Char(string='Fake Business Phone')
    industry = fields.Many2one('res.partner.industry', string='Industry', tracking=True)
    app_id = fields.Char(string="App Id", copy=False, readonly=True, default=lambda self: _("New"))
    vat = fields.Char(string="Tax ID", tracking=True)
    incorporation_state_id = fields.Many2one('res.country.state', string='Incorporation State', tracking=True)
    legal_entity = fields.Selection(selection=[
        ('llc', 'LLC'),
        ('corporation', 'Corporation'),
        ('sole_prop', 'Sole Prop.')
    ], string='Legal Entity', tracking=True)
    city = fields.Char(string="City", tracking=True)
    state_id = fields.Many2one('res.country.state', string="State", tracking=True)
    zip = fields.Char(tracking=True)
    country_id = fields.Many2one('res.country', string="Country", tracking=True)
    business_start_date = fields.Date(string='Business Start Date', tracking=True)
    avg_monthly_revenue = fields.Monetary(currency_field='company_currency', string='Average Monthly Revenue',
                                          tracking=True)
    credit_card_processing = fields.Monetary(currency_field='company_currency', string='Monthly Credit Card Processing',
                                             tracking=True)
    requested_financing_amount = fields.Monetary(currency_field='company_currency', string='Requested Financing Amount',
                                                 tracking=True)
    use_of_funds = fields.Text(string='Use of Funds')
    existing_loan_advance = fields.Selection(selection=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Existing business loan/advance?', tracking=True)
    # display only if above is yes
    no_loan_advance = fields.Integer(string='How many?', tracking=True)
    total_balance = fields.Monetary(currency_field='company_currency', string='Total Balance', tracking=True)

    own_rent_loc = fields.Selection(selection=[
        ('rent', 'Rent'),
        ('own', 'Own')
    ], string='Do you Own or Rent Location?', required=True, default='rent', tracking=True)
    # display only if above is set
    monthly_rent_mortgage = fields.Monetary(currency_field='company_currency', string='Monthly Rent/Mortgage',
                                            tracking=True)

    # if rent, then show landlord fields, else show bank fields
    landlord_id = fields.Many2one('landlord.landlord', string='Landlord Name', tracking=True)
    landlord_phone = fields.Char(string='Landlord Phone', related='landlord_id.phone', store=True, readonly=False,
                                 tracking=True)

    bank_id = fields.Many2one('res.bank', string='Bank Name', tracking=True)
    bank_phone = fields.Char(string='Bank Phone', related='bank_id.phone', store=True, readonly=False, tracking=True)

    business_owner_ids = fields.Many2many(
        'res.partner', string="Business Owner")

    attachment_application_ids = fields.Many2many('ir.attachment', 'attachment_application_rel', string="Applications")
    attachment_bank_statements_ids = fields.Many2many('ir.attachment', 'attachment_bank_statement_rel',
                                                      string="Bank Statements")
    attachment_id_ids = fields.Many2many('ir.attachment', 'attachment_id_rel', string="IDs")
    attachment_voided_check_ids = fields.Many2many('ir.attachment', 'attachment_voided_check_rel',
                                                   string="Voided Checks")
    attachment_ar_report_ids = fields.Many2many('ir.attachment', 'attachment_ar_report_rel', string="AR Reports")
    attachment_credit_card_statements_ids = fields.Many2many('ir.attachment', 'attachment_credit_card_statement_rel',
                                                             string="Credit Card Statements")
    attachment_proof_of_ein_ids = fields.Many2many('ir.attachment', 'attachment_proof_of_ein_rel',
                                                   string="Proof of EIN")
    attachment_misc_ids = fields.Many2many('ir.attachment', 'attachment_misc_rel', string="Miscellaneous")
    attachment_pdf_id = fields.Many2one('ir.attachment', 'Attachment PDF')

    additional_notes = fields.Html(string='Additional Notes')

    sign_1 = fields.Char()
    sign_2 = fields.Char()
    title_1 = fields.Char()
    title_2 = fields.Char()
    date_1 = fields.Date()
    date_2 = fields.Date()

    def action_open_wizard(self):
        return {
            'name': 'Send to Funds',
            'type': 'ir.actions.act_window',
            'res_model': 'fund.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('credit_application.fund_wizard_form').id,
            'target': 'new',
            'context': {
                'default_credit_application_id': self.id
            }
        }

    def action_submit_application(self):
        return {
            'name': 'Submit Application',
            'type': 'ir.actions.act_window',
            'res_model': 'fund.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('credit_application.fund_wizard_form').id,
            'target': 'new',
            'context': {
                'default_credit_application_id': self.id, 'app_submission': True
            }
        }

    def set_default_followers(self):
        current_followers = self.message_follower_ids.mapped('name')
        manager_group = self.env.ref('credit_application.group_send_funders')
        for user in manager_group.users:
            if user.name not in current_followers:
                self.env['mail.followers'].create({
                    'res_model': 'crm.lead',
                    'res_id': self.id,
                    'partner_id': user.partner_id.id
                })

    @api.model
    def create(self, vals):
        vals['app_id'] = self.env['ir.sequence'].next_by_code('credit.application') or _('New')
        vals['fake_business_phone'] = _generate_fake_phone()
        res = super().create(vals)
        res.set_default_followers()
        return res

    def write(self, vals):
        previous_business_owners = self.business_owner_ids
        res = super().write(vals)
        if 'business_owner_ids' in vals:
            business_owners = self.business_owner_ids
            for business_owner in business_owners:
                business_owner.credit_application_id = self.id
            for prev_owner in previous_business_owners:
                if prev_owner.id not in business_owners.ids:
                    prev_owner.credit_application_id = False
        return res


class CreditFund(models.Model):
    _name = 'credit.fund'
    _description = 'Credit Fund'

    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True)
    contact_ids = fields.Many2many('res.partner', string="Contacts")
