from openerp.osv import osv

class account_invoice_mass_mailing(osv.osv_memory):
    _name = "sale.order.send.many.offers"
    _description = "Send many offers to the same customer"

    def send_offers_by_email(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []

        sale_order_obj = self.pool['sale.order']
        email_template_obj = self.pool['email.template']
        mail_mail_obj = self.pool['mail.mail']
        ir_attachment_obj = self.pool['ir.attachment']

        
        sale_order_references = []
        partner_id_tmp = sale_order_obj.browse(cr, uid, active_ids[0], context=context).partner_id.id
        
        #checks if the offers have the same customer and the quotation have the state draft
        for sale_order in sale_order_obj.browse(cr, uid, active_ids, context=context):
            if partner_id_tmp!= sale_order.partner_id.id:
                raise osv.except_osv('Warning!', "Selected offer(s) don't have the same customer.")
            if sale_order.state != 'draft':
                raise osv.except_osv('Warning!', "Selected offer(s) need to be in draft.")
            sale_order_references.append(sale_order.name)

        #generates the references for the main email template
        references_detail_html_string = ""
        references_string = ""
        template_ids = email_template_obj.search(cr, uid, [('name', '=','Sales Order - Send many offers to the same customer, create one reference')], context=context)
        if template_ids:
            last = len(active_ids)-1
            i = 0
            for sale_order_id in active_ids:
                values = email_template_obj.generate_email(cr, uid, template_ids[0], sale_order_id)
                references_detail_html_string += values['body_html']
                if i == last:
                    references_string += str(sale_order_references[i])
                else:
                    references_string += str(sale_order_references[i]) +", "
                i+=1

        #generates the attachments
        attachments = []
        template_ids = email_template_obj.search(cr, uid, [('name', '=','Sales Order - Send by Email')], context=context)
        if template_ids:
            for sale_order_id in active_ids:
                values = email_template_obj.generate_email(cr, uid, template_ids[0], sale_order_id)
                attachments.append(values['attachments'][0])
        
        #generates the main email template
        template_ids = email_template_obj.search(cr, uid, [('name', '=','Sales Order - Send many offers to the same customer')], context=context)
        if template_ids:
            values = email_template_obj.generate_email(cr, uid, template_ids[0], active_ids[0])
            
            values['subject'] += " (Ref: "+references_string+")"
            values['body_html'] = values['body_html'].replace("#REFERENCES#", references_detail_html_string)
            
            ####################################################
            #inspired by the send_mail method of email.template#
            ####################################################
            
            if not values.get('email_from'):
                raise osv.except_osv(_('Warning!'), _("Sender email is missing or empty after template rendering. Specify one to deliver your message"))
            
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            
            attachment_ids = values.pop('attachment_ids', [])
            
            #removes attachment because we want to use the generated attachments from all the offers.
            values.pop('attachments', [])
            msg_id = mail_mail_obj.create(cr, uid, values, context=context)
            mail = mail_mail_obj.browse(cr, uid, msg_id, context=context)

            # manage attachments
            for attachment in attachments:
                attachment_data = {
                    'name': attachment[0],
                    'datas_fname': attachment[0],
                    'datas': attachment[1],
                    'res_model': 'mail.message',
                    'res_id': mail.mail_message_id.id,
                }
                context = dict(context)
                context.pop('default_type', None)
                attachment_ids.append(ir_attachment_obj.create(cr, uid, attachment_data, context=context))
            
            if attachment_ids:
                values['attachment_ids'] = [(6, 0, attachment_ids)]
                mail_mail_obj.write(cr, uid, msg_id, {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)

            mail_mail_obj.send(cr, uid, [msg_id])
        
        #mark the offers as sent
        for sale_order_id in active_ids:
            sale_order_obj.write(cr, uid, sale_order_id, {'state': 'sent'})
         
        return {'type': 'ir.actions.act_window_close'}