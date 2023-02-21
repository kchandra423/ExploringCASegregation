import os
import pprint

import dotenv
from census import Census
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv('API_KEY')
POPULATION = 'B03001_001E'
HISPANIC = 'B03001_003E'

# MONGO_PSWRD = os.getenv('MONGO_PASSWORD')
c = Census(KEY)
x = c.acs5.get(('NAME', HISPANIC),
                geo={'for': 'school district (secondary):*',
                     'in': f'state:06'})
pprint.pprint(x)