import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.views import Response
from apps.article.models import Article, Tags, Comment
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from apps.article.apis.serializers import ArticleSerializer, ArticleDetailSerializer, ArticleListSerializer, TagsSerializer, \
    CommentSerializer, CommentCreateSerializer
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema
from apps.article.permissions import ArticlePermission


@extend_schema(tags=["Article APIS"])
class ArticlesList(ListAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleListSerializer
    queryset = Article.objects.all()
    pagination_class = PageNumberPagination


@extend_schema(tags=["Article APIS"])
class ArticleAPI(CreateAPIView):

    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated,)

@extend_schema(tags=["Tags API"])
class TagsList(ListCreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = TagsSerializer
    queryset = Tags.objects.all()
    pagination_class = PageNumberPagination


@extend_schema(tags=["Search API"])
class SearchAPI(ListAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        name = self.request.GET.get('name')
        queryset = Article.objects.filter(Q(tags__name=name) | Q(title__icontains=name))
        return queryset


@extend_schema(tags=["Article APIS"])
class ArticleDetail(RetrieveUpdateDestroyAPIView):

    permission_classes = (IsAuthenticated, ArticlePermission)
    serializer_class = ArticleDetailSerializer

    def get_object(self):
        queryset = Article.objects.get(slug=self.kwargs['slug'])
        return queryset


@extend_schema(tags=["ThirdParty APIS"])
class ThirdPartyArticleList(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        url = ('https://newsapi.org/v2/top-headlines?'
               'country=us&'
               'apiKey=81a95fb3dc414362b56882f978ff0261')
        response = requests.get(url=url)
        return Response(response.json())


@extend_schema(tags=["Article APIS"])
@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def toggle_article_upvote(request, slug):
    article = get_object_or_404(Article, slug=slug)
    user = request.user

    if article.downvotes.filter(id=user.id).exists():
        article.downvotes.remove(user)

    if article.upvotes.filter(id=user.id).exists():
        article.upvotes.remove(user)
        action = 'removed upvote'
    else:
        article.upvotes.add(user)
        action = 'added upvote'

    return Response({
        "data": action,
    })


@extend_schema(tags=["Article APIS"])
@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def toggle_article_downvote(request, slug):
    """Toggle downvote for an article"""
    article = get_object_or_404(Article, slug=slug)
    user = request.user

    if article.upvotes.filter(id=user.id).exists():
        article.upvotes.remove(user)

    if article.downvotes.filter(id=user.id).exists():
        article.downvotes.remove(user)
        action = 'removed downvote'
    else:
        article.downvotes.add(user)
        action = 'added downvote'

    return Response({
        "data": action,
    })


@extend_schema(tags=["Comment APIS"])
class CommentListCreateView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        content_type_name = self.kwargs.get('content_type')
        object_id = self.kwargs.get('object_id')
        try:
            content_type = ContentType.objects.get(model=content_type_name.lower())
            return Comment.objects.filter(
                content_type=content_type,
                object_id=object_id
            ).select_related('created_by').prefetch_related('upvotes', 'downvotes')
        except ContentType.DoesNotExist:
            return Comment.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        content_type_name = self.kwargs.get('content_type')
        object_id = self.kwargs.get('object_id')

        content_type = ContentType.objects.get(model=content_type_name)
        serializer.save(
            created_by=self.request.user,
            content_type=content_type,
            object_id=object_id
        )


@extend_schema(tags=["Comment APIS"])
class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all().select_related('created_by').prefetch_related('upvotes', 'downvotes')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]


@extend_schema(tags=["Comment APIS"])
@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def toggle_comment_upvote(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if comment.downvotes.filter(id=user.id).exists():
        comment.downvotes.remove(user)

    if comment.upvotes.filter(id=user.id).exists():
        comment.upvotes.remove(user)
        action = 'removed upvote'
    else:
        comment.upvotes.add(user)
        action = 'added upvote'

    return Response({
        "data": action,
    })


@extend_schema(tags=["Comment APIS"])
@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_comment_downvote(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if comment.upvotes.filter(id=user.id).exists():
        comment.upvotes.remove(user)

    if comment.downvotes.filter(id=user.id).exists():
        comment.downvotes.remove(user)
        action = 'removed downvote'
    else:
        comment.downvotes.add(user)
        action = 'added downvote'

    return Response({
        "data": action,
    })
