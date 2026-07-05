from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.post import Post, PostFavorite
from web.models.user import UserProfile


class ToggleFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            post_id = request.data['post_id']
            post = Post.objects.get(id=post_id)

            favorite = PostFavorite.objects.filter(post=post, user=user_profile).first()
            if favorite:
                favorite.delete()
                is_favorited = False
            else:
                PostFavorite.objects.create(post=post, user=user_profile)
                is_favorited = True

            return Response({
                'result': 'success',
                'is_favorited': is_favorited,
                'favorite_count': PostFavorite.objects.filter(post=post).count(),
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })