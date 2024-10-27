from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Product, Category, Comment

class ProductAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'price', 'stock', 'image', 'category')
    list_display = ('name', 'price', 'stock', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Comment)
# admin.site.register(User, UserAdmin)