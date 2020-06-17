import requests
import time
from bs4 import BeautifulSoup as soup
from envs import *
from Parts import *

# To get the session info
session_start = time.strftime('%d/%m/%Y_%H.%M')
date, time = session_start.split('_')
NEWEGG_PRODUCT_LIST = [
    CPU('Ryzen 3 3300X', 3.8, 4, 8, 'AMD'), \
    CPU('Ryzen 5 3600', 3.6, 6, 12, 'AMD'), \
    CPU('Ryzen 7 3700X', 3.6, 8, 16, 'AMD', '100-100000071BOX'), \
    CPU('Ryzen 7 3800X', 3.9, 8, 16, 'AMD'), \
    CPU('Ryzen 9 3900X', 3.8, 12, 24, 'AMD')
]
# For logging
logging.basicConfig(filename='logs/newegg_log.md', filemode='a+', format='%(asctime)s - %(levelname)s - %(message)s'\
                    ,datefmt=('%d/%m/%Y, %H%M'), level=logging.INFO)
logger = logging.getLogger()

def shipping_fee_checker(page_soup):
    '''
    Checks whether shipping is free for this product
    :param page_soup: the souped page
    :return: True or False depending on whether the shipping is free
    '''
    try:
        promo_list = page_soup.find_all('div', {'class': 'SegmentPromo'})
    except Exception as e:
        print(type(e), e)
    else:
        for promo in promo_list:
            promotion = promo.h2.text
            if promotion.__contains__('Free Shipping'):
                return True

        return False


def get_product_details(product_url):
    '''
    Checks the details of this product including:
    - free shipping (True or False)
    - price (str to 2 dp)
    - best rating
    - worst rating
    :param product_url:
    :return:
    '''
    product_req = requests.get(product_url)
    page_soup = soup(product_req.text, 'html.parser')
    # print(page_soup.prettify())

    free_shipping = shipping_fee_checker(page_soup)
    # print('Free Shipping:', free_shipping)
    script = page_soup.findAll('script', {'type': "application/ld+json"})[-1].contents
    product_json = json.loads(''.join(script))
    price = product_json['offers']['price']
    # print('Price: ', price)
    rating_dict = product_json['review'][0]['reviewRating']
    best_rating, worst_rating = rating_dict['bestRating'], rating_dict['worstRating']
    # print('Best Rating: ', best_rating)
    # print('Worst Rating: ', worst_rating)
    return (price, best_rating, worst_rating, free_shipping)

def get_item_details(part):
    '''
    Gets item details from new egg
    :param part: the part (Part obj) in question
    :return:
    '''
    search_url = part.create_search_url('NewEgg')
    search_req = requests.get(search_url)
    page_soup = soup(search_req.text, 'html.parser')

    search_results = page_soup.find_all('div', {'class': 'item-container'})
    scores = []
    names_urls = []

    for product in search_results:
        item_title = product.find('a', {'class': 'item-title'})

        product_name = product.a.img['alt']
        product_url = item_title['href']
        score = part.evaluate(product_name)
        # convert to int to allow score evaluation
        score = int(score)
        scores.append(score)
        names_urls.append([product_name, product_url])

        # print('Product: ', product_name)
        # print('Product URL: ', product_url)

    completed = False

    while not completed:
        product_index = scores.index(max(scores))
        if not max(scores) >= part.min_score:
            return None
        product_url = names_urls[product_index][1]
        try:
            product_details = get_product_details(product_url)
        except KeyError:
            logger.exception('This product is out of stock')
            scores.pop(product_index)
            names_urls.pop(product_index)
            continue
        except Exception as e:
            print(type(e), e)
            logger.exception('Unknown error found. Please check the system')
            raise
        else:
            completed = True

        if len(scores) == 0:
            return None

    report = [names_urls[product_index][0], names_urls[product_index][1]]

    for detail in product_details: # price, best, worst, free_shipping
        report.append(detail)

    return tuple(report)

def prepare_part_result(part, report):
    '''
    Prepares the result of the part after evaluating it
    :param part: the part in question
    :param report: the report of evaluation
    :return:
    '''
    if report == None:
        part.set_result(date, 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown')
    else:
        assert len(report) in range(5,7), 'Check the number of arguments in your report'
        name, url, price, best, worst, shipping = report
        part.set_result(date, name, price, url, best, worst, shipping)

def main(parts_list):
    df_dict = dict()
    # iterates through the parts list
    for part in parts_list:
        assert isinstance(part, Part), 'part argument must be a Part Object'
        try:
            report = get_item_details(part) # get report from utils
            prepare_part_result(part, report) # from utils
            name, result = create_xl_df(part, NEWEGG_XL, TEMP_NE_XL, NEWEGG_HEADERS) # from utils
        except:
            logger.exception('Fatal Error while scarping newegg')
            continue
        else:
            df_dict[name] = result
    # writes in the excel
    with pd.ExcelWriter(TEMP_NE_XL) as xlwriter:
        for key in tuple(df_dict.keys()):
            df_dict[key].to_excel(xlwriter, key)
            print('Done writing for: ', key)

if __name__ == '__main__':
    session_start_msg = '''
===============
SESSION STARTED
===============
        '''
    logging.info(session_start_msg)
    print(session_start_msg)
    # logging items selected
    list_of_parts = []
    for part in NEWEGG_PRODUCT_LIST:
        list_of_parts.append(part.name)

    logging.info('Getting info for {} from NewEgg\n'.format(list_of_parts))
    # starts the main process
    main(NEWEGG_PRODUCT_LIST)

    res = commit('NewEgg')
    if res:
        logging.info('Committed changes to NewEgg')
    else:
        logging.info('Didn\'t commit changes to NewEgg')

    # part2 = CPU('Ryzen 9 3900X', 3.8, 12, 24, 'AMD')
    # print(get_item_details(part2))
    #
    # part3 = CPU('Ryzen 3 3300X', 3.8, 4, 8, 'AMD')
    # print(get_item_details(part3))
