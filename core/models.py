from django.db import models

# Create your models here.
class liveModel(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    file_or_url = models.CharField(max_length=500)
    output_rtmp = models.CharField(max_length=500)
    preset = models.ForeignKey('configFFMPEGModel', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class logsProcessModel(models.Model):
    live_model = models.ForeignKey(liveModel, on_delete=models.CASCADE)
    pid = models.IntegerField()
    status = models.CharField(max_length=100, choices=[('running', 'Running'), ('stopped', 'Stopped'), ('error', 'Error')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.live_model.title} at {self.timestamp} status: {self.status}"
    
class configFFMPEGModel(models.Model):
    preset_name = models.CharField(max_length=100)
    parameters = models.TextField()

    def __str__(self):
        return self.preset_name
    

class mediaFileModel(models.Model):
    file = models.FileField(upload_to='media_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media File uploaded at {self.uploaded_at}"