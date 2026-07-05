from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.post import Post, Comment
from web.models.user import UserProfile


class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            post_id = request.data['post_id']
            content = request.data.get('content', '').strip()[:1000]
            image = request.FILES.get('image', None)

            if not content and not image:
                return Response({
                    'result': '评论内容和图片不能同时为空'
                })

            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(
                post=post,
                author=user_profile,
                content=content,
                image=image,
            )

            return Response({
                'result': 'success',
                'comment_id': comment.id,
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })