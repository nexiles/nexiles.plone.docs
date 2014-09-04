# -*- coding: utf-8 -*-

import logging

from plone import api

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
    setup_catalog_indexes(portal)
    setup_doc_folder(portal)
    setup_docs(portal)

# The profile id of your package
PROFILE_ID = 'profile-plone.docs:default'

PROJECTS = [

    # id, **kwargs
    ("nexiles-documentation-project", {"title": "nexiles-documentation-project", "github": "https://github.com/nexiles/nexiles-documentation-project"})

]

DOCS = [

    # id, **kwargs
    ("nexiles-documentation-project", {"version": "0.2", "icon": None, "title": "nexiles-documentation-project"})

]

GROUPS = [
    # groupname, title, description, roles, groups
    ("external_users", "External Users", "", [], []),
    ("internal_users", "Internal Users", "", ["Member"], ["Documentation Admins", "Developers", "Consultants"])
]

INDEXES = [
    # name, type
    ("doc_url", "FieldIndex"),
    ("zip", "FieldIndex"),
    ("doc_icon", "FieldIndex"),
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


def setup_catalog_indexes(portal):
    """ Method to add indexes to the portal_catalog.
    """

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = api.portal.get_tool(name='portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = api.portal.get_tool(name='portal_catalog')
    indexes = catalog.indexes()

    # Specify the indexes you want, with ('index_name', 'index_type')
    indexables = []

    for name, meta_type in INDEXES:
        if name in indexes:
            logger.info("*** Index '%s' already in Catalog [SKIP]" % name)
            continue

        logger.info("*** Adding Index '%s' for field '%s' to catalog ...", meta_type, name)
        catalog.addIndex(name, meta_type)
        indexables.append(name)
        logger.info("*** Added Index '%s' for field '%s' to catalog [DONE]", meta_type, name)

    if len(indexables) > 0:
        logger.info("*** Indexing new indexes '[%s]' ..." % (', '.join(indexables), ))
        catalog.manage_reindexIndex(ids=indexables)
        logger.info("*** Indexing new indexes '[%s]' [DONE]" % (', '.join(indexables), ))


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
    docs.setLocallyAllowedTypes(("plone.docs.project",))
    docs.setImmediatelyAddableTypes(("plone.docs.project",))

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
