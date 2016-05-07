from mezzanine.conf import register_setting
from django.utils.translation import ugettext_lazy as _

register_setting(
	name="TEMPLATE_ACCESSIBLE_SETTINGS",
	append=True,
	default=(
		"SOCIAL_LINK_FACEBOOK",
		"SOCIAL_LINK_VIMEO",
		"SOCIAL_LINK_TUMBRL",
		"SOCIAL_LINK_TWITTER",
		"SOCIAL_LINK_DELICIOUS",
	),
)

register_setting(
	name="SOCIAL_LINK_FACEBOOK",
	label=_("Facebook link"),
	description=_("If present a Facebook icon linking here will be in the "
				  "header"),
	editable=True,
	default="#"
)

register_setting(
	name="SOCIAL_LINK_VIMEO",
	label=_("Vimeo link"),
	description=_("If present a Vimeo icon linking here will be in the "
				  "header"),
	editable=True,
	default="#"
)

register_setting(
	name="SOCIAL_LINK_TUMBRL",
	label=_("Tumbrl link"),
	description=_("If present a Tumbrl icon linking here will be in the "
				  "header"),
	editable=True,
	default="#"
)

register_setting(
	name="SOCIAL_LINK_TWITTER",
	label=_("Twitter link"),
	description=_("If present a Twitter icon linking here will be in the "
				  "header"),
	editable=True,
	default="#"
)

register_setting(
	name="SOCIAL_LINK_DELICIOUS",
	label=_("Delicious link"),
	description=_("If present a Delicious icon linking here will be in the "
				  "header"),
	editable=True,
	default="#"
)