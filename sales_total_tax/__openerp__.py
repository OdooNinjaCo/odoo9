{
    'name':'Sales Total Tax',
    'description':'Apply Taxing  To the Sales Total Amount and Invoice Total Amount',
    'author':'Odoo Ninja',
    'depends':['base','sale','account'],
    'data':['views/sale_view.xml',
            'views/invoice_view.xml'],
    'price':30.00,
    'currency': 'EUR',
    'application':True,
    'installable':True
}