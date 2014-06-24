from django.db import models

class ProcessedFile(models.Model):
	sha256_hash = models.CharField(blank=True, null=True, max_length=255)
