# Copyright (c) Tuukka Norri 2022-2025
# Licenced under the MIT licence.

from enum import Enum
import re
import sensors
import socket
import sqlite3


LOG_PATH = "/home/tsnorri/temperature-monitor/templog.db"
HDDTEMP_ADDRESS = ("localhost", 7634)


class SensorType(Enum):
	LINUX_MONITORING = 1
	HDDTEMP = 2


# |/dev/disk/by-id/scsi-SATA_OCZ-AGILITY3_OCZ-…|OCZ-AGILITY3|30|C|
HDDTEMP_RE = re.compile(
	r"""
	^
	[|]											# Device path
	[/]dev[/]disk[/]by-id[/] (?P<device>[^|]+)
	[|]											# Model
	(?: [^|]*)
	[|]											# Temperature
	(?P<temperature>[0-9]+)
	[|]											# Unit
	C
	[|]
	""",
	re.X
)


def read_from_socket(address):
	def helper():
		with socket.create_connection(address) as sock:
			while chunk := sock.recv(1024):
				yield chunk
	return b''.join(helper())


def add_reading(sensor_ids, key, temperature, curs, insert_sensor_statement):
	sensor_id = sensor_ids.get(key, None)
	if sensor_id is None:
		curs.execute("INSERT INTO sensor DEFAULT VALUES RETURNING id")
		sensor_id = curs.fetchone()[0]
		curs.execute(insert_sensor_statement, (sensor_id,) + key[1:])
		sensor_ids[key] = sensor_id
	curs.execute(
		"INSERT INTO temperature (sensor_id, value) VALUES (?, ?)",
		(sensor_id, temperature)
	)
	

def process_linux_monitoring_data(sensor_ids, curs):
	for chip in sensors.iter_detected_chips():
		for feature in chip:
			# Consider temperature only.
			if 2 != feature.type:
				continue

			# Consider sensible values only.
			val = feature.get_value()
			if (val <= 0):
				continue

			# Store the reading.
			sensor_key = (SensorType.LINUX_MONITORING, chip.adapter_name, chip.prefix, chip.addr, feature.label)
			add_reading(sensor_ids, sensor_key, val, curs, "INSERT INTO sensor_linux_monitoring (id, adapter_name, prefix, addr, feature) VALUES (?, ?, ?, ?, ?)")


def process_hddtemp_data(sensor_ids, curs):
	hddtemp_data = read_from_socket(HDDTEMP_ADDRESS).decode('UTF-8')

	# Parse the data in the beginning of the string.
	while match := HDDTEMP_RE.match(hddtemp_data):
		device = match.group("device")
		val = int(match.group("temperature"))

		# Store the reading.
		sensor_key = (SensorType.HDDTEMP, device)
		add_reading(sensor_ids, sensor_key, val, curs, "INSERT INTO sensor_hdd (id, name) VALUES (?, ?)")

		# Skip to the next entry.
		hddtemp_data = hddtemp_data[match.end():]


def main():
	conn = sqlite3.connect(LOG_PATH)
	curs = conn.cursor()
	curs.execute("PRAGMA foreign_keys = ON")

	# Fetch the known sensor ids.
	sensor_ids = {}
	curs.execute("SELECT id, adapter_name, prefix, addr, feature FROM sensor_linux_monitoring")
	for (sensor_id, adapter_name, prefix, addr, feature) in curs.fetchall():
		sensor_ids[(SensorType.LINUX_MONITORING, adapter_name, prefix, addr, feature)] = sensor_id
	curs.execute("SELECT id, name FROM sensor_hdd")
	for (sensor_id, name) in curs.fetchall():
		sensor_ids[(SensorType.HDDTEMP, name)] = sensor_id

	# Read the temperatures.
	process_linux_monitoring_data(sensor_ids, curs)
	process_hddtemp_data(sensor_ids, curs)
	conn.commit()
	conn.close()


if __name__ == "__main__":
	try:
		sensors.init()
		main()
	finally:
		sensors.cleanup()
