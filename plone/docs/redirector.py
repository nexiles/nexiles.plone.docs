from plone import api
import re
import logging
from plone.docs.interfaces import IProject
from plone.jsonapi.routes.interfaces import IInfo
from AccessControl.SecurityManagement import newSecurityManager

logger = logging.getLogger("plone.docs.redirector")

class DocHandler(object):
    """ Redirect handler registered as a ``redirect_handler`` Zope 3 <browser:page>
    """

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
        # See http://docs.plone.org/develop/plone/misc/commandline.html#posing-as-user
        # Hack for https://github.com/nexiles/nexiles.plone.docs/issues/11
        admin = api.user.get(userid="admin")
        newSecurityManager(None, admin)

        if url.endswith("/" + fieldname) or url.endswith("/" + fieldname + "/"):
            obj = api.content.get(path=re.sub("\/" + fieldname + "$", "", path))
            if not obj or not IProject.providedBy(obj):
                return None

            uid = IInfo(obj)()[fieldname]
            if not uid: return None

            latest = api.content.get(UID=uid)
            json = IInfo(latest)()

            logger.info("Redirect to %s", json["doc_url"])
            return json["doc_url"]

        return None
