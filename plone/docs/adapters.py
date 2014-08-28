from plone.docs.interfaces import *
from plone.jsonapi.routes.interfaces import IInfo
from Products.ZCatalog.interfaces import ICatalogBrain
from zope.globalrequest import getRequest
from five import grok
from plone import api

class SerializableBrain(grok.Adapter):
    grok.provides(IInfo)
    grok.context(ICatalogBrain)

    def to_dict(self):
        return IInfo(self.context.getObject())()

    def __call__(self):
        return self.to_dict()

class SerializableObject(grok.Adapter):
    grok.provides(IInfo)
    grok.context(IModelBased)

    def to_dict(self):
        obj = self.context
        state = api.content.get_state(obj=obj)
        creator = api.user.get(userid=obj.Creator())

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
            "title": obj.title,
            "state": state,
            "visibility": visibility,
            "creator": {
                          "username": creator.getId(),
                          "fullname": creator.getProperty("fullname") or None
                       },
            "uid": obj.UID(),
            "id": obj.id,
            "url": obj.absolute_url(),
            "modification_date": api.portal.get_localized_time(datetime=obj.modification_date, long_format=1),
        }

    def __call__(self):
        return self.to_dict()

class SerializableDocmeta(SerializableObject):
    grok.provides(IInfo)
    grok.context(Idocmeta)

    def to_dict(self):
        """ Returns the dictionary representation of the object.
            May only be called during a request!
        """
        doc = self.context
        out = super(SerializableDocmeta, self).to_dict()

        request = getRequest()
        host_name = request.get_header("NEXILES_DOC_HOST", "http://localhost:8888")
        doc_root  = request.get_header("NEXILES_DOC_ROOT", "/docs/")
        prefix = host_name + doc_root

        out.update({
            "version": doc.version,
            "doc_url": prefix + doc.get_doc_url(),
            "zip": prefix + doc.get_zip(),
            "doc_icon": doc.doc_icon and prefix + doc.doc_icon
        })
        return out

class SerializableProject(SerializableObject):
    grok.provides(IInfo)
    grok.context(IProject)

    def to_dict(self):
        released = None
        draft = None

        project = self.context
        out = super(SerializableProject, self).to_dict()
        docs = project.docmetas()

        for doc in docs:
            state = api.content.get_state(obj=doc)
            if "released" in state and (not released or doc.compareTo(released) > 0):
                    released = doc
            elif not "private" in state and (not draft or doc.compareTo(draft) > 0):
                    draft = doc

        out.update({
            "github": project.github,
            "docs": map(lambda item: IInfo(item)(), docs),
            "released": released and released.UID(),
            "latest": draft and draft.UID()
        })
        return out
