from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
class PictureAI(models.Model):
    img_AI=models.CharField(max_length=200, blank=True, null=True)
    description=RichTextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    