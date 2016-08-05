from openerp import models,fields ,api

class account_invoice(models.Model):
    _inherit='account.invoice'

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id','tax_id')
    def _compute_amount(self):
        if self.tax_id or not self.tax_id:
            print "hiiiiiiiiiiiiiii"
            tax=0.00
            self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
            amount_tax = self.tax_id.compute_all(self.amount_untaxed, self.currency_id, 1, product=False,
                                                  partner=self.partner_id)
            for items in amount_tax['taxes']:
                tax += items['amount']
            self.amount_tax=tax
            self.amount_total = self.amount_untaxed + self.amount_tax
            amount_total_company_signed = self.amount_total
            amount_untaxed_signed = self.amount_untaxed
            if self.currency_id and self.currency_id != self.company_id.currency_id:
                amount_total_company_signed = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
                amount_untaxed_signed = self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
            sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
            self.amount_total_signed = self.amount_total * sign
            self.amount_untaxed_signed = amount_untaxed_signed * sign
        else:
            return super(account_invoice,self)._compute_amount()

    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    amount_untaxed = fields.Monetary(string='Untaxed Amount',
                                     store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount', currency_field='company_currency_id',
                                            store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax',
                                 store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Total',
                                   store=True, readonly=True, compute='_compute_amount')
    amount_total_signed = fields.Monetary(string='Total', currency_field='currency_id',
                                          store=True, readonly=True, compute='_compute_amount',
                                          help="Total amount in the currency of the invoice, negative for credit notes.")
    amount_total_company_signed = fields.Monetary(string='Total', currency_field='company_currency_id',
                                                  store=True, readonly=True, compute='_compute_amount',
                                                  help="Total amount in the currency of the company, negative for credit notes.")