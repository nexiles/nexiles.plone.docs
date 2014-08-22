from plone import api
import re
import logging
from plone.docs.interfaces import IProject, ISerializable

logger = logging.getLogger("plone.docs.redirector")

class DocHandler(object):
    """ Redirect handler registered as a ``redirect_handler`` Zope 3 <browser:page>
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, url, host, port, path):
        """ Handle redirects per site.

        :param path: Path as written in HTTP request (not site virtual path)

        :return: None if no redirect needed, otherwise a string full HTTP URL to the redirect target

        :raise: zExceptions.Redirect or other custom redirect exception if needed
        """

        result = self.redirectTo("released", url, path)
        if result:
          return result

        return self.redirectTo("latest", url, path)

    def redirectTo(self, fieldname, url , path):
        if url.endswith("/" + fieldname) or url.endswith("/" + fieldname + "/"):
            obj = api.content.get(path=re.sub("\/" + fieldname + "$", "", path))
            if not obj or not IProject.providedBy(obj):
                return None

            uid = ISerializable(obj).toJson(self.request)[fieldname]
            if not uid: return None

            latest = api.content.get(UID=uid)
            json = ISerializable(latest).toJson(self.request)

            logger.info("Redirect to %s", json["doc_url"])
            return json["doc_url"]

        return None
