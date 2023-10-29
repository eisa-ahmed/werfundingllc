from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import base64


class FundWizard(models.TransientModel):
    _name = 'fund.wizard'
    _description = 'Fund Selection Wizard'

    credit_application_id = fields.Many2one('crm.lead', string='Credit Application')
    fund_ids = fields.Many2many('credit.fund', string='Funds')
    in_house = fields.Boolean()
    external = fields.Boolean()
    # Document options
    applications = fields.Boolean()
    doc_ids = fields.Boolean(string="Ids")
    ar_reports = fields.Boolean()
    proof_ein = fields.Boolean(string="Proof of EIN")
    bank_statement = fields.Boolean(string="Bank Statements")
    voided_checks = fields.Boolean(string="Voided Checks")
    credit_card_statements = fields.Boolean(string="Credit Card Statements")
    miscellaneous = fields.Boolean(string="Miscellaneous")

    def generate_application_pdf(self, app_id_ref):
        company_name = self.credit_application_id.name
        app_id = self.credit_application_id.app_id
        file_name = f"{company_name}-{app_id}.pdf"

        report_id = self.env.ref(app_id_ref).id
        report = self.env['ir.actions.report'].browse(report_id)

        pdf_data, _ = self.env.ref(app_id_ref)._render_qweb_pdf(report.id,
                                             [self.credit_application_id.id])
        # Create a new attachment record with the PDF data
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': base64.b64encode(pdf_data),
            'res_model': 'crm.lead',
            'res_id': self.credit_application_id.id,
            'type': 'binary',
            'mimetype': 'application/pdf'
        })
        self.credit_application_id.attachment_pdf_id = attachment.id

        return attachment

    def gather_attachment_ids(self, credit_application_id):

        applications = []

        if self.in_house:
            applications += self.generate_application_pdf('credit_app_report.credit_app_report_id')
        if self.external:
            applications += self.generate_application_pdf('credit_app_report.credit_app_report_fake')

        if self.applications:
            applications += credit_application_id.attachment_application_ids
        if self.bank_statement:
            applications += credit_application_id.attachment_bank_statements_ids
        if self.doc_ids:
            applications += credit_application_id.attachment_id_ids
        if self.ar_reports:
            applications += credit_application_id.attachment_ar_report_ids
        if self.proof_ein:
            applications += credit_application_id.attachment_proof_of_ein_ids
        if self.voided_checks:
            applications += credit_application_id.attachment_voided_check_ids
        if self.credit_card_statements:
            applications += credit_application_id.attachment_credit_card_statements_ids
        if self.miscellaneous:
            applications += credit_application_id.attachment_misc_ids

        if not len(applications):
            raise ValidationError(_("Please select attachment options for Submission."))

        all_attachment_ids = [att.id for att in applications]

        return all_attachment_ids

    def action_send_mail_funds(self):
        if not self.fund_ids and not self.env.context.get('app_submission', False):
            raise ValidationError(_("Please Select Funds to Send the application."))

        Mail = self.env['mail.mail']
        body = self.credit_application_id.additional_notes
        subject = f'New Submission - {self.credit_application_id.name} - {self.credit_application_id.app_id}'
        attachment_ids = self.gather_attachment_ids(self.credit_application_id)

        if not self.env.context.get('app_submission', False):
            for fund in self.fund_ids:
                email_cc = ', '.join(fund.contact_ids.mapped('email'))
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_from': 'submissions@werfundingllc.com',
                    'email_to': fund.email,
                    'email_cc': email_cc,
                    'model': 'crm.lead',
                    'res_id': self.credit_application_id.id,
                }

                mail = Mail.create(mail_values)
                mail.unrestricted_attachment_ids = [(6, 0, attachment_ids)]
                mail.send()
        else:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_from': self.env.user.email,
                'email_to': 'submissions@werfundingllc.com',
                'model': 'crm.lead',
                'res_id': self.credit_application_id.id,
            }

            mail = Mail.create(mail_values)
            mail.unrestricted_attachment_ids = [(6, 0, attachment_ids)]
            mail.send()

        return {'type': 'ir.actions.act_window_close'}
