def make_serializable(document):
    """
    Convert document['_id'] from ObjectId to string, so that it can be serialized and set in the response.
    """
    document['_id'] = str(['_id'])
