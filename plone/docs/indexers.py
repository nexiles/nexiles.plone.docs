from plone.indexer.decorator import indexer
from plone.docs.interfaces import Idocmeta

@indexer(Idocmeta)
def docmeta_doc_url(obj):
     return obj.get_doc_url()

@indexer(Idocmeta)
def docmeta_zip(obj):
     return obj.get_zip()
