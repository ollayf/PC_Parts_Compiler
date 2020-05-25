from envs import *
from scraper_utils import *

class Part(object):
    '''
    A part of the PC which should have a
    - Name
    - Price
    - Best Rating
    - Worst Rating
    -
    '''
    clock_speed_w = 1
    clock_speed_threshold = 0.1

    name_w = 1
    brand_w = 1

    NEWEGG_BASE_URL = 'https://www.newegg.com/global/sg-en/p/pl?d={}' # search+query+string
    AMAZON_BASE_URL = 'https://www.amazon.sg/s?k={}&ref=nb_sb_noss' # search+query+string
    AMAZON_SELLER_BASE_URL = 'https://www.amazon.sg/gp/offer-listing/{}/ref=dp_olp_new_mbc?ie=UTF8&condition=new' # product id
    model_no_w = 100

    def __init__(self, name, brand, model_no):
        self.name = name
        self.brand = brand
        self.model_no = model_no

    def set_result(self, date, name, price, url, best_rating, worst_rating, free_shipping=False):
        if free_shipping:
            shipping = 'Free'
        else:
            shipping = 'Unknown'
        if not price == 'Unknown':
            price = float(price)
            best_rating = int(best_rating)
            worst_rating = int(worst_rating)
        self.result = Result(date, name, price, url, best_rating, worst_rating, free_shipping)
        self._result = [date, name, price, url, best_rating, worst_rating, shipping]

    def create_search_url(self, site):
        '''
        Converts the name of the part into
        :param self: Part object to create a search url for
        :param site: 'NewEgg' or 'Amazon' not caps sensitive
        :return:
        '''
        # convert site to lower case
        site = site.lower()
        assert site == 'amazon' or site == 'newegg', 'Please input a valid site'
        name = self.name
        if site == 'amazon':
            base_url = self.AMAZON_BASE_URL
        else:
            base_url = self.NEWEGG_BASE_URL
        search_lang = name.split()
        search_lang = '+'.join(search_lang)
        search_url = base_url.format(search_lang)
        return search_url

class CPU(Part):
    clock_speed_w = 1
    clock_speed_t = 0.1

    cores_w = 1
    threads_w = 0.5

    min_score = 3.5

    result = None
    def __init__(self, name, clock_speed, cores, threads, brand, model_no=None):
        self.name = name
        self.clock = clock_speed
        self.cores = cores
        self.threads = threads
        self.brand = brand
        self.model_no = model_no
        if model_no != None:
            self.amazon_sellers_url = self.AMAZON_SELLER_BASE_URL.format(model_no)

    def evaluate(self, product_name):
        score = 0
        score += check_similarity(product_name, self.name) * self.name_w
        score += check_similarity(product_name, self.clock, self.clock_speed_t) * self.clock_speed_w
        score += check_similarity(product_name, self.cores) * self.cores_w
        score += check_similarity(product_name, self.threads) * self.threads_w
        score += check_similarity(product_name, self.brand) * self.brand_w
        if not self.model_no == None:
            score += check_similarity(product_name, self.model_no) * self.model_no_w
        print('Score:')
        print(f"{product_name}: {score}")
        return score


class GPU(Part):
    cores_t = 100
    clock_t = 0.2
    brand_w = 3

    identifier_w = 10

    def __init__(self, name, clock_speed, cores, brand, identifier=None, model_no=None):
        self.name = name
        self.clock = clock_speed
        self.cores = cores
        self.brand = brand
        self.identifier = identifier
        self.model_no = model_no
        if model_no != None:
            self.url

class Result(object):
    '''
    The result corresponding to the item in check
    '''
    def __init__(self, date, name, price, url, best_rating, worst_rating, free_shipping=False):
        self.date = date
        self.name = name
        self.price = price
        self.url = url
        self.best_rating = best_rating
        self.worst_rating = worst_rating
        if free_shipping:
            self.shipping = 'Free'
        else:
            self.shipping = 'Unknown'

    def __repr__(self):
        return str(list(self.date, self.name, self.price, self.url, self.best_rating, self.worst_rating, self.shipping))

    def __dir__(self):
        return (self.date, self.name, self.price, self.url, self.best_rating, self.worst_rating, self.shipping)
