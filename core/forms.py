from django import forms
from .models import liveModel, configFFMPEGModel, logsProcessModel

class LiveModelForm(forms.ModelForm):
    class Meta:
        model = liveModel
        fields = ['title', 'description', 'file_or_url', 'output_rtmp', 'preset']
        

class ConfigFFMPEGModelForm(forms.ModelForm):
    class Meta:
        model = configFFMPEGModel
        fields = ['preset_name', 'parameters']

class LogsProcessModelForm(forms.ModelForm):
    class Meta:
        model = logsProcessModel
        fields = ['live_model', 'pid', 'status']
        widgets = {
            'status': forms.Select(choices=[('running', 'Running'), ('stopped', 'Stopped'), ('error', 'Error')]),
        }

class MediaFileUploadForm(forms.Form):
    file = forms.FileField()
