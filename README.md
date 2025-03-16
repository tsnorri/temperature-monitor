# temperature-monitor
(Yet another) temperature logger for [lm-sensors](https://github.com/lm-sensors/lm-sensors) and [hddtemp](https://savannah.nongnu.org/projects/hddtemp/).

## Purpose

Read the temperature values from lm-sensors and hddtemp and store them to a [SQLite 3](https://sqlite.org/) database.

## Setup

1. Configure lm-sensors and hddtemp. Hddtemp needs to be run in daemon mode.
2. Run `sqlite3 /path/to/my-temperature-database.db < schema.sql`
3. Modify *read_temperature.py* to set `LOG_PATH` to the path to the database created in step 2.
4. Run *read_temperature.py* periodically by e.g. adding an entry similar to the following line to your crontab with `crontab -e`:

```
0,5,10,15,20,25,30,35,40,45,50,55 *	*	*	*	/usr/bin/python3 /home/tsnorri/temperature-monitor/read_temperature.py
```
