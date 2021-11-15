from django.contrib import admin
from .models import Place, DatePost, DayComment, DatePostComment


admin.site.register(Place)
admin.site.register(DatePost)
admin.site.register(DayComment)
admin.site.register(DatePostComment)
