import uuid

from django.utils.timezone import now

from django.db import models
from web.models.user import UserProfile


def post_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex[:10]}.{ext}'
    return f'post/images/{instance.author.user_id}_{filename}'

class Post(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to=post_image_upload_to, blank=True, null=True)  
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to=post_image_upload_to, blank=True, null=True)
    create_time = models.DateTimeField(default=now)

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('post', 'user') # 同一人只能赞一次

class PostFavorite(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('post', 'user') # 同一人只能收藏一次