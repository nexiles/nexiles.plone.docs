from five import grok
from plone.dexterity.content import Container
from plone.directives import dexterity
from plone import api
from plone.jsonapi.routes.interfaces import IInfo

from plone.docs import MessageFactory as _
from plone.docs.interfaces import IProject


class Project(Container):
    grok.implements(IProject)

    def docmetas(self):
        path = self.getPhysicalPath()
        path = "/".join(path)
        catalog = api.portal.get_tool(name="portal_catalog")
        brains = catalog(portal_type="plone.docs.docmeta", path={"query": path, "depth": 1})
        return map(lambda brain: brain.getObject(), brains)


# View class
# The view will automatically use a similarly named template in
# project_templates.

class View(dexterity.DisplayForm):
    """ Default Project View """

    grok.context(IProject)
    grok.require('zope2.View')

    def json(self):
        """ Returns information for the view
        """
        json = IInfo(self.context)()

        out = []
        if json["released"]: out.append(self.getByUid(json["released"]))
        if json["latest"]: out.append(self.getByUid(json["latest"]))
        json["all_latest"] = out

        return json

    def getByUid(self, uid):
        obj = api.content.get(UID=uid)
        return IInfo(obj)()
