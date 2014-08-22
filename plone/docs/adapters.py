from plone.docs.interfaces import *
from five import grok
from plone import api

class SerializableDocmeta(grok.Adapter):
    grok.provides(ISerializable)
    grok.context(IDocmeta)

    def toJson(self, request):
        host_name = request.get_header("NEXILES_DOC_HOST", "http://localhost:8888")
        doc_root  = request.get_header("NEXILES_DOC_ROOT", "/docs/")
        prefix = host_name + doc_root

        doc = self.context

        state = api.content.get_state(obj=doc)
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
            "title": doc.title,
            "state": state,
            "visibility": visibility,
            "version": doc.version,
            "uid": doc.UID(),
            "id": doc.id,
            "url": doc.absolute_url(),
            "modification_date": api.portal.get_localized_time(datetime=doc.modification_date, long_format=1),
            "doc_url": (doc.doc_url and prefix + doc.doc_url) or prefix + doc.id + "/" + doc.version + "/",
            "zip": (doc.zip and prefix + doc.zip) or prefix + doc.id + "/" + doc.version + ".zip",
            "doc_icon": doc.doc_icon and prefix + doc.doc_icon
        }

class SerializableProject(grok.Adapter):
    grok.provides(ISerializable)
    grok.context(IProject)

    def toJson(self, request):
        released = None
        draft = None

        project = self.context
        docs = project.docmetas()

        for doc in docs:
            state = api.content.get_state(obj=doc)
            if "released" in state and (not released or doc.compareTo(released) > 0):
                    released = doc

            elif not "private" in state and (not draft or doc.compareTo(draft) > 0):
                    draft = doc

        state = api.content.get_state(obj=project)
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
            "title": project.title,
            "state": state,
            "visibility": visibility,
            "github": project.github,
            "uid": project.UID(),
            "id": project.id,
            "url": project.absolute_url(),
            "modification_date": api.portal.get_localized_time(datetime=project.modification_date, long_format=1),
            "docs": map(lambda item: ISerializable(item).toJson(request), docs),
            "released": released and released.UID(),
            "latest": draft and draft.UID()
        }
