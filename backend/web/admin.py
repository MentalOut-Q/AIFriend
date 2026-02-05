from django.contrib import admin
from web.models.user import UserProfile
from web.models.character import Character

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)  #逗号千万不要删！！！！ 如果不加这个user, 就是以下拉菜单的方式, 加了就是单独开一个页面加载

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)
