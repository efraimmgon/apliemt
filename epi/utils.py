from django.utils.safestring import mark_safe
from mezzanine.forms.models import FormEntry, FieldEntry, Field

import os
from functools import reduce, partial


### Table representation

def ColumnHeader(label):
	"""
	Returns a column representing a single header field, containing
	the properties that mezzanine expects.
	Takes a label, which'll represent the column on a template.
	"""
	return {
		"sortable": False,
		"is_ordered_reverse": False,
		"label": label
	}

def Table(header, rows):
	"Returns a dict representing a table."
	return {"header": header, "rows": rows}


### Helper Functions for populating Table

def file_filter(acc, f):
	"""
	Checks if the FieldEntry.value is a file. If so, returns a link.
	Otherwise, returns the value
	"""
	val = f.value
	if val.startswith("forms/"):
		val = mark_safe("<a href='/form-file/%s/'>%s</a>" % (
			f.id, os.path.split(val)[1]))
	return acc + [val]

def accumulate_fields(formentry):
	"""
	Returns a list with the values for each field of a FieldEntry object
	for a given FormEntry object.
	"""
	return reduce(file_filter, 
				  FieldEntry.objects.filter(entry_id=formentry.id), 
				  [])

def fetch_header(fields):
	"""
	Returns a list with the labels for each field in a Field obj.
	"""
	return map(lambda field: ColumnHeader(field.label), fields)

def fetch_rows(formentries):
	"""
	Returns a list of lists, containing the values for each field 
	of a FieldEntry objects, for a given FormEntry object.
	"""
	return map(accumulate_fields, formentries)

def gen_table(form):
	"""
	Returns the values from a given Form object. A table is a dict with 
	two keys: `cols` and `rows`.
	"""
	return Table(header=fetch_header(Field.objects.filter(form_id=form.id)),
				 rows=fetch_rows(FormEntry.objects.filter(form_id=form.id)))


### Filtered table
def acc_specific_fields(formentry, wanted_value):
	return reduce(file_filter, 
				  FieldEntry.objects.filter(entry_id=formentry.id,
				  							value__contains=wanted_value), 
				  [])

def fetch_specific_rows(formentries, wanted_value):
	acc_fields = partial(acc_specific_fields, wanted_value=wanted_value)
	return map(acc_fields, formentries)

def gen_specific_table(form, header, identity_value, wanted_value):
	form_entries = FormEntry.objects.filter(form_id=form.id)
	submitted = filter(lambda f: FieldEntry.objects.get(entry_id=f.id, 
														value=identity_value),
					   form_entries)
	if submitted:
		return Table(header=[header],
				 	 rows=fetch_specific_rows(
				 	 	FormEntry.objects.filter(form_id=form.id),
				 	 	wanted_value))