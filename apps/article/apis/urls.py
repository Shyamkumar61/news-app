from django.urls import path
from apps.article.apis import views
from apps.article.apis.views import TagsList

urlpatterns = [
    path('', views.ArticlesList.as_view()),
    path('posts/', views.ArticleAPI.as_view()),
    path('posts/<slug:slug>/', views.ArticleDetail.as_view()),
    path('fetch-posts/', views.ThirdPartyArticleList.as_view()),
    path('search', views.SearchAPI.as_view()),
    path('tags/', TagsList.as_view()),
    path('<str:content_type>/<int:object_id>/comments/', views.CommentListCreateView.as_view(),
         name='comment-list-create'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('posts/<slug:slug>/upvote/', views.toggle_article_upvote, name='article-upvote'),
    path('posts/<slug:slug>/downvote/', views.toggle_article_downvote, name='article-downvote'),
    path('comment/<int:comment_id>/upvote/', views.toggle_comment_upvote, name='article-upvote'),
    path('comment/<int:comment_id>/downvote/', views.toggle_comment_downvote, name='article-downvote'),
]