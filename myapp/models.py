from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    pass 

class FriendRequest(models.Model):
    STATUS_CHOICES = (("send","Sent"),("accepted","Accepted"),("rejected","Rejected"),)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="send_requests",on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="received_requests",on_delete=models.CASCADE)
    status = models.CharField(max_length=8,choices=STATUS_CHOICES,default="sent")
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("sender","receiver")
    def __str__ (self):
        return f"{self.sender} -> {self.receiver} :{self.status}"