import pandas as pd
from envs import *

df = pd.read_excel(NEWEGG_XL, sheet_name='Ryzen 9 3900X', names=NEWEGG_HEADERS, usecols=range(1, 8), skiprows=0)
print(df)