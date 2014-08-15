from plone import api

import re
import logging

from plone.docs.project import Project

logger = logging.getLogger("plone.docs.redirector")

class DocHandler():
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
            if not obj or not isinstance(obj, Project):
                return None

            latest = obj.toJson(self.request)[fieldname]
            if not latest: return None

            url = latest["doc_url"]

            logger.info("Redirect to %s", url)
            return url

        return None
