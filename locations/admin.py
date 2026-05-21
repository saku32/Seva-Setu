from django.contrib import admin
from .models import District, City, Area


class CityInline(admin.TabularInline):
    model = City
    extra = 1
    show_change_link = True


class AreaInline(admin.TabularInline):
    model = Area
    extra = 1
    show_change_link = True


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_mr', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name_en', 'name_mr', 'code')
    inlines = [CityInline]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_mr', 'district', 'is_active')
    list_filter = ('is_active', 'district')
    search_fields = ('name_en', 'name_mr')
    inlines = [AreaInline]


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_mr', 'city', 'pin_code', 'is_active')
    list_filter = ('is_active', 'city__district')
    search_fields = ('name_en', 'name_mr', 'pin_code')
