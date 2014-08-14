from five import grok

from plone.dexterity.content import Item

from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable


from plone.docs import MessageFactory as _

from distutils.version import StrictVersion


# Interface class; used to define content-type schema.

class Idocmeta(form.Schema, IImageScaleTraversable):
    """
    Documentation meta data object
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/docmeta.xml to define the content type.

    form.model("models/docmeta.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class docmeta(Item):
    grok.implements(Idocmeta)

    def toJson(self, request):
        """ Returns a dictionary that contains serializable information
        """
        host_name = request.get_header("NEXILES_DOC_HOST", "http://localhost:8888")
        doc_root  = request.get_header("NEXILES_DOC_ROOT", "/docs/")
        prefix = host_name + doc_root

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
            "version": self.version,
            "uid": self.UID(),
            "id": self.id,
            "url": self.absolute_url(),
            "doc_url": (self.doc_url and prefix + self.doc_url) or prefix + self.id + "/" + self.version + "/",
            "zip": (self.zip and prefix + self.zip) or prefix + self.id + "/" + self.version + ".zip",
            "doc_icon": self.doc_icon and prefix + self.doc_icon
        }

    def compareTo(self, doc):
        if doc is None:
            raise TypeError("Argument must not be None")
        if not isinstance(doc, docmeta):
            raise TypeError("Argument must be an instance of plone.docs.docmeta")
        if self is doc: return 0
        v1 = StrictVersion(self.version)
        v2 = StrictVersion(doc.version)
        if v1 == v2: return 0
        if v1 < v2: return -1
        return 1


# View class
# The view will automatically use a similarly named template in
# docmeta_templates.

class View(dexterity.DisplayForm):
    """ Default documentation view """

    grok.context(Idocmeta)
    grok.require('zope2.View')

    def json(self):
        return self.context.toJson(self.request)
