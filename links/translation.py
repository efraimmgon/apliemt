from modeltranslation.translator import translator, TranslationOptions
from .models import (
	Link
)

class TranslatedLink(TranslationOptions):
	fields = ()

#class TranslatedIconBlurb(TranslationOptions):
#	fields = ("title", "content",)

#class TranslatedPortfolio(TranslationOptions):
#	fields = ("content",)

#class TranslatedPortfolioItem(TranslationOptions):
#	fields = ("short_description",)

#class TranslatedPortfolioItemImage(TranslationOptions):
#	fields = ()

translator.register(Link, TranslatedLink)
#translator.register(IconBlurb, TranslatedIconBlurb)
#translator.register(Portfolio, TranslatedPortfolio)
#translator.register(PortfolioItem, TranslatedPortfolioItem)
#translator.register(PortfolioItemImage, TranslatedPortfolioItemImage)