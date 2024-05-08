import math
import os

import pandas as pd
from sqlalchemy import create_engine, text

postgres_user = os.environ['POSTGRES_USER']
postgres_pw = os.environ['POSTGRES_PW']
postgres_host = os.environ['POSTGRES_HOST']
postgres_db = os.environ['POSTGRES_DB']

db = create_engine("postgresql://{postgres_user}:{postgres_pw}@{postgres_host}/{postgres_db}"
                   .format(postgres_pw=postgres_pw,
                        postgres_user=postgres_user,
                        postgres_host=postgres_host,
                        postgres_db=postgres_db
                        )
                   )

def subtract_dataframes(df1, df2):
    df1_tuples = set(df1.apply(tuple, axis=1))
    df2_tuples = set(df2.apply(tuple, axis=1))

    filtered_tuples = df1_tuples - df2_tuples
    return pd.DataFrame(list(filtered_tuples), columns=df1.columns)

def bcf_filter_drives_for_garbage_time(year):
    conn = db.connect()

    max_drives_df = pd.read_sql(text("select game_id, max(drive_number) as total_drives from cfbd.drives where year = {year} group by game_id".format(year=year)), con=conn)
    drives_df = pd.read_sql(text("select * from cfbd.drives where year={year}".format(year=year)), con=conn)
    conn.close()

    drives_df['scoring_deficit'] = abs(drives_df['start_o_score'] - drives_df['start_d_score'])

    # implement drive filters here, rule by rule

    # An offensive possession of two plays or fewer that runs out the clock to conclude the first half,
    # or that runs out the clock to conclude the second half with the score tied,
    # and does not result in a turnover, score, or field goal attempt.
    end_of_half_or_end_of_game_result_list = ['END OF HALF', 'END OF GAME', 'END OF 4TH QUARTER', 'END OF 2ND QUARTER']
    end_of_game_result_list = ['END OF GAME', 'END OF 4TH QUARTER']
    end_of_half_result_list = ['END OF HALF', 'END OF 2ND QUARTER']

    rule_1_drives = drives_df.loc[((drives_df['plays'] <= 2) & (drives_df['drive_result'].isin(end_of_half_result_list))) | ((drives_df['drive_result'].isin(end_of_half_or_end_of_game_result_list)) & (drives_df['scoring_deficit'] == 0))]

    # A possession in the second half of a game in which eight times the number of the losing team's remaining
    # possessions plus one is less than the losing team's scoring deficit at the start of the possession.
    rule_2_drives = drives_df.loc[(drives_df['start_period'].isin([3,4]))]

    rule_2_drives = pd.merge(rule_2_drives,max_drives_df, on='game_id')
    rule_2_drives['total_remaining_possessions'] = (rule_2_drives['total_drives'] - rule_2_drives['drive_number'])
    rule_2_drives['drives_remaining'] = ( (rule_2_drives['total_drives'] - rule_2_drives['drive_number'])/ 2) # lazy but it's close, can round up on odd +1?
    rule_2_drives['drives_remaining'] = rule_2_drives['drives_remaining'].apply(lambda x: int(math.ceil(x)))

    rule_2_drives['2nd_half_magic_number'] = ((rule_2_drives['drives_remaining']) + 1 ) * 8
    rule_2_drives['rule_2_check'] = rule_2_drives['2nd_half_magic_number'] < rule_2_drives['scoring_deficit']

    rule_2_drives = rule_2_drives.drop(rule_2_drives[rule_2_drives['rule_2_check'] == False].index) # drop all but our rule_2_check = true columns
    rule_2_drives.drop(columns=['rule_2_check','drives_remaining','total_remaining_possessions','2nd_half_magic_number','total_drives'], axis=1, inplace=True)

    # An offensive possession of two plays or fewer by the losing team with a score deficit greater than eight points
    # that runs out the clock to conclude the game.
    rule_3_drives = drives_df.loc[(drives_df['plays'] <= 2) & (drives_df['scoring_deficit'] > 8) & ((drives_df['drive_result'].isin(end_of_game_result_list)))]

    # An offensive possession or non-offensive scoring possession by the winning team leading by eight points or fewer
    # at the start of the possession that runs out the clock to conclude the game.
    rule_4_drives = drives_df.loc[(drives_df['scoring_deficit'] < 8) & ((drives_df['drive_result'].isin(end_of_game_result_list)))]

    # build out the filtered dataframe
    filtered_df = subtract_dataframes(drives_df,rule_1_drives)
    filtered_df2 = subtract_dataframes(filtered_df,rule_2_drives)
    filtered_df3 = subtract_dataframes(filtered_df2,rule_3_drives)
    filtered_df4 = subtract_dataframes(filtered_df3,rule_4_drives)

    return filtered_df4


drives = bcf_filter_drives_for_garbage_time(2023)

# write result to DB
conn = db.connect()
drives.to_sql(name='drives_bcf_filtered',con=conn, if_exists='replace', schema='cfbd')
conn.commit()
conn.close()
