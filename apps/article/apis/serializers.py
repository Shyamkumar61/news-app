from rest_framework import serializers
from apps.article.models import Article, Comment, Tags
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ArticleListSerializer(serializers.ModelSerializer):

    total_upvotes = serializers.SerializerMethodField()
    total_downvotes = serializers.SerializerMethodField()

    def get_total_upvotes(self, obj):
        return obj.upvotes.count()

    def get_total_downvotes(self, obj):
        return obj.downvotes.count()

    class Meta:
        model = Article
        fields = (
            "title",
            "tags",
            "user",
            "slug",
            "get_description",
            "total_upvotes",
            "total_downvotes",
        )


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('name',)


class CommentSerializer(serializers.ModelSerializer):

    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()

    def get_upvotes(self, obj):
        return obj.upvotes.count()

    def get_downvotes(self, obj):
        return obj.downvotes.count()

    class Meta:
        model = Comment
        fields = (
            "comments",
            "upvotes",
            "downvotes",
        )


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ("title", "tags", "user", "description",)

    def to_representation(self, instance):
        ret = super(ArticleSerializer, self).to_representation(instance)
        ret["upvotes"] = instance.upvotes.count()
        ret["downvotes"] = instance.downvotes.count()
        ret['tags'] = [i.name for i in instance.tags.all()]
        ret['user'] = instance.user.first_name + " " + instance.user.last_name
        return ret


class ArticleDetailSerializer(serializers.ModelSerializer):

    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = '__all__'

    def get_upvotes(self, obj):
        return obj.upvotes.count()

    def get_downvotes(self, obj):
        return obj.downvotes.count()

    def to_representation(self, instance):
        ret = super(ArticleDetailSerializer, self).to_representation(instance)
        ret['tags'] = [i.name for i in instance.tags.all()]
        return ret


class CommentSerializer(serializers.ModelSerializer):
    total_upvotes = serializers.ReadOnlyField()
    total_downvotes = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = [
            'id', 'comments', 'created_by', 'total_upvotes', 'total_downvotes',
        ]
        read_only_fields = ['id', 'created_by']

    def get_total_upvotes(self, obj):
        return obj.upvotes.count()

    def get_total_downvotes(self, obj):
        return obj.downvotes.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    content_type_name = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = ['comments', 'content_type_name', 'object_id']

    def validate_content_type_name(self, value):
        try:
            content_type = ContentType.objects.get(model=value.lower())
            return content_type
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(f"Invalid content type: {value}")

    def create(self, validated_data):
        content_type_name = validated_data.pop('content_type_name')
        comment = Comment.objects.create(
            **validated_data
        )
        return comment