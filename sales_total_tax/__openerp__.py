{
    'name':'Sales Total Tax',
    'description':"""
    Avoids Order Line And Invoice Line Tax Calculations


    Instaed applies Tax Calucation to the Final Sales Values and Invoice Value


    Free Customization and Support will be provided  related to this work After the purchase of the module
     """,
    'author':'Odoo Ninja',
    'depends':['base','sale','account'],
    'data':['views/sale_view.xml',
            'views/invoice_view.xml'],
    'price':30.00,
    'currency': 'EUR',
    'email':'odooninja@gmail.com',
    'application':True,
    'installable':True
}