from django import forms
from .models import UploadedFile

class OtomatisasiForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['course_name', 'start_date', 'end_date', 'course_model', 'destination', 'file']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Validasi: end date tidak boleh kurang dari start date
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End Date tidak boleh kurang dari Start Date")
        return cleaned_data
