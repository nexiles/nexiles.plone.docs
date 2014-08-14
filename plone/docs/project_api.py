# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.docs.doc_api import rewrite
from plone.docs.doc_api import fix_missing_uids


# GET PROJECTS
@router.add_route("/docs/api/1.0/projects", "projects", methods=["GET"])
@router.add_route("/docs/api/1.0/projects/<string:uid>", "projects", methods=["GET"])
def get(context, request, uid=None):
    """ get projects
    """
    items = get_items("plone.docs.project", request, uid=uid, endpoint="projects")

    return {
        "count": len(items),
        "items": rewrite(items, request)
    }

# CREATE
@router.add_route("/docs/api/1.0/projects/create", "projects_create", methods=["POST"])
@router.add_route("/docs/api/1.0/projects/create/<string:uid>", "projects_create", methods=["POST"])
def create(context, request, uid=None):
    """ create projects
    """
    items = create_items("plone.docs.project", request, uid=uid, endpoint="projects")
    items = fix_missing_uids(items)

    return {
        "count": len(items),
        "items": rewrite(items, request)
    }


# UPDATE
@router.add_route("/docs/api/1.0/projects/update", "projects_update", methods=["POST"])
@router.add_route("/docs/api/1.0/projects/update/<string:uid>", "projects_update", methods=["POST"])
def update(context, request, uid=None):
    """ update projects
    """
    items = update_items("plone.docs.project", request, uid=uid, endpoint="projects")
    items = fix_missing_uids(items)

    return {
        "count": len(items),
        "items": rewrite(items, request)
    }


# DELETE
@router.add_route("/docs/api/1.0/projects/delete", "projects_delete", methods=["POST"])
@router.add_route("/docs/api/1.0/projects/delete/<string:uid>", "projects_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete projects
    """
    result = delete_items("plone.docs.project", request, uid=uid, endpoint="projects")

    return {
        "result": result
    }

# vim: set ft=python ts=4 sw=4 expandtab :
