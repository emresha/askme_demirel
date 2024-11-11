from django.contrib import admin
from app.models import *

# Register your models here.
admin.site.register(Post)
admin.site.register(PostTag)
admin.site.register(PostLike)
admin.site.register(UserProfile)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(CommentLike)