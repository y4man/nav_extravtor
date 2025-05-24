from django.db import models

class Website(models.Model):
    query = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.url

class NavbarLink(models.Model):
    website = models.ForeignKey(Website, related_name='nav_links', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    href = models.URLField()

    def __str__(self):
        return f"{self.text} -> {self.href}"
