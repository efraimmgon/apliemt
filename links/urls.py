from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from mezzanine.conf import settings

from links.views import (LinkList, LinkCreate, LinkDetail, CommentList, TagList,
						profile, profile_redirect)

from links import views

PROFILE_URL = getattr(settings, "PROFILE_URL", "/users/")
_slash = "/" if settings.APPEND_SLASH else ""

urlpatterns = patterns("",
    url("^$",
        LinkList.as_view(),
        name="home"),
    url("^newest/$",
        LinkList.as_view(), {"by_score": False},
        name="link_list_latest"),
    url("^comments/$",
        CommentList.as_view(), {"by_score": False},
        name="comment_list_latest"),
    url("^best/$",
        CommentList.as_view(),
        name="comment_list_best"),
    url("^link/create/$",
        login_required(LinkCreate.as_view()),
        name="link_create"),
    url("^link/(?P<slug>.*)/$",
        LinkDetail.as_view(),
        name="link_detail"),
    url("^users/(?P<username>.*)/links/$",
        LinkList.as_view(), {"by_score": False},
        name="link_list_user"),
    url("^users/(?P<username>.*)/comments/$",
        CommentList.as_view(), {"by_score": False},
        name="comment_list_user"),
    url("^tags/$",
        TagList.as_view(),
        name="tag_list"),
    url("^tags/(?P<tag>.*)/$",
        LinkList.as_view(),
        name="link_list_tag"),)


### Overriding the original at mezzanine.accounts


if settings.ACCOUNTS_PROFILE_VIEWS_ENABLED:
    override = [
        url("^%s%s$" % (PROFILE_URL.strip("/"), _slash),
            profile_redirect, name="profile_redirect"),
		# certificate
        url("^%s/(?P<username>.*)/certificados/$" % PROFILE_URL.strip("/"),
            views.certificates, name="certificates"),
		# download certificate
        url("^%s/(?P<username>.*)/certificado/(?P<field_id>\d+)$" % (
            PROFILE_URL.strip("/")),  views.download_certificate,
            name="_download_certificate"),
		# artigo final
        url("^%s/(?P<username>.*)/artigos-finais/$" % PROFILE_URL.strip("/"),
            views.artigo_final, name="artigos-finais"),
		# download artigo finai
        url("^%s/(?P<username>.*)/artigos-finais/(?P<field_id>\d+)$" % (
            PROFILE_URL.strip("/")),  views.download_artigo_final,
            name="_download-artigo-final"),

		# profile
        url("^%s/(?P<username>.*)%s$" % (PROFILE_URL.strip("/"), _slash),
            profile, name="profile"),
    ]
    urlpatterns += override
