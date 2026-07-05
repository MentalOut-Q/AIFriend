from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.post import Post, PostLike
from web.models.user import UserProfile


class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            post_id = request.data['post_id']
            post = Post.objects.get(id=post_id)

            like = PostLike.objects.filter(post=post, user=user_profile).first()
            if like:
                like.delete()
                is_liked = False
            else:
                PostLike.objects.create(post=post, user=user_profile)
                is_liked = True

            return Response({
                'result': 'success',
                'is_liked': is_liked,
                'like_count': PostLike.objects.filter(post=post).count(),
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
