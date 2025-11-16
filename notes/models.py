from django.db import models
class Note(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    language = models.CharField(max_length=10, default='en')
    translated_text = models.TextField(null=True, blank=True)
    translated_language = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.title} ({self.language})"
