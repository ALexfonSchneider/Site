from django.db import models

class Path(models.Model):
    system_path = models.TextField()
    uri = models.TextField(unique=True)

    def __str__(self):
        return f'{self.uri}'

    def get_absolute_url(self):
        return  f'/WebExplorer/{self.uri}'