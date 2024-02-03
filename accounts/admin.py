from django.contrib import admin
from .models import *

from django_jalali.admin.filters import JDateFieldListFilter
from menu.models import itemImageShip, Menu

# you need import this for adding jalali calander widget
import django_jalali.admin as jadmin

# Register your models here.
#TODO add banner model



class imageComplexFilter(admin.SimpleListFilter):
    title = 'Complex'
    parameter_name = 'Complex'
    
    def lookups(self, request, model_admin):
        listComplex = list()
        complexQuery = complex.objects.all()
        for eachComplex in complexQuery:
            listComplex.append (tuple((eachComplex.name, eachComplex.name)))
        return listComplex

    @staticmethod
    def getIdList(value):
        try:
            idList = list()
            complexQuery = complex.objects.get(name = value)
            ids = complexQuery.complexImage.all().values('id')
            for id in ids:
                idList.append(id.get('id'))
            ids = complexQuery.banner.all().values('id')
            for id in ids:
                idList.append(id.get('id'))
            menuQuery = Menu.objects.filter(complex=complexQuery)
            for eachMenu in menuQuery:
                items = eachMenu.items.all()
                for item in items:
                    ids = itemImageShip.objects.filter(item=item).values('id')
                    for id in ids:
                        idList.append(id.get('id'))
            return idList
        except:
            return idList

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            idList = imageComplexFilter.getIdList(value)
            return queryset.filter(id__in=idList)
        return queryset

class complexAdmin(admin.ModelAdmin):
    list_display= [
        "id", 
        "name",
        "owner",
        "phoneNumber",
        ]
    fields = [
        "id",
        "owner",
        "name",
        "created_at",
        "update_at",
        # "bankName",
        # "shabaNumber",
        "state",
        "city",
        "neighborhood",
        "address",
        "telephone",
        "logo",
        "logo_tumbnail",
        "color",
        "phoneNumber",
        "Slogan",
        "socialMedia",
        "emergencyCall",
        "location",
        "membership_type",
        "workTime",
        "rate",
        "bio",
        "website",
        "taxType",
        "qrCode",
        "customer_ordering",
        "dark_mode"
    ]
    readonly_fields = [
        "id",
        "created_at",
        "update_at",
    ]
    search_fields = [
        'id',
        'name',
        'phoneNumber',
        "owner",
        'state',
        'city'
    ]
    list_filter = [
        "state",
        "city",
        "taxType",
        ('created_at',JDateFieldListFilter),
        ('update_at',JDateFieldListFilter)
    ]
    list_per_page = 10

class bannerShipAdmin(admin.ModelAdmin):
    list_display= [
        "id",
        "get_complex",
    ]
    fields = [
        "id",
        "created_at",
        "foodcomplex",
        "banner",
        # "get_first_name",
        # "get_last_name",
    ]
    readonly_fields = [
        "id",
        "created_at",
    ]
    list_filter = [
        "foodcomplex",
        ("created_at",JDateFieldListFilter)
    ]
    search_fields=[
        "foodcomplex",
        "created_at",  
    ]
    list_per_page = 10
    def get_complex(self, obj):
        return obj.foodcomplex.name
    get_complex.short_description = "complex"

class imageAdmin(admin.ModelAdmin):
    list_display= [
        "id",
        "title",
        "is_item",
        "is_banner",
        "is_complexImage",
        "get_complex",
        "get_item",
        "get_menu",
    ]
    fields = [
        "id",
        "created_at",
        "title",
        "pic",
        "pic_tumbnail",
    ]
    readonly_fields = [
        "id",
        "created_at",
    ]
    list_filter = [
        imageComplexFilter,
        ("created_at",JDateFieldListFilter)
    ]
    list_per_page = 10

    def is_item(self, obj):
        itemImageShipQuery = itemImageShip.objects.all()
        menuQuery = Menu.objects.all()
        for eachShip in itemImageShipQuery:
            if eachShip.image == obj:
                item = eachShip.item 
                for eachMenu in menuQuery:
                    itemAllQuery = eachMenu.items.all()
                    if itemAllQuery.filter(id=item.id).exists:
                        return True
        return False
    is_item.boolean = True
    is_item.short_description = "item?"

    def is_banner(self, obj):
        complexQuery = complex.objects.all()
        for eachComplex in complexQuery:
            imageQuery = eachComplex.banner.all()
            comp = imageQuery.filter(id=obj.id)
            if comp.exists():
                return True
        return False

    is_banner.boolean = True
    is_banner.short_description = "banner?"
    
    def is_complexImage(self, obj):
        complexQuery = complex.objects.all()
        for eachComplex in complexQuery:
            imageQuery = eachComplex.complexImage.all()
            comp = imageQuery.filter(id=obj.id)
            if comp.exists():
                return True
        return False

    is_complexImage.boolean = True
    is_complexImage.short_description = "complex?"

    def get_complex(self, obj):
        complexQuery = complex.objects.all()
        for eachComplex in complexQuery:
            imageQuery = eachComplex.complexImage.all() | eachComplex.banner.all()
            comp = imageQuery.filter(id=obj.id)
            if comp.exists():
                return eachComplex.name
        itemImageShipQuery = itemImageShip.objects.all()
        menuQuery = Menu.objects.all()
        for eachShip in itemImageShipQuery:
            if eachShip.image == obj:
                item = eachShip.item 
                for eachMenu in menuQuery:
                    itemAllQuery = eachMenu.items.all()
                    if itemAllQuery.filter(id=item.id).exists:
                        return eachMenu.complex.name
    get_complex.short_description = "Complex"

    def get_item(self, obj):
        itemImageShipQuery = itemImageShip.objects.all()
        for eachShip in itemImageShipQuery:
            if eachShip.image == obj:
                item = eachShip.item 
                return item.name
        return "-"
    get_item.short_description = 'Item'

    def get_menu(self, obj):
        itemImageShipQuery = itemImageShip.objects.all()
        menuQuery = Menu.objects.all()
        for eachShip in itemImageShipQuery:
            if eachShip.image == obj:
                item = eachShip.item 
                for eachMenu in menuQuery:
                    itemAllQuery = eachMenu.items.all()
                    if itemAllQuery.filter(id=item.id).exists:
                        return eachMenu.name
    get_menu.short_description = "Menu"

