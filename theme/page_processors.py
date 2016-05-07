from mezzanine.pages.page_processors import processor_for
from .models import Portfolio, PortfolioItem, PortfolioItemCategory, HomePage

@processor_for(Portfolio)
def portfolio_processor(request, page):
	"""
	Adds a portfolio's portfolio items to the context
	"""
	# get the Portfolio's items, prefetching categories for performance
	items = PortfolioItem.objects.published(
		for_user=request.user).prefetch_related('categories')
	items = items.filter(parent=page)
	# filter out only categories that are user in the Portfolio's items
	categories = PortfolioItemCategory.objects.filter(
		portfolioitems__in=items).distinct()
	return {'items': items, 'categories': categories}

@processor_for(PortfolioItem)
def portfolioitem_processor(request, page):
	"""
	Adds a portfolio's portfolio items to the context
	"""
	portfolioitem = PortfolioItem.objects.published(
		for_user=request.user).prefetch_related(
		'categories', 'images').get(id=page.portfolioitem.id)
	return {'portfolioitem': portfolioitem}

@processor_for(HomePage)
def home_processor(request, page):
	items = PortfolioItem.objects.published(
		for_user=request.user).prefetch_related('categories')
	items = items.filter(parent=page.homepage.featured_portfolio)
	return {'items': items}