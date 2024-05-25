from django.contrib import admin

from oglas.models import *

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Ad)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Message)
admin.site.register(Event)
admin.site.register(Wishlist)