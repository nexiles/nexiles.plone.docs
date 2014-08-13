from five import grok

from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable


from plone.docs import MessageFactory as _

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

    def toJson(self, request):
        """ Returns a dictionary that contains serializable information
        """
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

        return {
            "title": self.title,
            "state": state,
            "visibility": visibility,
            "uid": self.UID(),
            "id":   self.id,
            "docs": map(lambda item: item.toJson(request), self.values())
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

    def latest(self):
        """Returns the latest draft and the latest release
        """
        released = None
        draft = None

        for doc in self.context.values():
            state = self.context.portal_workflow.getInfoFor(doc, "review_state")
            if "released" in state and (not released or doc.compareTo(released) > 0):
                    released = doc

            elif not "private" in state and (not draft or doc.compareTo(draft) > 0):
                    draft = doc

        out = []
        if released:
            self.appendJson(released, out)
        if draft:
            self.appendJson(draft, out)
        return out

    def appendJson(self, doc, out):
        json = doc.toJson(self.request)
        json["modification_date"] = doc.modification_date
        out.append(json)

    def docs(self):
        """Returns a dictionary of documentation to show
        """
        out = []
        for doc in self.context.values():
          self.appendJson(doc, out)

        return out
