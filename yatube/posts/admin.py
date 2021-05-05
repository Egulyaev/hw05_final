from django.contrib import admin

from .models import Group, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date",
                    "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug", "description")
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'created')
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)