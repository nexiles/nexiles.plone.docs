from plone.docs.interfaces import *
from five import grok
from plone import api

class SerializableObject(grok.Adapter):
    grok.provides(ISerializable)
    grok.context(IModelBased)

    def toJson(self, request):
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


class Serializabledocmeta(SerializableObject):
    grok.provides(ISerializable)
    grok.context(Idocmeta)

    def toJson(self, request):
        host_name = request.get_header("NEXILES_DOC_HOST", "http://localhost:8888")
        doc_root  = request.get_header("NEXILES_DOC_ROOT", "/docs/")
        prefix = host_name + doc_root

        doc = self.context
        out = super(Serializabledocmeta, self).toJson(request)

        out.update({
            "version": doc.version,
            "doc_url": (doc.doc_url and prefix + doc.doc_url) or prefix + doc.id + "/" + doc.version + "/",
            "zip": (doc.zip and prefix + doc.zip) or prefix + doc.id + "/" + doc.version + ".zip",
            "doc_icon": doc.doc_icon and prefix + doc.doc_icon
        })
        return out

class SerializableProject(SerializableObject):
    grok.provides(ISerializable)
    grok.context(IProject)

    def toJson(self, request):
        released = None
        draft = None

        project = self.context
        out = super(SerializableProject, self).toJson(request)
        docs = project.docmetas()

        for doc in docs:
            state = api.content.get_state(obj=doc)
            if "released" in state and (not released or doc.compareTo(released) > 0):
                    released = doc
            elif not "private" in state and (not draft or doc.compareTo(draft) > 0):
                    draft = doc

        out.update({
            "github": project.github,
            "docs": map(lambda item: ISerializable(item).toJson(request), docs),
            "released": released and released.UID(),
            "latest": draft and draft.UID()
        })
        return out
