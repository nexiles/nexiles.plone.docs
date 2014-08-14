from plone import api

import logging

PROFILE_ID = "profile-plone.docs:default"

def convert_docs(context, logger=None):
    """Method to convert docmetas to plone.docs.docmeta.

    When called from the import_various method, 'context' is
    the plone site and 'logger' is the portal_setup logger.

    But this method will be used as upgrade step, in which case 'context'
    will be portal_setup and 'logger' will be None.

    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('plone.docs')

    setup = api.portal.get_tool(name='portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')

    catalog = api.portal.get_tool(name='portal_catalog')
    brains = catalog(portal_type='docmeta')

    count = 0
    for brain in brains:
        source = brain.getObject()
        doc = api.content.create(
            type='plone.docs.docmeta',
            title=source.title,
            container=source.getParentNode())
        doc.version = source.version
        doc.url = source.url
        doc.zip = source.zip
        doc.icon = source.icon
        doc.setCreators(source.Creator())
        api.content.delete(obj = source)
        count += 1

    logger.info("%s objects converted." % count)

def update_doc_folder(context, logger=None):
    """Method to fix documentation folder

    When called from the import_various method, 'context' is
    the plone site and 'logger' is the portal_setup logger.

    But this method will be used as upgrade step, in which case 'context'
    will be portal_setup and 'logger' will be None.

    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('plone.docs')

    portal = api.portal.get()

    docs = portal["documentation"]
    docs.setLocallyAllowedTypes(("plone.docs.docmeta", "plone.docs.project"))
    docs.setImmediatelyAddableTypes(("plone.docs.docmeta", "plone.docs.project"))
