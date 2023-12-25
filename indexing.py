from whoosh.index import create_in
from whoosh.fields import *
import os
import textract





schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, vector=True))



if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

ix = create_in("indexdir", schema)


writer = ix.writer()


for root, dirs, files in os.walk('documents'):
    for filename in files:
        path = os.path.join(root, filename)
        content = textract.process(path,)
        content = content.decode('utf-8')
        writer.add_document(title=filename, path=path, content=content)


writer.commit()
