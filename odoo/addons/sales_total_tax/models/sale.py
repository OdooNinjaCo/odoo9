from openerp import models,fields ,api

class sale_order(models.Model):
    _inherit='sale.order'

    @api.depends('order_line.price_total')
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
