def iterate_attributes(obj):
    for att in dir(obj):
        if att.startswith('_'):
            continue
        att_obj = getattr(obj, att)
        if att_obj is None:
            continue
        if callable(att_obj):
            continue
        if isinstance(att_obj, list):
            for itr in att_obj:
                yield att, itr
        else:
            yield att, att_obj
