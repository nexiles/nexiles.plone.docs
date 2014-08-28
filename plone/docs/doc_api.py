# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

# GET DOCS
@router.add_route("/docs/api/1.0/docmetas", "docs", methods=["GET"])
@router.add_route("/docs/api/1.0/docmetas/<string:uid>", "docs", methods=["GET"])
def get(context, request, uid=None):
    """ get docs
    """
    items = get_items("plone.docs.docmeta", request, uid=uid, endpoint="docs")

    return {
        "count": len(items),
        "items": items
    }

# CREATE
@router.add_route("/docs/api/1.0/docmetas/create", "docs_create", methods=["POST"])
@router.add_route("/docs/api/1.0/docmetas/create/<string:uid>", "docs_create", methods=["POST"])
def create(context, request, uid=None):
    """ create docs
    """
    items = create_items("plone.docs.docmeta", request, uid=uid, endpoint="docs")

    return {
        "count": len(items),
        "items": items
    }


# UPDATE
@router.add_route("/docs/api/1.0/docmetas/update", "docs_update", methods=["POST"])
@router.add_route("/docs/api/1.0/docmetas/update/<string:uid>", "docs_update", methods=["POST"])
def update(context, request, uid=None):
    """ update docs
    """
    items = update_items("plone.docs.docmeta", request, uid=uid, endpoint="docs")

    return {
        "count": len(items),
        "items": items
    }


# DELETE
@router.add_route("/docs/api/1.0/docmetas/delete", "docs_delete", methods=["POST"])
@router.add_route("/docs/api/1.0/docmetas/delete/<string:uid>", "docs_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete docs
    """
    result = delete_items("plone.docs.docmeta", request, uid=uid, endpoint="docs")

    return {
        "result": result
    }

# vim: set ft=python ts=4 sw=4 expandtab :
