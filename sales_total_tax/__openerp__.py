{
    'name':'Sales Total Tax',
    'description':"""
    Avoids Order Line And Invoice Line Tax Calculations


    Instaed applies Tax Calucation to the Final Sales Values and Invoice Value

     """,
    'author':'Odoo Ninja',
    'depends':['base','sale','account'],
    'data':['views/sale_view.xml',
            'views/invoice_view.xml',
            'report/report_saleorder.xml',
            'report/report_invoice.xml'],
    'email':'odooninja@gmail.com',
    'application':True,
    'installable':True
}