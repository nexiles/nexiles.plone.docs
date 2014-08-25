from five import grok
from plone.dexterity.content import Item
from plone.directives import dexterity
from distutils.version import StrictVersion

from plone.docs import MessageFactory as _
from plone.docs.interfaces import Idocmeta, ISerializable


class docmeta(Item):
    grok.implements(Idocmeta)

    def compareTo(self, doc):
        if doc is None:
            raise TypeError("Argument must not be None")
        if not Idocmeta.providedBy(doc):
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
        serializer = ISerializable(self.context)
        return serializer.toJson(self.request)
