# -*- coding: utf-8 -*-

import logging

from plone import api

from Products.CMFCore.utils import getToolByName

logger = logging.getLogger("plone.docs.setuphandlers")


def create(where, what, id, **kw):
    """ helper to create content types
    """
    logger.info(where)
    _ = where.invokeFactory(what, id, **kw)
    return where.get(_)

def setupVarious(context):
    """ import steps
    """

    if context.readDataFile('plone.docs.marker.txt') is None:
        # Not plone.docs add-on
        return

    portal = context.getSite()

    # run import steps
    setup_groups(portal)
    setup_demo_users(portal)
    setup_doc_folder(portal)
    setup_docs(portal)

PROJECTS = [

    # id, **kwargs
    ("nexiles-documentation-project", {"title": "nexiles-documentation-project", "github": "https://github.com/nexiles/nexiles-documentation-project"})

]

DOCS = [

    # id, **kwargs
    ("nexiles-documentation-project", {"version": "0.1", "icon": None, "title": "nexiles-documentation-project"})

]

GROUPS = [
    # groupname, title, description, roles, groups
    ("doc_admins", "Documentation Admins", "", [], []),
    ("user_admins", "User Admins", "", ["User Manager"], []),
    ("developers", "Developers", "", [], []),
    ("consultants", "Consultants", "", [], []),
    ("external_users", "External Users", "", [], []),
    ("internal_users", "Internal Users", "", ["Member"], ["doc_admins", "user_admins", "developers", "consultants"])
]

DEMO_USERS = [

    # Add some users
    # email, username, password, roles, properties, groups
    ("dev@example.com", "developer", "secret", (), {"fullname": "Developer"}, ("developers",)),
    ("consultant@example.com", "consultant", "secret", (), {"fullname": "Consultant"}, ("consultants",)),
    ("doc_admin@example.com", "doc_admin", "secret", (), {"fullname": "Doc-Admin"}, ("doc_admins", "user_admins")),
    ("info@siemens.com", "siemens", "secret", (), {"fullname": "Siemens"}, ("external_users",))

]

def setup_groups(portal):
    """ setup required groups
    """

    for group in GROUPS:
        groupname, title, description, roles, groups = group

        if api.group.get(groupname):
            logger.info("*** Group '%s' already exists [SKIP]" % groupname)
            continue

        logger.info("*** Creating Group '%s' ..." % groupname)
        group = api.group.create(groupname, title, description, roles, groups)
        logger.info("*** Creating Group '%s' [DONE]" % groupname)


def setup_demo_users(portal):
    """ Add some demo users to the groups
    """

    # email or username as login?
    portal_props = getToolByName(portal, 'portal_properties')
    props = portal_props.site_properties
    use_email_as_login = props.getProperty('use_email_as_login')

    for user in DEMO_USERS:
        email, username, password, roles, properties, groups = user

        login = use_email_as_login and email or username
        if api.user.get(login):
            logger.info("*** User '%s' already exists [SKIP]" % username)
            continue

        logger.info("*** Creating User '%s' ..." % username)
        user = api.user.create(email, username, password, roles, properties)

        # Add user to groups
        for group in groups:
            logger.info("*** Adding User '%s' to Group '%s' ..." % (username, group))
            api.group.add_user(groupname=group, user=user)
            logger.info("*** Adding User '%s' to Group '%s' [DONE]" % (username, group))

        logger.info("*** Creating User '%s' [DONE]" % username)


def setup_doc_folder(portal):
    """ Handler to setup the `Documentation` Folder
    """
    docs = portal.get("documentation", None)
    if not docs:
        logger.info("*** Adding Documentation folder to portal ...")
        _ = portal.invokeFactory("Folder", "documentation", title="Documentation", description="Documentation Folder")
        docs = portal.get(_)

    # only allow Documentation to be added
    docs.setConstrainTypesMode(1)
    docs.setLocallyAllowedTypes(("plone.docs.docmeta", "plone.docs.project"))
    docs.setImmediatelyAddableTypes(("plone.docs.docmeta", "plone.docs.project"))

    # local roles
    docs.manage_setLocalRoles("internal_users", ["Reader"])
    docs.manage_setLocalRoles("developers", ["Contributor"])
    docs.manage_setLocalRoles("doc_admins", ["Contributor", "Editor", "Reviewer"])

    # make public
    if api.content.get_state(obj=docs) == "private":
        api.content.transition(obj=docs, transition='publish')

    # make front-page public
    page = api.content.get(path="/front-page")
    if api.content.get_state(obj=page) == "private":
        api.content.transition(obj=page, transition="publish")


def setup_docs(portal):

    docs = portal.get("documentation", None)

    for project in PROJECTS:
        project_id, kwargs = project

        # Documentation exists already, skipping
        if project_id in docs:
            logger.info("*** Project '%s' already in Documentation Folder [SKIP]" % project_id)
            continue

        logger.info("*** Creating Project '%s' ..." % project_id)
        result = create(docs, "plone.docs.project", project_id, **kwargs)
        result.manage_setLocalRoles("developer", ["Owner"])
        logger.info("*** Creating Project '%s' [DONE]" % project_id)

        for doc in DOCS:
            doc_id, kwargs = doc

            # Documentation exists already, skipping
            if doc_id in result:
                logger.info("*** Documentation '%s' already in Project [SKIP]" % doc_id)
                continue

            logger.info("*** Creating Documentation '%s' ..." % doc_id)
            d = create(result, "plone.docs.docmeta", doc_id, **kwargs)
            d.manage_setLocalRoles("developer", ["Owner"])
            logger.info("*** Creating Documentation '%s' [DONE]" % doc_id)


# vim: set ft=python ts=4 sw=4 expandtab :
