from django import forms
from mezzanine.forms.models import Form


class FormSelectorForm(forms.Form):
	title = forms.CharField(label="Título", help_text="Título da página",
		max_length=200)

	def is_valid(self):
		valid = super(FormSelectorForm, self).is_valid()
		if not valid: return valid
		try:
			Form.objects.get(title=self.cleaned_data['title'])
		except Form.DoesNotExist:
			self.add_error("title", "Página `%s` não existe" % (
				self.cleaned_data['title']))
			return False
		return True