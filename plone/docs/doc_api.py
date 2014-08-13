# -*- coding: utf-8 -*-

import os

from plone.jsonapi.core import router

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone import api


# see https://github.com/nexiles/nexiles.plone.docs/issues/2
def fix_missing_uids(items):
    for item in items:
        if "uid" not in item:
            item["uid"] = os.path.basename(item["api_url"])
    return items


@router.add_route("/plone/api/1.0/login", "login", methods=["GET"])
def checkLogin(context, request):
    """ check for login
    """
    member = api.user.get_current()
    return {
        "logged_in": not api.user.is_anonymous(),
        "email": member.getProperty("email"),
        "name": member.getProperty("fullname"),
    }


# GET DOCS
@router.add_route("/docs/api/1.0", "docs", methods=["GET"])
@router.add_route("/docs/api/1.0/<string:uid>", "docs", methods=["GET"])
def get(context, request, uid=None):
    """ get docs
    """
    items = get_items("plone.docs.docmeta", request, uid=uid, endpoint="docs")

    return {
        "count": len(items),
        "items": rewrite(items, request),
    }

# CREATE
@router.add_route("/docs/api/1.0/create", "docs_create", methods=["POST"])
@router.add_route("/docs/api/1.0/create/<string:uid>", "docs_create", methods=["POST"])
def create(context, request, uid=None):
    """ create docs
    """
    items = create_items("plone.docs.docmeta", request, uid=uid, endpoint="docs")
    items = fix_missing_uids(items)

    return {
        "count": len(items),
        "items": rewrite(items, request)
    }


# UPDATE
@router.add_route("/docs/api/1.0/update", "docs_update", methods=["POST"])
@router.add_route("/docs/api/1.0/update/<string:uid>", "docs_update", methods=["POST"])
def update(context, request, uid=None):
    """ update docs
    """
    items = update_items("plone.docs.docmeta", request, uid=uid, endpoint="docs")
    items = fix_missing_uids(items)

    return {
        "count": len(items),
        "items": rewrite(items, request)
    }


# DELETE
@router.add_route("/docs/api/1.0/delete", "docs_delete", methods=["POST"])
@router.add_route("/docs/api/1.0/delete/<string:uid>", "docs_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete docs
    """
    result = delete_items("plone.docs.docmeta", request, uid=uid, endpoint="docs")

    return {
        "result": result
    }

def rewrite(items, request):
    """ map all items to the refetched items
    """
    return map(lambda item: refetch(item["uid"], request), items)

def refetch(uid, request):
    """ generate a new item with all necessary attributes
    """
    item = api.content.get(UID=uid)
    return item.toJson(request)

# vim: set ft=python ts=4 sw=4 expandtab :