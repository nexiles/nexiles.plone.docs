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

class IDocmeta(IModelBased):
    """Documentation meta data object.
    """

    form.model("models/docmeta.xml")

    def compareTo(doc):
        """ Returns 0 if this object and doc have the same version.
            Returns > 0 if this object has a higher version.
            Returns < 0 if doc has a higher version.
        """

class ISerializable(Interface):
    """Supports serialization to a JSON object.
    """

    def toJson(request):
        """Returns a dictionary that can be directly transformed into JSON.
           Takes a request argument to build data that depends on request
           specific information.
        """
