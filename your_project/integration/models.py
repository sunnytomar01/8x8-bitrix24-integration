from django.db import models

class CallRecording(models.Model):
    call_id = models.CharField(max_length=255)
    recording_url = models.URLField()
    lead_id = models.IntegerField()
    uploaded = models.BooleanField(default=False)

    def __str__(self):
        return f"Call ID: {self.call_id}, Lead ID: {self.lead_id}"
