from five import grok

from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable


from plone.docs import MessageFactory as _
from plone.docs.docmeta import docmeta

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
      return filter(lambda v: isinstance(v, docmeta), self.values())

    def toJson(self, request):
        """ Returns a dictionary that contains serializable information
        """
        released = None
        draft = None

        docs = self.docmetas()

        for doc in docs:
            state = doc.portal_workflow.getInfoFor(doc, "review_state")
            if "released" in state and (not released or doc.compareTo(released) > 0):
                    released = doc

            elif not "private" in state and (not draft or doc.compareTo(draft) > 0):
                    draft = doc

        state = self.portal_workflow.getInfoFor(self, "review_state")
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

        out = {
            "title": self.title,
            "state": state,
            "visibility": visibility,
            "github": self.github,
            "uid": self.UID(),
            "id": self.id,
            "url": self.absolute_url(),
            "docs": map(lambda item: item.toJson(request), docs),
            "latest": {}
        }

        if released: out["latest"]["released"] = released.UID()
        if draft: out["latest"]["draft"] = draft.UID()

        return out


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
        json["latest"] = [
            self.extendJson(api.content.get(UID=json["latest"][key]).toJson(self.request)) for key in json["latest"].keys()
        ]
        json["docs"] = [
            self.extendJson(doc) for doc in json["docs"]
        ]
        return json

    def extendJson(self, doc):
        obj = api.content.get(UID=doc["uid"])
        doc["modification_date"] = obj.modification_date
        doc["creator"] = obj.Creator()
        return doc
