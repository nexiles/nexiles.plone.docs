import re
from plone import api
from plone.jsonapi.core import router
from AccessControl import Unauthorized, getSecurityManager
from plone.docs.interfaces import ISerializable

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

@router.add_route("/plone/api/1.0/auth", "auth", methods=["GET"])
def authorize(context, request):
    """ check authorization
    """
    uri = request.get_header("X-Original-URI")
    doc_root  = request.get_header("NEXILES_DOC_ROOT", "/docs/")

    if not uri.startswith(doc_root):
        # fake address
        request.response.setStatus(404)
        return {}

    catalog = api.portal.get_tool(name="portal_catalog")
    brains = catalog(portal_type="plone.docs.docmeta")
    if not brains:
        # no documentation visible for the current user
        request.response.setStatus(401)
        return {}

    host_name = request.get_header("NEXILES_DOC_HOST", "http://localhost:8888")
    url = host_name + uri
    doc = None
    for brain in brains:
        obj = brain.getObject()
        json = ISerializable(obj).toJson(request)
        if url.startswith(re.sub("\/index.html", "", json["doc_url"])) or url.startswith(re.sub(".zip", "", json["zip"])):
            doc = obj
            break

    if not doc or not getSecurityManager().checkPermission("View", doc):
        # no view permission
        request.response.setStatus(401)

    return {}

# vim: set ft=python ts=4 sw=4 expandtab :
