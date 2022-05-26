from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.
from .models import Player, Transaction
#from .models import Profile
#
#class PlayerInline(admin.StackedInline):
#    model = Profile
#    can_delete = False
#    verbose_name_plural = 'Profile'
#    fk_name = 'user'
#
#class CustomUserAdmin(UserAdmin):
#    inlines = (PlayerInline, )
#
#    def get_inline_instances(self, request, obj=None):
#        if not obj:
#            return list()
#        return super(CustomUserAdmin, self).get_inline_instances(request, obj)
#
#
#admin.site.unregister(User)
#admin.site.register(User, CustomUserAdmin)

admin.site.register(Player)
admin.site.register(Transaction)
