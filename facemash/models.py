from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class FaceMash(models.Model):
    photo = models.ImageField(_("Photo"), upload_to="facemash/photos")
    ratings = models.FloatField(_("Rating"), default=1500)
    rd = models.FloatField(_("Rating Deviation"), default=350)
    sigma = models.FloatField(_("Sigma"), default=0.06)
    
    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now)

    class Meta:
        verbose_name = "FaceMash"
        verbose_name_plural = "FaceMash"
        ordering = ["-timestamp"]

    def __str__(self):
        return self.photo.name + " --- " + str(self.ratings) + " score"
