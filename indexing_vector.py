from gensim import corpora, models
import os
from docx import Document


directory = 'documents/'


def extract_text_from_docx(filename):
    doc = Document(filename)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])


documents = []
for filename in os.listdir(directory):
    if filename.endswith('.docx'):
        document_text = extract_text_from_docx(os.path.join(directory, filename))
        documents.append(document_text)


texts = [[word for word in document.lower().split()] for document in documents]


dictionary = corpora.Dictionary(texts)


corpus = [dictionary.doc2bow(text) for text in texts]


tfidf = models.TfidfModel(corpus)


dictionary.save('tmp/dictionary.dict')
corpora.MmCorpus.serialize('tmp/corpus.mm', corpus)
tfidf.save("tmp/model.tfidf")
