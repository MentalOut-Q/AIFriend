import os
import posixpath
import uuid
from pathlib import Path
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.character import Voice
from web.views.create.character.voice.custom.create_voice import create_voice


DEFAULT_PUBLIC_MEDIA_BASE_URL = 'https://app7501.acapp.acwing.com.cn/media/'


def upload_to_cloud_tmp(local_path, filename):
    try:
        import paramiko
    except ImportError as e:
        raise RuntimeError('请先安装paramiko：pip install paramiko') from e

    host = os.getenv('VOICE_UPLOAD_SFTP_HOST')
    username = os.getenv('VOICE_UPLOAD_SFTP_USERNAME')
    remote_dir = os.getenv('VOICE_UPLOAD_REMOTE_DIR')
    if not host or not remote_dir:
        raise RuntimeError('请配置VOICE_UPLOAD_SFTP_HOST、VOICE_UPLOAD_REMOTE_DIR')

    ssh_config = {}
    ssh_config_path = Path.home() / '.ssh' / 'config'
    if ssh_config_path.exists():
        with ssh_config_path.open(encoding='utf-8') as f:
            ssh_config = paramiko.SSHConfig.from_file(f).lookup(host)

    hostname = ssh_config.get('hostname', host)
    username = username or ssh_config.get('user')
    if not username:
        raise RuntimeError('请配置VOICE_UPLOAD_SFTP_USERNAME，或在~/.ssh/config里配置User')

    port = int(os.getenv('VOICE_UPLOAD_SFTP_PORT') or ssh_config.get('port', '22'))
    password = os.getenv('VOICE_UPLOAD_SFTP_PASSWORD')
    key_filename = os.getenv('VOICE_UPLOAD_SFTP_KEY_FILE')
    if not key_filename and ssh_config.get('identityfile'):
        key_filename = ssh_config['identityfile'][0]
    if key_filename:
        key_filename = os.path.expanduser(key_filename)
    remote_path = posixpath.join(remote_dir.rstrip('/'), filename)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=hostname,
            port=port,
            username=username,
            password=password or None,
            key_filename=key_filename or None,
            timeout=15,
        )
        sftp = client.open_sftp()
        try:
            parts = [part for part in remote_dir.strip('/').split('/') if part]
            current = ''
            for part in parts:
                current = posixpath.join(current, part)
                directory = '/' + current
                try:
                    sftp.stat(directory)
                except OSError:
                    sftp.mkdir(directory)
            sftp.put(local_path, remote_path)
        finally:
            sftp.close()
    finally:
        client.close()


class CreateCustomVoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        audio = request.FILES.get('audio')
        name = request.data.get('name', '').strip()
        confirmed = request.data.get('confirm_voice_rights')

        if not audio:
            return Response({'result': '音频不能为空'})
        if not name:
            return Response({'result': '音色名称不能为空'})
        if confirmed not in ['true', '1', True]:
            return Response({'result': '请先确认该声音已获得授权'})
        if audio.size > 20 * 1024 * 1024:
            return Response({'result': '音频不能超过20MB'})
        if audio.content_type and not audio.content_type.startswith('audio/'):
            return Response({'result': '请上传音频文件'})
        if not os.getenv('VOICE_URL'):
            return Response({'result': 'VOICE_URL未配置'})
        if not os.getenv('API_KEY'):
            return Response({'result': 'API_KEY未配置'})

        try:
            ext = audio.name.rsplit('.', 1)[-1].lower() if '.' in audio.name else 'webm'
            filename = f'{uuid.uuid4().hex}.{ext}'
            relative_path = f'tmp/{filename}'
            storage = FileSystemStorage(location=settings.MEDIA_ROOT)
            saved_path = storage.save(relative_path, audio).replace('\\', '/')
            local_path = storage.path(saved_path)
            base_url = os.getenv('PUBLIC_MEDIA_BASE_URL', DEFAULT_PUBLIC_MEDIA_BASE_URL).rstrip('/') + '/'
            voice_url = urljoin(base_url, saved_path)
            try:
                upload_to_cloud_tmp(local_path, filename)
            except Exception as e:
                return Response({
                    'result': f'上传云端失败：{e}',
                    'voice_url': voice_url,
                })

            prefix = f'u{request.user.id % 1000}{uuid.uuid4().hex[:6]}'[:10]
            data = create_voice(voice_url, prefix)
            aliyun_voice_id = data.get('output', {}).get('voice_id')

            if not aliyun_voice_id:
                return Response({
                    'result': data.get('message') or data.get('code') or '音色复刻失败',
                    'voice_url': voice_url,
                    'detail': data,
                })

            voice = Voice.objects.create(
                name=name[:100],
                voice_id=aliyun_voice_id,
            )
            return Response({
                'result': 'success',
                'voice': {
                    'id': voice.id,
                    'name': voice.name,
                },
                'voice_url': voice_url,
            })
        except Exception as e:
            return Response({
                'result': '系统异常，请稍后重试',
                'detail': str(e),
            })
