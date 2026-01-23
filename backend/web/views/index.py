#views的主要作用就是返回html
from django.shortcuts import render

def index(request):
    return render(request, 'index.html') #templates里面的html, 你用鼠标中键点''里的就可以跳转到templates里的index.html