from __future__ import unicode_literals
from future.builtins import super

import os
from datetime import timedelta
from mimetypes import guess_type
from functools import reduce

from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.messages import info, error

from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.http import HttpResponse

from mezzanine.accounts import get_profile_model
from mezzanine.conf import settings
from mezzanine.generic.models import ThreadedComment, Keyword
from mezzanine.utils.views import paginate
from mezzanine.pages.models import RichTextPage

from links.forms import LinkForm
from links.models import Link
from links.utils import order_by_score

from theme.models import Portfolio, PortfolioItem, Certificate, ArtigoFinal


fs = FileSystemStorage(location=settings.FORMS_UPLOAD_ROOT)


# Returns the name to be used for reverse profile lookups from the user
# object. That's "profile" for the ``links.Profile``, but otherwise
# depends on the model specified in ``AUTH_PROFILE_MODULE``.
USER_PROFILE_RELATED_NAME = get_profile_model().user.field.related_query_name()


class UserFilterView(ListView):
    """
    List view that puts a ``profile_user`` variable into the context,
    which is optionally retrieved by a ``username`` urlpattern var.
    If a user is loaded, ``object_list`` is filtered by the loaded
    user. Used for showing lists of links and comments.
    """

    def get_context_data(self, **kwargs):
        context = super(UserFilterView, self).get_context_data(**kwargs)
        try:
            username = self.kwargs["username"]
        except KeyError:
            profile_user = None
        else:
            users = User.objects.select_related(USER_PROFILE_RELATED_NAME)
            lookup = {"username__iexact": username, "is_active": True}
            profile_user = get_object_or_404(users, **lookup)
            qs = context["object_list"].filter(user=profile_user)
            context["object_list"] = qs
            # Update context_object_name variable
            context_object_name = self.get_context_object_name(context["object_list"])
            context[context_object_name] = context["object_list"]

        context["profile_user"] = profile_user
        context["no_data"] = ("Whoa, there's like, literally no data here, "
                              "like seriously, I totally got nothin.")
        return context


class ScoreOrderingView(UserFilterView):
    """
    List view that optionally orders ``object_list`` by calculated
    score. Subclasses must defined a ``date_field`` attribute for the
    related model, that's used to determine time-scaled scoring.
    Ordering by score is the default behaviour, but can be
    overridden by passing ``False`` to the ``by_score`` arg in
    urlpatterns, in which case ``object_list`` is sorted by most
    recent, using the ``date_field`` attribute. Used for showing lists
    of links and comments.
    """

    def get_context_data(self, **kwargs):
        context = super(ScoreOrderingView, self).get_context_data(**kwargs)
        qs = context["object_list"]
        context["by_score"] = self.kwargs.get("by_score", True)
        if context["by_score"]:
            qs = order_by_score(qs, self.score_fields, self.date_field)
        else:
            qs = qs.order_by("-" + self.date_field)
        context["object_list"] = paginate(qs, self.request.GET.get("page", 1),
            settings.ITEMS_PER_PAGE, settings.MAX_PAGING_LINKS)
        # Update context_object_name variable
        context_object_name = self.get_context_object_name(context["object_list"])
        context[context_object_name] = context["object_list"]
        context["title"] = self.get_title(context)
        return context


class LinkView(object):
    """
    List and detail view mixin for links - just defines the correct
    queryset.
    """
    def get_queryset(self):
        return Link.objects.published().select_related(
            "user",
            "user__%s" % USER_PROFILE_RELATED_NAME
        )


class LinkList(LinkView, ScoreOrderingView):
    """
    List view for links, which can be for all users (homepage) or
    a single user (links from user's profile page). Links can be
    order by score (homepage, profile links) or by most recently
    created ("newest" main nav item).
    """

    date_field = "publish_date"
    score_fields = ["rating_sum", "comments_count"]

    def get_queryset(self):
        queryset = super(LinkList, self).get_queryset()
        tag = self.kwargs.get("tag")
        if tag:
            queryset = queryset.filter(keywords__keyword__slug=tag)
        return queryset.prefetch_related("keywords__keyword")

    def get_title(self, context):
        tag = self.kwargs.get("tag")
        if tag:
            return get_object_or_404(Keyword, slug=tag).title
        if context["by_score"]:
            return ""  # Homepage
        if context["profile_user"]:
            return "Links by %s" % getattr(
                context["profile_user"],
                USER_PROFILE_RELATED_NAME
            )
        else:
            return "Newest"


class LinkCreate(CreateView):
    """
    Link creation view - assigns the user to the new link, as well
    as setting Mezzanine's ``gen_description`` attribute to ``False``,
    so that we can provide our own descriptions.
    """

    form_class = LinkForm
    model = Link

    def form_valid(self, form):
        hours = getattr(settings, "ALLOWED_DUPLICATE_LINK_HOURS", None)
        if hours and form.instance.link:
            lookup = {
                "link": form.instance.link,
                "publish_date__gt": now() - timedelta(hours=hours),
            }
            try:
                link = Link.objects.get(**lookup)
            except Link.DoesNotExist:
                pass
            else:
                error(self.request, "Link exists")
                return redirect(link)
        form.instance.user = self.request.user
        form.instance.gen_description = False
        info(self.request, "Link created")
        return super(LinkCreate, self).form_valid(form)


