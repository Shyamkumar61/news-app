import datetime
from django.db import models
from autoslug import AutoSlugField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_extensions.db.models import TimeStampedModel


User = get_user_model()

# Create your models here.


class Tags(TimeStampedModel):

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Article(TimeStampedModel):

    title = models.CharField(max_length=100)
    images = models.ImageField(upload_to='articles/', null=True, blank=True)
    tags = models.ManyToManyField(Tags, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    slug = AutoSlugField(populate_from='title')
    comments = GenericRelation("Comment", related_name="article_comments")
    upvotes = models.ManyToManyField(User, related_name='liked_answers', blank=True)
    downvotes = models.ManyToManyField(User, related_name='dislikes_answers', blank=True)

    def get_description(self):
        return self.description[:50]

class Comment(TimeStampedModel):
    comments = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_comments')

    upvotes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    downvotes = models.ManyToManyField(User, related_name='dislikes_comments', blank=True)


    def __str__(self):
        return self.comments[:50] + '...'

    def get_created(self):
        data = datetime.fromisoformat(str(self.created))
        return data.strftime("%B %Y %I:%M %p")

    def total_upvotes(self):
        return self.upvotes.count()

    def total_downvotes(self):
        return self.downvotes.count()