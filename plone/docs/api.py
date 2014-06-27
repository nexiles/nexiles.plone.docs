# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

from plone.jsonapi.routes.api import url_for

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone import api

PREFIX = "http://192.168.100.137/docs/"


@router.add_route("/docs/api/1.0/login", "login", methods=["GET"])
def check(context, request):
    """ check for login
    """

    if api.user.is_anonymous():
        return {
          "logged_in": False
        }

    member = api.user.get_current()
    return {
      "logged_in": True,
      "email": member.getProperty("email"),
      "name": member.getProperty("fullname"),
    }


# GET DOCS
@router.add_route("/docs/api/1.0", "docs", methods=["GET"])
@router.add_route("/docs/api/1.0/<string:uid>", "docs", methods=["GET"])
def getPublic(context, request, uid=None):
    """ get docs
    """

    items = get_items("docmeta", request, uid=uid, endpoint="docs")

    # res = filter(arr, func)
    return {
        "url": url_for("docs"),
        "count": len(items),
        "items": filter(items, request),
    }

# CREATE
@router.add_route("/docs/api/1.0/create", "docs_create", methods=["POST"])
@router.add_route("/docs/api/1.0/create/<string:uid>", "docs_create", methods=["POST"])
def create(context, request, uid=None):
    """ create docs
    """
    items = create_items("docmeta", request, uid=uid, endpoint="docs")
    return {
        "url": url_for("docs_create"),
        "count": len(items),
        "items": filter(items, request)
    }


# UPDATE
@router.add_route("/docs/api/1.0/update", "docs_update", methods=["POST"])
@router.add_route("/docs/api/1.0/update/<string:uid>", "docs_update", methods=["POST"])
def update(context, request, uid=None):
    """ update docs
    """
    items = update_items("docmeta", request, uid=uid, endpoint="docs")
    return {
        "url": url_for("docs_update"),
        "count": len(items),
        "items": filter(items, request)
    }


# DELETE
@router.add_route("/docs/api/1.0/delete", "docs_delete", methods=["POST"])
@router.add_route("/docs/api/1.0/delete/<string:uid>", "docs_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete docs
    """
    items = delete_items("docmeta", request, uid=uid, endpoint="docs")
    return {
        "url": url_for("docs_delete"),
        "count": len(items),
        "items": filter(items, request)
    }


## maybe better use map?
#
# return {
#    "url": url_for("docs_delete"),
#    "count": len(items),
#    "items": map(items, lambda item: filter(PREFIX, item, request))
#}


def filter(prefix, items, request):
  result = list()

  for item in items:
    item = get_items("docmeta", request, uid=item["uid"], endpoint="docs")[0]
    state = item["workflow_info"]["status"]
    if state == "Externally visible" or state == "Internally published":
      state = "released"
    else:
      state = None

    out = {
      "name": item["title"],
      "state": state,
      "version": item["version"]
      "url": item["url"] or ...
    }

    if item["url"]:
      out["url"] = item["url"]
    else:
      out["url"] = PREFIX + out["name"] + "/v" + out["version"] + "/"

    if item["zip"]:
      out["zip"] = PREFIX + item["zip"]
    else:
      out["zip"] = PREFIX + out["name"] + "/v" + out["version"] + ".zip"

    if item["icon"]:
      out["icon"] = PREFIX + item["icon"]
    else:
      out["icon"] = item["icon"]

    result.append(out)

  return result

# vim: set ft=python ts=4 sw=4 expandtab :
