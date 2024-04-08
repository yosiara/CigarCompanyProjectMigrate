
from odoo import models, tools, fields, api


class SendMailMixin(models.AbstractModel):
    _name = 'computers_inventory.send_mail_mixin'

    def get_email_from(self, template):
        email_from = ''
        if template.mail_server_id:
            email_from = template.mail_server_id.smtp_user
        else:
            mail_server = template.env['ir.mail_server'].sudo().search([], limit=1, order='sequence')
            if mail_server:
                email_from = mail_server.smtp_user
        return email_from

    def get_computer_inventory_responsible(self):
        group = self.env.ref('l10n_cu_hlg_computers_inventory.computers_inventory_manager')
        emails = []
        for user in group.users:
            if user.email:
                emails.append(user.email)
        return emails

    @api.multi
    def send_mail(self, template_xmlid, recipients, force_send=False):

        template = self.env.ref(template_xmlid)

        rendering_context = dict(self._context)

        rendering_context.update({
            'email_to': ', '.join(recipients),
            'email_from': self.get_email_from(template)
        })
        template = template.with_context(rendering_context)

        mails_to_send = self.env['mail.mail']
        for record in self:
            mail_id = template.send_mail(record.id)
            current_mail = self.env['mail.mail'].browse(mail_id)
            mails_to_send |= current_mail

        if force_send and mails_to_send:
            mails_to_send.send()

        return True

