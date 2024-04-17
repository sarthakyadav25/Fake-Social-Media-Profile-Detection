from django.db import models
from traitlets import default

class Profile(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    num_posts = models.IntegerField()
    followers = models.IntegerField()
    following = models.IntegerField()
    bio = models.CharField(max_length=300)
    profile_pic = models.ImageField()
    fake = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.name} searched {self.username}"
