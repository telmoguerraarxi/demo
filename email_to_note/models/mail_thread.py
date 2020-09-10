import logging
from odoo import api, models, tools, _

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _routing_create_bounce_email(self, email_from, body_html, message, **mail_values):
        raise ValueError(_("Bounce"))

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        email_from = message_dict['email_from']
        try:
            return super(MailThread, self).message_route(message, message_dict, model, thread_id, custom_values)
        except:
            rcpt_tos_localparts = [e.split('@')[0].lower() for e in tools.email_split(message_dict['recipients'])]
            dest_aliases = self.env['mail.alias'].search([('alias_name', 'in', rcpt_tos_localparts)], limit=1)

            user_id = self._mail_find_user_for_gateway(email_from, alias=dest_aliases).id or self._uid

            new_model = 'note.note'
            new_thread_id = self.env.ref('arxi.note_email_without_route', raise_if_not_found=False).id or False
            route = self._routing_check_route(
                message, message_dict,
                (new_model, new_thread_id, custom_values, user_id, dest_aliases),
                raise_exception=False)
            return [route]
