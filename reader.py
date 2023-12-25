from whoosh.index import open_dir


ix = open_dir("indexdir")


with ix.searcher() as searcher:
    num_docs = searcher.reader().doc_count_all()


