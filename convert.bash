 for s in \
    "s/import hammock.resource as resource/import hammock/" \
    "s/from hammock import resource/import hammock/" \
    s/resource.passthrough/hammock.sink/ \
    s/resource.delete/hammock.delete/ \
    s/resource.get/hammock.get/ \
    s/resource.put/hammock.put/ \
    s/resource.post/hammock.post/ \
    s/resource.head/hammock.head/ \
    s/resource.patch/hammock.patch/ \
    s/resource.TOKEN_ENTRY/hammock.TOKEN_ENTRY/ \
    s/resource.sink/hammock.sink/ \
    s/resource.Resource/hammock.Resource/ \
    s/resource.KW_HEADERS/hammock.KW_HEADERS/ \
    s/resource.TYPE_JSON/hammock.TYPE_JSON/ \
    s/resource.TYPE_OCTET_STREAM/hammock.TYPE_OCTET_STREAM/ \
    s/resource.CONTENT_TYPE/hammock.CONTENT_TYPE/ \
    s/resource.CONTENT_LENGTH/hammock.CONTENT_LENGTH/ \

do
    sed -i "$s" `find $1 -name "*.py"`
done

