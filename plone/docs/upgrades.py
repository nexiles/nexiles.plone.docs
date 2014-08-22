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
    brains = catalog(portal_type='plone.docs.docmeta')

    count = 0
    for brain in brains:
        source = brain.getObject()
        data = {
            "title": source.title,
            "parent": source.getParentNode(),
            "version": source.version,
            "doc_url": source.doc_url,
            "doc_icon": source.doc_icon,
            "zip": source.zip,
            "creators": source.Creator()
        }
        api.content.delete(obj = source)
        doc = api.content.create(
            type='plone.docs.docmeta',
            title=data["title"],
            container=data["parent"])
        doc.version = data["version"]
        doc.doc_url = data["doc_url"]
        doc.zip = data["zip"]
        doc.doc_icon = data["doc_icon"]
        doc.setCreators(data["creators"])
        count += 1

    logger.info("%s objects converted." % count)
