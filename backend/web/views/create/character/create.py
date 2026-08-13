from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character, Voice
from web.models.user import UserProfile


class CreateCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            name = request.data.get('name').strip()
            voice_id = request.data.get('voice_id')
            profile = request.data.get('profile').strip()[:100000]
            photo = request.FILES.get('photo', None)
            background_image = request.FILES.get('background_image', None)

            if not name:
                return Response({
                    'result': '名字不能为空'
                })
            if not profile:
                return Response({
                    'result': '角色介绍不能为空'
                })
            if not photo:
                return Response({
                    'result': '头像不能为空'
                })
            if not background_image:
                return Response({
                    'result': '聊天背景不能为空'
                })

            voice = Voice.objects.get(id=voice_id)
            story_file = request.FILES.get('story_file', None)

            character = Character.objects.create(
                author=user_profile,
                name=name,
                voice=voice,
                profile=profile,
                photo=photo,
                background_image=background_image,
                story_file=story_file,  # 有字段时
            )
            if story_file:
                # FileField 保存后才有 .path
                from web.documents.utils.insert_documents import insert_character_story
                insert_character_story(character.id, character.story_file.path)
            return Response({
                'result': 'success',
                'character_id': character.id,  # 建议返回
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
