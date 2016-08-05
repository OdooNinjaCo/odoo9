from openerp import models,fields ,api,_
from openerp.exceptions import UserError

class sale_order(models.Model):
    _inherit='sale.order'

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        if self.tax_id or not self.tax_id:
            self.ensure_one()
            journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
            if not journal_id:
                raise UserError(_('Please define an accounting sale journal for this company.'))
            invoice_vals = {
                'name': self.client_order_ref or '',
                'origin': self.name,
                'type': 'out_invoice',
                'account_id': self.partner_invoice_id.property_account_receivable_id.id,
                'partner_id': self.partner_invoice_id.id,
                'journal_id': journal_id,
                'currency_id': self.pricelist_id.currency_id.id,
                'comment': self.note,
                'payment_term_id': self.payment_term_id.id,
                'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
                'company_id': self.company_id.id,
                'user_id': self.user_id and self.user_id.id,
                'team_id': self.team_id.id,
                'tax_id':[(6, 0, self.tax_id.ids)]
            }
            return invoice_vals
        else:
            return super(sale_order,self)._prepare_invoice()

    @api.depends('order_line.price_total','tax_id')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            if order.tax_id:
                amount_untaxed = tax = 0.0
                for line in order.order_line:
                    amount_untaxed += line.price_subtotal
                amount_tax=order.tax_id.compute_all(amount_untaxed, order.currency_id,1, product=False, partner=order.partner_id)
                for items in amount_tax['taxes']:
                    tax+=items['amount']
                order.update({
                    'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                    'amount_tax': tax,
                    'amount_total': amount_untaxed + tax,
                })
            else:
                return super(sale_order,self)._amount_all()

    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')



class sale_order_line(models.Model):
    _inherit='sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.order_id.tax_id or not line.order_id.tax_id:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_id)
                line.update({
                    'price_total': taxes['total_excluded'],
                    'price_subtotal': taxes['total_excluded'],
                })
            else:
                return super(sale_order_line,self)._compute_amount()

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Taxes', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
