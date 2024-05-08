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

#### Drives
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

#### Plays

After pulling play data a couple of data issues were noticed looking at carries for Leshon Williams & Kaleb Johnson.
Below is a query to pull the rushing numbers for Leshon Williams on a game by game basis
```
select game_id,defense, count(*) as carries, sum(yards_gained) 
from cfbd.plays 
where play_type in ('Rush', 'Rushing Touchdown', 'Fumble Recovery (Own)', 'Fumble Recovery (Opponent)', 'Penalty') 
and offense = 'Iowa' 
and play_text like '%Leshon Williams%'
group by game_id, defense
order by game_id;
```
The plays that have issues are very often plays with penalties or plays that involve turnovers(in particular fumbles).

The ESPN play by play for them is often missing data as well. In particular in the Michigan St game, Leshon Williams had run for 3 yards that resulted in a Michigan St fumble return for a TD. The play by play text was `Cal Haladay 42 Yd Fumble Return (Jonathan Kim Kick)` The `yards_gained` value was 42y as well. This leaves you with a missing carry for 3 yards and no way to parse it out. To manually correct the below was done:

```
UPDATE cfbd.plays SET
play_text = 'Leshon Williams rush for 3 yards, fumbled, recovered by Cal Haladay. Cal Haladay 42 Yd Fumble Return (Jonathan Kim Kick)'::character varying, yards_gained = '3'::smallint WHERE
id = '401520281103869101';
```

You can always cross check these play by play lines on the official NCAA site [play-by-play](https://www.ncaa.com/game/6154097/play-by-play) as well:
```
 (13:15) Williams,Leshon rush left for 3 yards gain to the IOW42 fumbled by Williams,Leshon at IOW42 forced by Adeleye,Tunmise recovered by MSU Haladay,Cal at IOW42 Haladay,Cal return 42 yards to the IOW00 TOUCHDOWN, clock 13:08.
```

Another error that had to be corrected was a play that was listed as a 2 yard gain in the Nebraska game that should have been a 2 yard loss. Below is the update that was run:

```
UPDATE cfbd.plays SET
yards_gained = '-2'::smallint, play_text = 'Leshon Williams run for a loss of 2 yds to the IOWA 35'::character varying WHERE
id = '401520425104949206';
```

The only error that showed up for Kaleb Johnson's numbers was a carry vs Utah St for 2 yards that had a facemask penalty tacked on and it had `yards_gained` set to `15`. The below update was done to correct it:

```
UPDATE cfbd.plays SET
yards_gained = '2'::smallint, play_text = 'Kaleb Johnson rush for 2 yards to the Iowa 47. Utah State Penalty, Face mask (15 yards) (Jaiden Francois) to the USU 38 for a 1ST down'::character varying WHERE
id = '401520157101954901';
```

It's likely there are other data issues that will show up over time that I'll try to document here. 