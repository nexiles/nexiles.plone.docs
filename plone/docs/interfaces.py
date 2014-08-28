from zope.interface import Interface

from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable

class IModelBased(form.Schema, IImageScaleTraversable):
    """Supertype for model-driven types.
    """

class IProject(IModelBased):
    """Contains docmeta objects and links for a project.
    """

    form.model("models/project.xml")

    def docmetas():
        """Returns all contained docmetas found in the project.
           Only the for the user visible objects are returned.
        """

class Idocmeta(IModelBased):
    """Documentation meta data object.
    """

    form.model("models/docmeta.xml")

    def compareTo(doc):
        """ Returns 0 if this object and doc have the same version.
            Returns > 0 if this object has a higher version.
            Returns < 0 if doc has a higher version.
        """

    def get_doc_url():
        """ Returns doc_url or if doc_url is not set a generated url
        """

    def get_zip():
        """ Returns zip or if zip is not set a generated zip url
        """
