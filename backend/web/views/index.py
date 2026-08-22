#views的主要作用就是返回html
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    vite_index = Path(settings.BASE_DIR) / 'static' / 'frontend' / 'index.html'
    if vite_index.exists():
        html = vite_index.read_text(encoding='utf-8')
        return HttpResponse(html)
    return render(request, 'index.html') #templates里面的html, 你用鼠标中键点''里的就可以跳转到templates里的index.html
