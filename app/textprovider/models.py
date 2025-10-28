from django.db import models

class Notams(models.Model):
    notam_text = models.TextField(max_length=1500)
    part = models.CharField(max_length=255, unique=True, null=True)

    def __str__(self):
        return self.part

class ParsedNotams(models.Model):
    notam = models.OneToOneField(Notams, on_delete=models.CASCADE, related_name='parsed_notams')

    identifier = models.CharField(max_length=255, null=True)
    sec_q = models.CharField(max_length=255, null=True)
    sec_a = models.CharField(max_length=255, null=True)
    sec_b = models.CharField(max_length=255, null=True)
    sec_c = models.CharField(max_length=255, null=True)
    sec_d = models.CharField(max_length=255, null=True)
    sec_e = models.TextField(max_length=1500)
    sec_f = models.CharField(max_length=255, null=True)

    created = models.DateTimeField()
    source = models.CharField(max_length=255)

    def __str__(self):
        return 'parsed ' + self.notam.part

class Coordinates(models.Model):
    notam = models.ForeignKey(Notams, on_delete=models.CASCADE, related_name='coordinates')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    class Meta:
        unique_together = ('latitude','longitude')
