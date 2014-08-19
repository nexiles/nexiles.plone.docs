from five import grok

from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable


from plone.docs import MessageFactory as _

from plone import api

# Interface class; used to define content-type schema.

class IProject(form.Schema, IImageScaleTraversable):
    """
    Contains documentation objects and links for a project.
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/project.xml to define the content type.

    form.model("models/project.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Project(Container):
    grok.implements(IProject)

    def docmetas(self):
        """Returns all docmetas found in the project.
        """
        path = self.getPhysicalPath()
        path = "/".join(path)
        catalog = api.portal.get_tool(name="portal_catalog")
        brains = catalog(portal_type="plone.docs.docmeta", path={"query": path, "depth": 1})
        return map(lambda brain: brain.getObject(), brains)

    def toJson(self, request):
        """ Returns a dictionary that contains serializable information
        """
        released = None
        draft = None

        docs = self.docmetas()

        for doc in docs:
            state = api.content.get_state(obj=doc)
            if "released" in state and (not released or doc.compareTo(released) > 0):
                    released = doc

            elif not "private" in state and (not draft or doc.compareTo(draft) > 0):
                    draft = doc

        state = api.content.get_state(obj=self)
        if "external" in state:
            visibility = "external"
        elif "internal" in state:
            visibility = "internal"
        else:
            visibility = state

        if "released" in state:
            state = "released"
        elif state != "private":
            state = "draft"

        return {
            "title": self.title,
            "state": state,
            "visibility": visibility,
            "github": self.github,
            "uid": self.UID(),
            "id": self.id,
            "url": self.absolute_url(),
            "modification_date": api.portal.get_localized_time(datetime=self.modification_date, long_format=1),
            "docs": map(lambda item: item.toJson(request), docs),
            "released": released and released.UID(),
            "latest": draft and draft.UID()
        }


# View class
# The view will automatically use a similarly named template in
# project_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(dexterity.DisplayForm):
    """ Default Project View """

    grok.context(IProject)
    grok.require('zope2.View')

    def json(self):
        """ Returns information for the view
        """
        json = self.context.toJson(self.request)
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
            out = obj.toJson(self.request)
        out["creator"] = obj.Creator()
        return out
