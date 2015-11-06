{
   'name': "Send many offers to the same customer",
    'version': '1.0',
    'depends': ['sale'],
    'author': "Bernard DELHEZ, AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Sales',
    'description': 
    """
    Send many offers to the same customer

    It adds a new menuitem "Send by email" in the more section when your are in Quotation or Sale Order.
    It sends all selected Sales Orders. It checkes if the sales orders have the same customer and the state is in draft.
    It creates a new email template containing the different offers.
    
    This module has been developed by Bernard Delhez, intern @ AbAKUS it-solutions, under the control of Valentin Thirion.
    """,
    'data': ['wizard/sale_order_send_many_offers.xml',
             'sale_order_send_many_offers_to_same_customer_data.xml'
            ],
}