class imageShipAdmin(admin.ModelAdmin):
    list_display=[
        "id",
        "get_complex",
    ]
    fields = [
        "id",
        "created_at",
        "foodcomplex",
        "image",
        # "get_first_name",
        # "get_last_name",
    ]
    readonly_fields = [
        "id",
        "created_at",
    ]
    list_filter = [
        "foodcomplex",
        ("created_at",JDateFieldListFilter)
    ]
    search_fields = [
        "foodcomplex",
        "created_at",
    ]
    list_per_page = 10

    def get_complex(self, obj):
        return obj.foodcomplex.name
    get_complex.short_description = "complex"

class customerAdmin(admin.ModelAdmin):
    list_display=[
        "id",
        "phoneNumber",
        "get_first_name",
        "get_last_name",
    ]
    fields = [
        "id",
        "created_at",
        "update_at",
        "user",
        "phoneNumber",
        "birthDate",
        "address",
        "acceptedRules",

    ]
    readonly_fields = [
        "id",
        "created_at",
        "update_at",
    ]
    list_filter = [
        ('birthDate', JDateFieldListFilter),
        ("created_at",JDateFieldListFilter),
        ("update_at",JDateFieldListFilter)
    ]
    search_fields = [
        "phoneNumber",
        'user',
        "created_at",
        "update_at",
    ]
    list_per_page = 10

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'FirstName'
    get_first_name.admin_order_field = 'user__id'
    
    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'lastName'
    get_last_name.admin_order_field = 'user__id'

class workerAdmin(admin.ModelAdmin):
    fields = [
        "id",
        "complex",
        "user",
        "created_at",
        "update_at",
        "phoneNumber",
        "roleName",
        "permission",
    ]
    list_display = [
        "id",
        "user",
        "complex",
        "roleName",

    ]
    readonly_fields = [
        "id",
        "created_at",
        "update_at"
    ]
    list_filter = [
        "complex",
        "permission",
        ("created_at",JDateFieldListFilter),
        ("update_at",JDateFieldListFilter),
    ]
    search_fields = [
        "complex",
        "user",
        "phoneNumber",
        "roleName",
    ]
    list_per_page = 10


class SystemLogAdmin(admin.ModelAdmin):
    fields = [
        "id",
        "complex",
        "worker",
        "model",
        "action",
        "level",
        "message",
        "created_at",
    ]
    list_display = [
        "complex",
        "worker",
        "action",
        "level",
        "model",
        "message",
        "created_at",

    ]
    readonly_fields = [
        "id",
        "complex",
        "worker",
        "action",
        "level",
        "message",
        "created_at",
        "model",
    ]
    list_filter = [
        "complex",
        "action",
        "level",
        ("created_at",JDateFieldListFilter),
    ]
    search_fields = [
        "complex",
        "worker",
        "action",
        "level",
        "message",
        "model",
    ]
    list_per_page = 10


admin.site.register(complex, complexAdmin)
admin.site.register(bannerShip, bannerShipAdmin)
admin.site.register(image, imageAdmin)
admin.site.register(imageShip, imageShipAdmin)
admin.site.register(customer, customerAdmin)
admin.site.register(worker, workerAdmin)
admin.site.register(SystemLog, SystemLogAdmin)