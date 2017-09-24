from django.contrib import admin

# Register your models here.

from mptt.admin import MPTTModelAdmin
from SchoolBuy.models import *

admin.site.register(GoodsType, MPTTModelAdmin)
admin.site.register(UserProfile)
admin.site.register(GoodsMessage)
admin.site.register(GoodsWords)
