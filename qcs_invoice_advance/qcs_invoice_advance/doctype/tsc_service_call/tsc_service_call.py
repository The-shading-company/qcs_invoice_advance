# Copyright (c) 2024, Quark Cyber Systems FZC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, cstr, flt, now, nowdate, nowtime, get_system_timezone
from datetime import datetime, time, date, timedelta
from pytz import timezone


class TSCServiceCall(Document):
	def validate(self):
		if self.status == "Arranging Site Visit":
			if (self.status_time_log):
				pass
			else:
				item = []
				system_current_time = timezone_converted_datetime(datetime.now())
				current_time = system_current_time.strftime('%H:%M:%S')
				#current_time = datetime.now().strftime('%H:%M:%S')
				item.append({
					"status": self.status,
					"date": today(),
					"time": current_time,
				})
				self.update({
					"status_time_log" : item
				})

		if len(self.status_time_log) > 0:
			tab = self.status_time_log
			check = []
			item = []
			for i in range(0, len(tab)):
				item.append({
					"status": tab[i].get("status"),
					"date": tab[i].get("date"),
					"time": tab[i].get("time"),
					"hours": tab[i].get("hours")
				})
				if (self.status == tab[i].get("status")):
					check.append(1)
				else:
					check.append(0)
			if (1 not in check):

				system_current_time = timezone_converted_datetime(datetime.now())
				current_time = system_current_time.time()
				# previous_time = datetime.strptime(tab[i-1].get("time"), '%H:%M:%S')
				# current_time1 = datetime.strptime(current_time, '%H:%M:%S')

				#current_time_str = datetime.now().strftime('%H:%M:%S')
				current_date_str = date.today()
				
				previous_time_str = tab[i-1].get("time")
				previous_date_str = tab[i-1].get("date")
				if isinstance(previous_time_str, timedelta):
					pass
				else:
					previous_time_str = str_to_timedelta(previous_time_str)

				if isinstance(previous_date_str, date):
					pass
				else:
					previous_date_str = datetime.strptime(previous_date_str, "%Y-%m-%d")

				# previous_date_str = str(previous_date_str1)

				frappe.errprint(type(previous_time_str))
				frappe.errprint(type(previous_date_str))
				# previous_datetime = datetime.strptime(str(previous_date_str) + ' ' + previous_time_str, '%Y-%m-%d %H:%M:%S')
				# frappe.errprint(previous_datetime)

				combined_datetime = convert_and_combine(previous_date_str, previous_time_str)
				current_datetime = datetime.combine(current_date_str, current_time)

				#current_datetime = datetime.strptime(current_date_str + ' ' + current_time_str, '%Y-%m-%d %H:%M:%S')
				frappe.errprint(combined_datetime)
				time_diff = current_datetime - combined_datetime
				hours = time_diff.total_seconds() / 3600

				item.append({
					"status": self.status,
					"date": today(),
					"time": current_time,
					"hours": hours
				})
			frappe.errprint(item)
			if (item):
				self.update({
					"status_time_log" : item
				})


# Assuming previous_date_str is a date object and previous_time_str is a timedelta
def convert_and_combine(previous_date_str, previous_time_str):
	# Convert timedelta to time object
	hours = previous_time_str.seconds // 3600
	minutes = (previous_time_str.seconds % 3600) // 60
	seconds = previous_time_str.seconds % 60

	time_value = time(hours, minutes, seconds)

	# Combine date and time into datetime
	combined_datetime = datetime.combine(previous_date_str, time_value)
	return combined_datetime


def str_to_timedelta(time_str):
	# Parse the string into a datetime object (using a dummy date)
	dt = datetime.strptime(time_str, "%H:%M:%S")
	# Create a timedelta from the time part
	return timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)


def timezone_converted_datetime(date_time):
	system_timezone = timezone(get_system_timezone())
	datetime_in_timezone = date_time.astimezone(system_timezone)
	return datetime_in_timezone
