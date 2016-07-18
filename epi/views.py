from django.shortcuts import get_object_or_404, render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from mezzanine.forms.models import Form, FieldEntry
from mezzanine.conf import settings

import os
from mimetypes import guess_type

from .forms import FormSelectorForm
from .utils import gen_table

fs = FileSystemStorage(location=settings.FORMS_UPLOAD_ROOT)


def table_form(request):
	form = FormSelectorForm()
	table = None
	if request.GET.get("title"):
		form = FormSelectorForm(request.GET)
		if form.is_valid():
			table = gen_table(
				form=Form.objects.get(title=form.cleaned_data['title']))
	context = {"table": table, "settings": settings, "form": form}
	return render(request, "formtable.html", context)


def download_file(request, field_entry_id):
	field_entry = get_object_or_404(FieldEntry, id=field_entry_id)
	path = os.path.join(fs.location, field_entry.value)
	response = HttpResponse(content_type=guess_type(path)[0])
	with open(path, "r+b") as f:
		response["Content-Disposition"] = "attachment; filename=%s" % f.name
		response.write(f.read())
	return response

def show_receipt():
	form = Form.objects.get(title="Inscrições EPI")
	form_entries = FormEntry.objects.filter(form_id=form.id)
	filter_value = "field2"
	def from_user_p(f):
		return FieldEntry.objects.get(entry_id=f.id, value=filter_value)
	submitted = filter(from_user_p, form_entries)
	if submitted:
		return map(acc_specific_fields, submitted)