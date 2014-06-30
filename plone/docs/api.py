# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone import api

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

    return {
        "count": len(items),
        "items": rewriteItems(items, request),
    }

# CREATE
@router.add_route("/docs/api/1.0/create", "docs_create", methods=["POST"])
@router.add_route("/docs/api/1.0/create/<string:uid>", "docs_create", methods=["POST"])
def create(context, request, uid=None):
    """ create docs
    """
    items = create_items("docmeta", request, uid=uid, endpoint="docs")

    return {
        "count": len(items),
        "items": rewriteItems(items, request)
    }


# UPDATE
@router.add_route("/docs/api/1.0/update", "docs_update", methods=["POST"])
@router.add_route("/docs/api/1.0/update/<string:uid>", "docs_update", methods=["POST"])
def update(context, request, uid=None):
    """ update docs
    """
    items = update_items("docmeta", request, uid=uid, endpoint="docs")

    return {
        "count": len(items),
        "items": rewriteItems(items, request)
    }


# DELETE
@router.add_route("/docs/api/1.0/delete", "docs_delete", methods=["POST"])
@router.add_route("/docs/api/1.0/delete/<string:uid>", "docs_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete docs
    """
    items = delete_items("docmeta", request, uid=uid, endpoint="docs")

    return {
        "count": len(items),
        "items": rewriteItems(items, request)
    }

def rewriteItems(items, request):
    """ map all items to the refetched items
    """
    host_name = request.get_header("NEXILES_DOC_HOST", "http://localhost:8888")
    doc_root  = request.get_header("NEXILES_DOC_ROOT", "/docs/")
    prefix = host_name + doc_root
    return map(lambda item: refetch(item["uid"], request, prefix), items)

def refetch(id, request, prefix):
    """ generate a new item with all necessary attributes
    """
    item = get_items("docmeta", request, uid=id, endpoint="docs")[0]

    state = item["workflow_info"]["status"]
    if state == "Externally visible" or state == "Internally published":
      state = "released"
    else:
      state = "internal"

    return {
      "name": item["title"],
      "state": state,
      "version": item["version"],
      "url": item["url"] or prefix + item["title"] + "/v" + item["version"] + "/",
      "zip": item["zip"] or prefix + item["title"] + "/v" + item["version"] + ".zip",
      "icon": item["icon"] and prefix + item["icon"]
    }

# vim: set ft=python ts=4 sw=4 expandtab :
