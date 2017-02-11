from django.contrib import admin
from mezzanine.core.admin import (
	TabularDynamicInlineAdmin, DisplayableAdmin)
from mezzanine.pages.admin import PageAdmin


from theme.models import (
	HomePage, Slide, IconBlurb, Portfolio, PortfolioItem, PortfolioItemImage,
	PortfolioItemCategory, Certificate, ArtigoFinal
)

class SlideInline(TabularDynamicInlineAdmin):
	model = Slide

class IconBlurbInline(TabularDynamicInlineAdmin):
	model = IconBlurb

class HomePageAdmin(PageAdmin):
	inlines = (SlideInline, IconBlurbInline)

admin.site.register(HomePage, HomePageAdmin)
admin.site.register(Portfolio, PageAdmin)

class PortfolioItemImageInline(TabularDynamicInlineAdmin):
	model = PortfolioItemImage

class PortfolioItemAdmin(PageAdmin):
	inlines = (PortfolioItemImageInline,)

admin.site.register(PortfolioItem, PortfolioItemAdmin)
admin.site.register(PortfolioItemCategory)


admin.site.register(Certificate)
admin.site.register(ArtigoFinal)
