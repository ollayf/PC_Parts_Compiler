import logging
from Parts import *
from scraper_utils import *

NEWEGG_HEADERS = ('Date', 'Name', 'Price', 'URL', 'Best Rating', 'Worst_Rating', 'Shipping Cost')
AMAZON_HEADERS = ('Date', 'Amazon Branch', 'Amazon Price', 'Amazon Delivery', \
                 'Cheapest Seller', 'Cheapest Price', 'Cheapest Delivery')

##########
# LOGGER #
##########

NEWEGG_XL = r'C:\Users\fei\Desktop\NewEgg_Prices.xlsx'
AMAZON_XL = r'C:\Users\fei\Desktop\Amazon_Prices.xlsx'