from django.contrib.auth.models import User
from django.utils.timezone import localtime
from rest_framework.views import APIView
from rest_framework.response import Response

from web.models.post import Post, Comment, PostLike, PostFavorite
from web.models.user import UserProfile


class GetListPostView(APIView):
    def get(self, request):
        try:
            items_count = int(request.query_params.get('items_count'))
            user_id = request.query_params.get('user_id')
            favorites = str(request.query_params.get('favorites', '')).lower() in ('1', 'true')

            queryset = Post.objects.all()
            user_profile_data = None
            current_profile = None
            if request.user.is_authenticated:
                current_profile = UserProfile.objects.filter(user=request.user).first()

            if favorites:
                if not current_profile:
                    return Response({
                        'result': '请先登录'
                    })
                # 按收藏时间倒序（PostFavorite.id 越大越新）
                queryset = queryset.filter(
                    postfavorite__user=current_profile
                ).order_by('-postfavorite__id').distinct()
            elif user_id:
                user = User.objects.get(id=int(user_id))
                author_profile = UserProfile.objects.get(user=user)
                queryset = queryset.filter(author=author_profile)
                user_profile_data = {
                    'user_id': user.id,
                    'username': user.username,
                    'profile': author_profile.profile,
                    'photo': author_profile.photo.url,
                }
                queryset = queryset.order_by('-create_time')
            else:
                queryset = queryset.order_by('-create_time')

            posts_raw = queryset[items_count: items_count + 20]

            posts = []
            for post in posts_raw:
                author = post.author
                is_liked = False
                is_favorited = False
                if current_profile:
                    is_liked = PostLike.objects.filter(post=post, user=current_profile).exists()
                    is_favorited = PostFavorite.objects.filter(post=post, user=current_profile).exists()

                posts.append({
                    'id': post.id,
                    'content': post.content,
                    'image': post.image.url if post.image else '',
                    'create_time': localtime(post.create_time).strftime('%Y-%m-%d %H:%M'),
                    'like_count': PostLike.objects.filter(post=post).count(),
                    'comment_count': Comment.objects.filter(post=post).count(),
                    'favorite_count': PostFavorite.objects.filter(post=post).count(),
                    'is_liked': is_liked,
                    'is_favorited': is_favorited,
                    'author': {
                        'user_id': author.user_id,
                        'username': author.user.username,
                        'photo': author.photo.url,
                    }
                })

            response_data = {
                'result': 'success',
                'posts': posts,
            }
            if user_profile_data:
                response_data['user_profile'] = user_profile_data

            return Response(response_data)
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })