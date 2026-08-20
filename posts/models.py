from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Tag(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class Post(models.Model):
    STATUS_CHOICES = [
        ('public', 'Công khai'),
        ('private','Riêng tư'),
    ]
    title = models.CharField(max_length=50)
    description = RichTextField()
    author = models.CharField(max_length=30)  # Tên hiển thị
    author_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='public')
    img_thumbnail = models.CharField(max_length=200, blank=True, null=True)
    tag = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self): return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'Comment by {self.author.username}'