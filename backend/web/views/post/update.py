from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.post import Post
from web.views.utils.photo import remove_old_photo


class UpdatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            post_id = request.data['post_id']
            post = Post.objects.get(id=post_id, author__user=request.user)

            content = request.data.get('content', post.content).strip()[:5000]
            image = request.FILES.get('image', None)
            remove_image = str(request.data.get('remove_image', '')).lower() in ('true', '1')

            if image:
                remove_old_photo(post.image)
                post.image = image
            elif remove_image:
                remove_old_photo(post.image)
                post.image = None

            if not content and not post.image:
                return Response({'result': '内容和图片不能同时为空'})

            post.content = content
            post.update_time = now()
            post.save()

            return Response({
                'result': 'success',
                'content': post.content,
                'image': post.image.url if post.image else '',
            })
        except:
            return Response({'result': '系统异常，请稍后重试'})