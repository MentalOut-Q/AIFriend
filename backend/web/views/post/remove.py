from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.post import Post, Comment
from web.views.utils.photo import remove_old_photo


class RemovePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            post_id = request.data['post_id']
            post = Post.objects.get(id=post_id, author__user=request.user)

            for comment in Comment.objects.filter(post=post):
                remove_old_photo(comment.image)

            remove_old_photo(post.image)
            post.delete()

            return Response({
                'result': 'success',
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })