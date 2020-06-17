import time
import difflib
import re
import json
import requests
import xlrd
import os
import time
import logging
import pandas as pd
from bs4 import BeautifulSoup as soup
from envs import *
import shutil

def get_input(question, succ_msg, fail_msg):
    '''
    Gets the user input on the question asked
    :param question:
    :param succ_msg:
    :param fail_msg:
    :return:
    '''
    res = None
    while res == None:
        ans = input(question + '\n')
        if ans.lower() == 'y':
            res = True
            print(succ_msg)
        elif ans.lower() == 'n':
            res = False
            print(fail_msg)
    return res


def commit(site):
    '''
    Checks if the user wants to commit the changes
    :param website:
    :return:
    '''
    assert site == 'Amazon' or site == 'NewEgg', 'Invalid Site input'
    res = get_input(f'Commit {site}? y/n', 'Successfully committed', 'Successfully ignored')
    if res:
        if site == 'Amazon':
            os.remove(AMAZON_XL)
            os.rename(TEMP_AMAZON_XL, AMAZON_XL)
        elif site == 'NewEgg':
            os.remove(NEWEGG_XL)
            os.rename(TEMP_NE_XL, NEWEGG_XL)

    return res

def seq_match(product_name, desired_product):
    '''
    Matches a string to another string. Accuracy for string of different lengths are not good
    Typically better to be used for words only
    :param product_name:
    :param desired_product:
    :param threshold:
    :return: The ratio of similarity between the two words
    '''
    assert isinstance(product_name, str), 'Product name must be a str obj'
    assert isinstance(desired_product, str), 'Desired Product name must be a str obj'
    matcher = difflib.SequenceMatcher(None, product_name, desired_product)
    ratio = matcher.ratio()
    return ratio


def check_similarity(product_name, desired_product, value_t=0, prod_threshold=0.75, word_threshold=0.9):
    '''
    Checks the name of the product to see if it corresponds with the desired product
    :param product_name: the name of product in question
    :param desired_product: the name of the product desired
    :param value_t: If desired_product is a float value, allow a range of value_t
    :param prod_threshold: minimum similarity to accept the product
    :param word_threshold: minimum similarity of each word to accept the word
    :return: 1 or 0 of whether the name corresponds to the desired product
    '''

    assert isinstance(product_name, str), 'Product name must be a str obj'
    assert isinstance(desired_product, (str, float, int)), 'Desired Product name must be a str or float obj'

    # converts the name of the product in to a list without commas
    product_name = product_name.lower()
    product_name = product_name.replace(',', '')
    product_list = product_name.split()

    if isinstance(desired_product, str):
        # converts the name of the desired product into a list
        desired_product = desired_product.lower()
        desired_product = desired_product.replace(',', '')
        desired_list = desired_product.split()

        # check for level of correspondence
        max_score = len(desired_list)
        product_score = 0
        for word in desired_list:
            for prod_word in product_list:
                result = seq_match(word, prod_word)
                if result >= word_threshold:
                    product_score += 1
                    break

        similarity_value = product_score / max_score
        # print('Similarity Value: ', similarity_value)
        if similarity_value >= prod_threshold:
            return True

        else:
            return False
    else: # if desired product is a int or float
        if isinstance(desired_product, int):
            possible_values = re.findall(r"\d+", product_name)
        else:
            possible_values = re.findall(r"\d+\.\d+", product_name)
        for value in possible_values:
            value = float(value)
            if desired_product - value_t <= value <= desired_product + value_t:
                return True
        # if none of the numbers are similar...
        return False


def create_xl_df(part, xl_file, temp_xl_file, headers):
    '''
    After the result has been generated for the part, write the summary into the df_dict to be written in to the excel
    :param part: part to add to df_dict
    :param xl_file: path to the excel file
    :param headers: the headers to the columns
    :param df_dict: the df dict to save all the results in
    :return:
    '''
    write_columns = False
    # Checks if the file has been initiated
    if not os.path.exists(xl_file):
        with open(xl_file, 'w+') as t:
            t.write('')
        print('Excel File created at: ', xl_file)

    # creates a copy of xl file before committing
    shutil.copy(xl_file, temp_xl_file)

    try:
        df = pd.read_excel(temp_xl_file, sheet_name=part.name, names=headers, usecols=range(1,8), skiprows=0)
    except xlrd.biffh.XLRDError:
        print('This sheet is empty')
        write_columns = True
    except Exception as e:
        print(type(e), e)
        raise
    print('Result: ', str(part._result))
    if write_columns or df.empty:
        df = pd.DataFrame([part._result], columns=headers)
    else:
        print('Appending!')
        print('Initial df: ')
        print(df)
        appended_df = pd.DataFrame([part._result], columns=headers)
        df = df.append(appended_df)

    print('Final df: ')
    print(df)
    return part.name, df

if __name__ == '__main__':
    part = CPU('Ryzen 5 3600', 3.6, 6, 12, 'AMD')
    print(check_similarity('MSI GeForce RTX 2080 Ti DirectX 12 RTX 2080 Ti GAMING TRIO 11GB 352-Bit GDDR6 PCI \
    Express 3.0 x16 HDCP Ready', 'Sapphire RTX 2080 Ti'))
    write_into_xl(part, xl_file=NEWEGG_XL)