from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.post import Post
from web.models.user import UserProfile


class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            content = request.data.get('content', '').strip()[:5000]
            image = request.FILES.get('image', None)

            if not content and not image:
                return Response({
                    'result': '内容和图片不能同时为空'
                })

            post = Post.objects.create(
                author=user_profile,
                content=content,
                image=image,
            )
            return Response({
                'result': 'success',
                'post_id': post.id,
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })