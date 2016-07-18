from django.db import models


class TableModel:
	column_count = 0
	rows = []
	columns = []

	def __init__(self):
		self.rows = []
		self.columns = []


class ColumnModel:
	sortable = False
	is_ordered_reverse = False
	label = ''

	def __init__(self):
		label = ''

	def __str__(self):
		return self.label