class LinkDetail(LinkView, DetailView):
    """
    Link detail view - threaded comments and rating are implemented
    in its template.
    """
    pass


class CommentList(ScoreOrderingView):
    """
    List view for comments, which can be for all users ("comments" and
    "best" main nav items) or a single user (comments from user's
    profile page). Comments can be order by score ("best" main nav item)
    or by most recently created ("comments" main nav item, profile
    comments).
    """

    date_field = "submit_date"
    score_fields = ["rating_sum"]

    def get_queryset(self):
        qs = ThreadedComment.objects.filter(is_removed=False, is_public=True)
        select = ["user", "user__%s" % (USER_PROFILE_RELATED_NAME)]
        prefetch = ["content_object"]
        return qs.select_related(*select).prefetch_related(*prefetch)

    def get_title(self, context):
        if context["profile_user"]:
            return "Comments by %s" % getattr(
                context["profile_user"],
                USER_PROFILE_RELATED_NAME
            )
        elif context["by_score"]:
            return "Best comments"
        else:
            return "Latest comments"


class TagList(TemplateView):
    template_name = "links/tag_list.html"


#################################################
# Overriding the original at mezzanine.accounts #
#################################################


@login_required
def profile_redirect(request):
    """
    Just gives the URL prefix for profiles an action - redirect
    to the logged in user's profile.
    """
    return redirect("profile", username=request.user.username)


def profile(request, username, template="accounts/account_profile.html",
            extra_context=None):
    """
    Display a profile.
    """
    lookup = {"username__iexact": username, "is_active": True}
    context = {"profile_user": get_object_or_404(User, **lookup)}
    context.update(extra_context or {})

    context.update(
        {"informativos": get_specific_portfolio_item(request, "Informativos"),
         "cronograma": get_specific_portfolio_item(request, "Cronograma"),
         "XIX_EPI": RichTextPage.objects.get(title_pt_br__icontains="XIX EPI")}
    )
    return TemplateResponse(request, template, context)

# ------------------------------------------------------
# certificados
# ------------------------------------------------------

def certificates(request, username):
    lookup = {"username__iexact": username, "is_active": True}
    certificates = Certificate.objects.filter(owner=request.user)
    context = {
        "profile_user": get_object_or_404(User, **lookup),
        "certificates": reduce(acc_certificates, certificates, []),
        "XIX_EPI": RichTextPage.objects.get(title_pt_br__icontains="XIX EPI")
    }
    return render(request, "certificates.html", context)

def download_certificate(request, username, field_id):
    obj = get_object_or_404(Certificate, id=field_id)
    ## the obj does not return a full path
    #path = os.path.join(fs.location, obj.certificate)
    if settings.DEBUG:
        path = "".join([fs.location, "/static/media/", str(obj.certificate)])
    else:
        path = "".join([fs.location,
            "/Sites/apliemt/static/media/", str(obj.certificate)])
    response = HttpResponse(content_type=guess_type(path)[0])
    with open(path, "r+b") as f:
        response["Content-Disposition"] = "attachment; filename=%s" % f.name
        response.write(f.read())
    return response

def testing(request):
    return HttpResponse("Ok")

# ------------------------------------------------------
# artigo final
# ------------------------------------------------------

def acc_artigos(acc, i):
    return acc + [{"id": i.id, "name": os.path.basename(str(i.doc))}]

def artigo_final(request, username):
    lookup = {"username__iexact": username, "is_active": True}
    artigos = ArtigoFinal.objects.filter(owner=request.user)
    context = {
        "profile_user": get_object_or_404(User, **lookup),
        "artigos": reduce(acc_artigos, artigos, []),
        "XIX_EPI": RichTextPage.objects.get(title_pt_br__icontains="XIX EPI")
    }
    return render(request, "artigo_final.html", context)

def download_artigo_final(request, username, field_id):
    obj = get_object_or_404(Certificate, id=field_id)
    ## the obj does not return a full path
    #path = os.path.join(fs.location, obj.certificate)
    if settings.DEBUG:
        path = "".join([fs.location, "/static/media/", str(obj.doc)])
    else:
        path = "".join([fs.location,
            "/Sites/apliemt/static/media/", str(obj.doc)])
    response = HttpResponse(content_type=guess_type(path)[0])
    with open(path, "r+b") as f:
        response["Content-Disposition"] = "attachment; filename=%s" % f.name
        response.write(f.read())
    return response

# ------------------------------------------------------
# Helper functions
# ------------------------------------------------------

def acc_certificates(acc, c):
    return acc + [{"id": c.id, "name": os.path.basename(str(c.certificate))}]

def get_specific_portfolio_item(request, specific):
    try:
        p = Portfolio.objects.get(title_pt_br=specific)
        item = PortfolioItem.objects.published(
            for_user=request.user).filter(parent=p)
    except Portfolio.DoesNotExist:
        item = None
    return item
