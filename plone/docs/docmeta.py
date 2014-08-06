from five import grok

from plone.dexterity.content import Item

from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable


from plone.docs import MessageFactory as _


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

    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# docmeta_templates.

class View(dexterity.DisplayForm):
    """ Default documentation view """

    grok.context(Idocmeta)
    grok.require('zope2.View')

    def baseUrl(self):
      host_name = self.request.get_header("NEXILES_DOC_HOST", "http://localhost:8888")
      doc_root  = self.request.get_header("NEXILES_DOC_ROOT", "/docs/")
      return host_name + doc_root

    def contextUrl(self):
      return (self.context.url and self.baseUrl() + self.context.url) or self.baseUrl() + self.context.title + "/v" + self.context.version + "/"

    def contextZip(self):
      return (self.context.zip and self.baseUrl() + self.context.url) or self.baseUrl() + self.context.title + "/v" + self.context.version + ".zip"
