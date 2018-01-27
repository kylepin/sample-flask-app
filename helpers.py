from copy import deepcopy

def make_serializable(document):
    """
    Convert document['_id'] from ObjectId to string, so that it can be serialized and set in the response.
    """
    document_copy = deepcopy(document)
    document_copy['_id'] = str(document_copy['_id'])
    return document_copy
