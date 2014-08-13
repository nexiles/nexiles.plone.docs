from five import grok

from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable


from plone.docs import MessageFactory as _

from distutils.version import StrictVersion

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

    # Add your class methods and properties here
    pass


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
            if "released" in state:
                if not released or StrictVersion(doc.version) > StrictVersion(released.version):
                    released = doc

            elif not "private" in state:
                if not draft or StrictVersion(doc.version) > StrictVersion(draft.version):
                    draft = doc

        out = []
        if released:
            out.append(buildRowData(released))
        if draft:
            out.append(buildRowData(draft))

        return out

    def docs(self):
        """Returns a dictionary of documentation to show
        """
        out = []
        for doc in self.context.values():
          out.append(buildRowData(doc))

        return out

# Helper Methods

def buildRowData(doc):
    return {
        "title": doc.title,
        "version": doc.version,
        "id":   doc.id,
        "modification_date": doc.modification_date,
        "creator": doc.Creator(),
        "state": doc.portal_workflow.getInfoFor(doc, "review_state").title().replace("_", " ")
    }
