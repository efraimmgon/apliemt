from modeltranslation.translator import translator, TranslationOptions
from .models import (
	HomePage, IconBlurb, Portfolio, PortfolioItem, PortfolioItemImage
)

class TranslatedHomePage(TranslationOptions):
	fields = ("heading", "subheading", "featured_works_heading", 
		"content_heading", "content_content", "latest_posts_heading",)

class TranslatedIconBlurb(TranslationOptions):
	fields = ("title", "content",)

class TranslatedPortfolio(TranslationOptions):
	fields = ("content",)

class TranslatedPortfolioItem(TranslationOptions):
	fields = ("short_description",)

class TranslatedPortfolioItemImage(TranslationOptions):
	fields = ()

translator.register(HomePage, TranslatedHomePage)
translator.register(IconBlurb, TranslatedIconBlurb)
translator.register(Portfolio, TranslatedPortfolio)
translator.register(PortfolioItem, TranslatedPortfolioItem)
translator.register(PortfolioItemImage, TranslatedPortfolioItemImage)