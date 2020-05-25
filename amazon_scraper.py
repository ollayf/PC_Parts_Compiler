import requests
import time
from bs4 import BeautifulSoup as soup
import re
from envs import *
from Parts import *

session_start = time.strftime('%d/%m/%Y_%H.%M')
date, time = session_start.split('_')
AMAZON_PRODUCT_LIST = [
    CPU('Ryzen 3 3300X', 3.8, 4, 8, 'AMD', 'B0876YS2T4'), \
    CPU('Ryzen 5 3600', 3.6, 6, 12, 'AMD', 'B07STGGQ18'), \
    CPU('Ryzen 7 3700X', 3.6, 8, 16, 'AMD', 'B07SXMZLPK'), \
    CPU('Ryzen 7 3800X', 3.9, 8, 16, 'AMD', 'B07SXMZLPJ'), \
    CPU('Ryzen 9 3900X', 3.8, 12, 24, 'AMD', 'B07SXMZLP9')
]

# For logging
logging.basicConfig(filename='logs/amazon_log.md', filemode='a+', format='%(asctime)s - %(levelname)s - %(message)s' \
                    , datefmt=('%d/%m/%Y, %H%M'), level=logging.INFO)
logger = logging.getLogger()

def process_shipping_message(shipping_message: str):
    '''
    Process the shipping message from the Amazon url to the product to get the shipping fee
    deprecated as I'm now using the sellers page
    :param shipping_message:
    :return:
    '''
    shipping_message = ' '.join(shipping_message.split())
    shipping_message = shipping_message.lower()
    print(shipping_message)
    if shipping_message == 'free delivery.':
        return 'Free'

def get_seller_details(seller_cont):
    '''
    Gets the seller's name, price and delivery cost when given the seller's html container
    :param seller_cont: html container of the seller
    :return: [name, price, delivery] of the seller
    '''
    # Get the sellername out
    name = seller_cont.find('h3', {'class': 'a-spacing-none olpSellerName'})
    seller_name = name.span.a.text
    seller_name = ' '.join(seller_name.split())
    print('Seller Name: ', seller_name)
    # Gets the price out
    price = seller_cont.find('span', {'class': 'a-size-large a-color-price olpOfferPrice a-text-bold'}).text
    price = price.split()[0]
    price = float(re.findall(r"\d+\.\d+", price)[0])
    print(price)
    try: # if delivery is free
        delivery_msg = seller_cont.find('p', {'class': 'olpShippingInfo'}).span.b.text
        if 'free' in delivery_msg.lower():
            delivery = 'Free'
        else:
            delivery = 'Unknown'
            logging.info('Delivery is unknown. Please find out the problem')
    except: # if there is delivery charge
        try:
            delivery_msg = seller_cont.find('span', {'class': 'olpShippingPrice'}).text
            delivery = float(re.findall(r"\d+\.\d+", delivery_msg)[0])
        except:
            logger.exception('Delivery is unknown. Please find out the problem')
            delivery = 'Unknown'

    print('Delivery: +', delivery)
    return [seller_name, price, delivery]

def get_item_details(part):
    '''
    Gets the details of the product from the direct_url
    :param part: the part in question
    :return: the report which is a list
    '''
    assert isinstance(part, Part), 'the part must be a Part instance'
    try:
        part_req = requests.get(part.amazon_sellers_url)
        page_soup = soup(part_req.text, 'html.parser')
    except:
        logger.exception('Site not found')
        return None

    seller_containers = page_soup.findAll('div', {'class': "a-row a-spacing-mini olpOffer"})
    cheapest = []
    amazon = []
    for seller_cont in seller_containers:
        name, price, delivery = get_seller_details(seller_cont)
        if name.lower().__contains__('amazon'):
            if amazon == []:
                amazon.extend([name, price, delivery])
        else:
            if cheapest == []:
                cheapest.extend([name, price, delivery])

        if len(cheapest) > 1 and len(amazon) > 1:
            break
    # check if both the cheapest and the amazon have entries
    if not len(amazon) > 1:
        amazon = ['N.A', 'N.A', 'N.A']
    if not len(cheapest) > 1:
        cheapest = ['N.A', 'N.A', 'N.A']
    report = amazon
    report.extend(cheapest)

    return report

def prepare_part_result(part, report):
    '''
    Prepares the _result of the part after evaluating it
    :param part: the part in question
    :param report: the report of evaluation
    :return:
    '''
    if report == None:
        part._result = [date, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown']
    else:
        assert isinstance(report, list) and len(report)==6, 'Report must be a list of 6 values'
        result = [date]
        result.extend(report)
        part._result = result

def main(parts_list):
    df_dict = dict()
    # iterates through the parts list
    for part in parts_list:
        assert isinstance(part, Part), 'part argument must be a Part Object'
        report = get_item_details(part) # get report from utils
        prepare_part_result(part, report) # from utils
        name, result = create_xl_df(part, AMAZON_XL, AMAZON_HEADERS) # from utils
        # writes the df into the dictionary
        df_dict[name] = result
        print('Done')
    # writes in the excel
    with pd.ExcelWriter(AMAZON_XL) as xlwriter:
        for key in tuple(df_dict.keys()):
            df_dict[key].to_excel(xlwriter, key)
            print('Done writing for: ', key)

if __name__ == '__main__':
    # logging session start
    session_start_msg = '''
===============
SESSION STARTED
===============
    '''
    logging.info(session_start_msg)
    print(session_start_msg)
    list_of_parts = []
    # logging items selected
    for part in AMAZON_PRODUCT_LIST:
        list_of_parts.append(part.name)

    logging.info('Getting info for {} from Amazon\n'.format(list_of_parts))
    # start getting products info
    main(AMAZON_PRODUCT_LIST)