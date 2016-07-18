from django.conf.urls import url
from .views import table_form, download_file


urlpatterns = [
	url("^form-file/(?P<field_entry_id>\d+)/$", download_file, 
		name="download_file"),
	url("^form-table/$", table_form, name="form_table"),
]