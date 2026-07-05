from django.utils.timezone import localtime
from rest_framework.views import APIView
from rest_framework.response import Response

from web.models.post import Post, Comment, PostLike, PostFavorite
from web.models.user import UserProfile


class GetSinglePostView(APIView):
    def get(self, request):
        try:
            post_id = request.query_params.get('post_id')
            post = Post.objects.get(id=post_id)
            author = post.author

            current_profile = None
            if request.user.is_authenticated:
                current_profile = UserProfile.objects.filter(user=request.user).first()

            is_liked = False
            is_favorited = False
            if current_profile:
                is_liked = PostLike.objects.filter(post=post, user=current_profile).exists()
                is_favorited = PostFavorite.objects.filter(post=post, user=current_profile).exists()

            comments_raw = Comment.objects.filter(post=post).order_by('create_time')
            comments = []
            for comment in comments_raw:
                comment_author = comment.author
                comments.append({
                    'id': comment.id,
                    'content': comment.content,
                    'image': comment.image.url if comment.image else '',
                    'create_time': localtime(comment.create_time).strftime('%Y-%m-%d %H:%M'),
                    'author': {
                        'user_id': comment_author.user_id,
                        'username': comment_author.user.username,
                        'photo': comment_author.photo.url,
                    }
                })

            return Response({
                'result': 'success',
                'post': {
                    'id': post.id,
                    'content': post.content,
                    'image': post.image.url if post.image else '',
                    'create_time': localtime(post.create_time).strftime('%Y-%m-%d %H:%M'),
                    'like_count': PostLike.objects.filter(post=post).count(),
                    'comment_count': comments_raw.count(),
                    'favorite_count': PostFavorite.objects.filter(post=post).count(),
                    'is_liked': is_liked,
                    'is_favorited': is_favorited,
                    'author': {
                        'user_id': author.user_id,
                        'username': author.user.username,
                        'photo': author.photo.url,
                    },
                    'comments': comments,
                }
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })