from django.contrib import admin

from web.models.friend import Friend, Message, SystemPrompt
from web.models.user import UserProfile
from web.models.character import Character, Voice


# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)  #逗号千万不要删！！！！ 如果不加这个user(这是个外键, 孩子), 就是以下拉菜单的方式, 加了就是单独开一个页面加载

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author', 'voice')

admin.site.register(Voice)

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    raw_id_fields = ('me', 'character',) # 把所有的外键全部加进来

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = ('friend',)

admin.site.register(SystemPrompt)