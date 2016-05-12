from __future__ import unicode_literals

from collections import defaultdict
from django import template
from django.template.defaultfilters import timesince
from django.core.urlresolvers import reverse

from links.utils import order_by_score
from links.views import CommentList, USER_PROFILE_RELATED_NAME

from mezzanine.conf import settings
from mezzanine.utils.importing import import_dotted_path
from mezzanine.generic.models import ThreadedComment


register = template.Library()


@register.filter
def get_profile(user):
    """
    Returns the profile object associated with the given user.
    """
    return getattr(user, USER_PROFILE_RELATED_NAME)


@register.simple_tag(takes_context=True)
def order_comments_by_score_for(context, link):
    """
    Preloads threaded comments in the same way Mezzanine initially does,
    but here we order them by score.
    """
    comments = defaultdict(list)
    qs = link.comments.visible().select_related(
        "user",
        "user__%s" % (USER_PROFILE_RELATED_NAME)
    )
    for comment in order_by_score(qs, CommentList.score_fields, "submit_date"):
        comments[comment.replied_to_id].append(comment)
    context["all_comments"] = comments
    return ""


@register.filter
def short_timesince(date):
    return timesince(date).split(",")[0]


@register.inclusion_tag("generic/includes/drum_comments.html", takes_context=True)
def drum_comments_for(context, obj):
    """
    Provides a generic context variable name for the object that
    comments are being rendered for.
    """
    form_class = import_dotted_path(settings.COMMENT_FORM_CLASS)
    form = form_class(context["request"], obj)
    try:
        context["posted_comment_form"]
    except KeyError:
        context["posted_comment_form"] = form
    context["unposted_comment_form"] = form
    context["comment_url"] = reverse("comment")
    context["object_for_comments"] = obj
    return context


@register.inclusion_tag("generic/includes/drum_comment.html", takes_context=True)
def drum_comment_thread(context, parent):
    """
    Return a list of child comments for the given parent, storing all
    comments in a dict in the context when first called, using parents
    as keys for retrieval on subsequent recursive calls from the
    comments template.
    """
    if "all_comments" not in context:
        comments = defaultdict(list)
        if "request" in context and context["request"].user.is_staff:
            comments_queryset = parent.comments.all()
        else:
            comments_queryset = parent.comments.visible()
        for comment in comments_queryset.select_related("user"):
            comments[comment.replied_to_id].append(comment)
        context["all_comments"] = comments
    parent_id = parent.id if isinstance(parent, ThreadedComment) else None
    try:
        replied_to = int(context["request"].POST["replied_to"])
    except KeyError:
        replied_to = 0
    context.update({
        "comments_for_thread": context["all_comments"].get(parent_id, []),
        "no_comments": parent_id is None and not context["all_comments"],
        "replied_to": replied_to,
    })
    return context