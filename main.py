import pandas as pd

# This is a Public School based table with the following filters applied: State(s) (All Years): All 50 + DC
# Data Source: U.S. Department of Education National Center for Education Statistics Common Core of Data (CCD) "Public Elementary/Secondary School Universe Survey" 2021-22 v.1a.
SCH_LVL = 'School Level (SY 2017-18 onward) [Public School] 2021-22'
AGC_ID = 'Agency ID - NCES Assigned [Public School] Latest available year'
AGC_NAME = 'Agency Name [Public School] 2021-22'
HSPC = 'Hispanic Students [Public School] 2021-22'
WHITE = 'White Students [Public School] 2021-22'
ASIAN = 'Asian or Asian/Pacific Islander Students [Public School] 2021-22'
BLK = 'Black or African American Students [Public School] 2021-22'
TOTAL = 'Total Race/Ethnicity [Public School] 2021-22'
STATE = 'State Name [Public School] Latest available year'

type_options = ['white_v_hispanic', 'asian_v_hispanic', 'hispanic_v_non', 'asian_v_non',
                'white_v_non']

size_options = ['small', 'medium', 'large']


# All schools w/ more than 1 school
# CALIFORNIA HIGH SCHOOLS
# 18th, 95th percentile
# Ranking of FUHSD: 340/359
# Ranking of Palo Alto Unified: 142/359
# ALL SCHOOLS
# 171st, 94th percentile
# Ranking of FUHSD: 2574/2746
# Ranking of Palo Alto Unified: 992/2746


# † indicates that the data are not applicable.
# – indicates that the data are missing.
# ‡ indicates that the data do not meet NCES data quality standards.
def get_high_schools_districts(type):
    df = pd.read_csv('data/us.csv')
    df = df[df[SCH_LVL] == 'High']
    nulls = ['†', '–', '‡']
    df = df[~df[AGC_ID].isin(nulls)]
    df = df[~df[TOTAL].isin(nulls)]

    df[TOTAL] = df[TOTAL].astype(int)

    if 'hispanic' in type:
        df = df[~df[HSPC].isin(nulls)]
        df[HSPC] = df[HSPC].astype(int)

    if 'asian' in type:
        df = df[~df[ASIAN].isin(nulls)]
        df[ASIAN] = df[ASIAN].astype(int)

    if 'black' in type:
        df = df[~df[BLK].isin(nulls)]
        df[BLK] = df[BLK].astype(int)

    if 'white' in type:
        df = df[~df[WHITE].isin(nulls)]
        df[WHITE] = df[WHITE].astype(int)

    return df.groupby(AGC_ID)


def get_dissimilarity(df, type):
    group_a = 0
    if type == 'brown_v_non':
        group_a = df[BLK].sum() + df[HSPC].sum()
    elif type == 'white_v_non':
        group_a = df[WHITE].sum()
    elif type == 'asian_v_non':
        group_a = df[ASIAN].sum()
    elif type == 'hispanic_v_non':
        group_a = df[HSPC].sum()
    group_b = df[TOTAL].sum() - group_a
    if type == 'asian_v_hispanic':
        group_a = df[ASIAN].sum()
        group_b = df[HSPC].sum()
    elif type == 'white_v_hispanic':
        group_a = df[WHITE].sum()
        group_b = df[HSPC].sum()
    if df[TOTAL].sum() == 0 or group_a == 0 or group_b == 0:
        return -1
    dis = 0
    for idx, school in df.iterrows():
        group_a_school = 0
        if type == 'brown_v_non':
            group_a_school = school[BLK] + school[HSPC]
        elif type == 'white_v_non':
            group_a_school = school[WHITE]
        elif type == 'asian_v_non':
            group_a_school = school[ASIAN]
        elif type == 'hispanic_v_non':
            group_a_school = school[HSPC]

        group_b_school = school[TOTAL] - group_a_school
        if type == 'asian_v_hispanic':
            group_a_school = school[ASIAN]
            group_b_school = school[HSPC]
        elif type == 'white_v_hispanic':
            group_a_school = school[WHITE]
            group_b_school = school[HSPC]
        dis += abs((group_a_school / group_a) - (group_b_school / group_b))
    return dis / 2


def rank_schools(size, type):
    districts = get_high_schools_districts(type)
    district_segs = {'District Name': [], 'nces_id': [], 'Dissimilarity': [], 'State': [], 'Size': []}
    for district, df in districts:
        # must have more than 1 schools
        if df.shape[0] < 2:
            continue
        min_size = 0
        if size == 'small':
            min_size = 2000
        elif size == 'medium':
            min_size = 5000
        elif size == 'large':
            min_size = 10000
        if df[TOTAL].sum() < min_size:
            continue
        dis = get_dissimilarity(df, type)
        if dis == -1:
            continue
        district_segs['Dissimilarity'].append(dis)
        district_segs['nces_id'].append(district)
        district_segs['District Name'].append(df.iloc[0][AGC_NAME])
        district_segs['State'].append(df.iloc[0][STATE])
        district_segs['Size'].append(df[TOTAL].sum())

    district_output_df = pd.DataFrame(district_segs)
    district_output_df.sort_values(by=['Dissimilarity'], ascending=False).reset_index(inplace=True)
    district_output_df.to_csv(f'outputs/district_seg_{type}_us_{size}.csv', index=False)
    district_output_df[district_output_df['State'] == 'California'].to_csv(f'data/district_seg_{type}_ca_{size}.csv')

    print(
        f'Ranking of FUHSD: {district_output_df.index[district_output_df["District Name"] == "Fremont Union High"].tolist()[0]}')


def print_district(name, index, districts):
    if index in districts:
        print(f'Ranking of {name}: {len(districts) - districts.index(index)}/{len(districts)}')
    else:
        print(f'{name} does not satisfy criteria or does not exist')


def main():
    type = None
    size = None
    while type == None:
        print('What type of segregation would you like to compute?')
        print(type_options)
        x = input('Selection: ')
        if x in type_options:
            type = x
        else:
            print('Please enter a valid selection from the list of options')
    while size == None:
        print('What size of high schools would you like to filter by')
        print(size_options)
        x = input('Selection: ')
        if x in size_options:
            size = x
        else:
            print('Please enter a valid selection from the list of options')
    rank_schools(size, type)


main()
