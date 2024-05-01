# cfbd-api-scape

This repo contains a simple example of how to pull drive data from the cfbd [API](https://api.collegefootballdata.com/api/docs/?url=/api-docs.json) and persist it in Postgres, this can be found in `cfbd-drives-scape.py`
It requires a valid `CFBD_API_KEY` value be passed in as an env variable and one can be obtained [here](https://collegefootballdata.com/key).

It is currently set up to persist the results of that drive API call to a postgres instance. You need to pass in 4 additional env variables for that postgres connection:


`'POSTGRES_USER'`

`'POSTGRES_PW'`

`'POSTGRES_HOST'`

`'POSTGRES_DB'`


The postgres table def that was used is [here](/sql/create_drives_table.sql)

This repo also contains an example of filtering out garbage time drives from that dataset using bcftoys [rules](https://www.bcftoys.com/notes#garbage) and writing it back to postgres. This can be found in `filter-drives.py`

### Data issues found
There are several data issues with the raw data set for Iowa's drives in the data for 2021-2023. Either the `end_o_score` column or the `start_o_score` column data was wrong( ie `drive_result` was `TD` but `end_o_score` and `start_o_score` were the same value) causing the calculation for how many points a drive yielded to be wrong. Below are the `drive_id` values that needed to be fixed.
```
drive_id
40152022711
40152022718
40140508223
4012827215
40128275618
40128275826
40128276212
```

An easy way to query this data to check it is to run this query(per year):

```sql
select defense, SUM(end_o_score - start_o_score) as offensive_points_scored
from cfbd.drives 
where year = '2023'
and offense = 'Iowa'
group by defense;
```

This should output look like this if data issues have been corrected:

| defense | offensive_points_scored |
----   | ---- |
Utah State | 24
Iowa State |13
Western Michigan  | 39
Penn State | 0
Michigan State | 19
Purdue | 20
Wisconsin | 13
Minnesota | 10
Northwestern |10
Rutgers   | 22 |  
Illinois | 13
Nebraska | 13
Michigan | 0
Tennessee | 0