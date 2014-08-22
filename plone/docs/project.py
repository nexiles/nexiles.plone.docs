from five import grok
from plone.dexterity.content import Container
from plone.directives import dexterity
from plone import api

from plone.docs import MessageFactory as _
from plone.docs.interfaces import IProject, ISerializable


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
        serializer = ISerializable(self.context)
        json = serializer.toJson(self.request)
        json["docs"] = [
            self.extendJson(doc["uid"], doc) for doc in json["docs"]
        ]

        out = []
        if json["released"]: out.append(self.extendJson(json["released"]))
        if json["latest"]: out.append(self.extendJson(json["latest"]))
        json["all_latest"] = out

        return json

    def extendJson(self, uid, out=None):
        obj = api.content.get(UID=uid)
        if not out:
            sobj = ISerializable(obj)
            out = sobj.toJson(self.request)
        out["creator"] = obj.Creator()
        return out
