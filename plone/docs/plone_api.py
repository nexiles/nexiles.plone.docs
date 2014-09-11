import re
from plone import api
from plone.jsonapi.core import router

@router.add_route("/plone/api/1.0/login", "login", methods=["GET"])
def checkLogin(context, request):
    """ check for login
    """
    member = api.user.get_current()
    loggedin = not api.user.is_anonymous()

    # set cookie for basic auth requests
    if loggedin and not request.cookies.get("__ac"):
        context.acl_users.session._setupSession(member.getUserName(), request.response)

    return {
        "logged_in": loggedin,
        "username": member.getUserName(),
        "email": member.getProperty("email"),
        "name": member.getProperty("fullname")
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

    uri = re.sub(doc_root, "", uri)
    catalog = api.portal.get_tool(name="portal_catalog")
    if catalog(portal_type="plone.docs.docmeta", doc_url=uri) or catalog(portal_type="plone.docs.docmeta", zip=uri) or catalog(portal_type="plone.docs.docmeta", doc_icon=uri):
        # 200 OK
        return {}

    brains = catalog(portal_type="plone.docs.docmeta")
    for brain in brains:
        if uri.startswith(re.sub("\/index.html", "", brain["doc_url"])):
            # 200 OK
            return {}

    # no view permission
    request.response.setStatus(401)
    return {}

# vim: set ft=python ts=4 sw=4 expandtab :
