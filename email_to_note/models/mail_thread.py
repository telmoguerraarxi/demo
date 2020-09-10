import logging
from odoo import api, models, tools

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        try:
            return super(MailThread, self).message_route(message, message_dict, model, thread_id, custom_values)
        except ValueError as e:

            references = tools.decode_message_header(message, 'References')
            in_reply_to = tools.decode_message_header(message, 'In-Reply-To').strip()
            thread_references = references or in_reply_to
            reply_match, reply_model, reply_thread_id, reply_hostname, reply_private = tools.email_references(thread_references)

            rcpt_tos = ','.join([
                tools.decode_message_header(message, 'Delivered-To'),
                tools.decode_message_header(message, 'To'),
                tools.decode_message_header(message, 'Cc'),
                tools.decode_message_header(message, 'Resent-To'),
                tools.decode_message_header(message, 'Resent-Cc')])
            rcpt_tos_localparts = [
                e.split('@')[0].lower()
                for e in tools.email_split(rcpt_tos)
            ]

            dest_aliases = self.env['mail.alias'].search([
                ('alias_name', 'in', rcpt_tos_localparts),
                ('alias_model_id.model', '=', model),
            ], limit=1)

            note_id = self.env.ref('email_to_note.note_email_without_route')

            new_model = 'note.note'
            new_thread_id = note_id.id
            route = self.message_route_verify(
                message, message_dict,
                (new_model, new_thread_id, custom_values, self._uid, dest_aliases),
                update_author=True, assert_model=reply_private, create_fallback=True,
                allow_private=reply_private, drop_alias=True)
            return [route]
