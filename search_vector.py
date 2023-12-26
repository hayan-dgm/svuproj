



































































from gensim import corpora, models, similarities
from docx import Document
import os
from nltk.tokenize import sent_tokenize
import re


directory = 'documents/'


def extract_text_from_docx(filename):
    doc = Document(filename)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])


def highlight_terms(text, terms):
    """Wrap the search terms in HTML tags in the text."""
    for term in terms:
        text = re.sub(f'\\b{term}\\b', f'<b style="background-color: yellow;">{term}</b>', text, flags=re.IGNORECASE)
    return text


documents = []
filenames = []  
def listFiles():
    for filename in os.listdir(directory):
        if filename.endswith('.docx'):
            document_text = extract_text_from_docx(os.path.join(directory, filename))
            sentences = sent_tokenize(document_text)  
            documents.extend(sentences)  
            filenames.extend([filename] * len(sentences))  


    texts = [[word for word in document.lower().split()] for document in documents]


    dictionary = corpora.Dictionary(texts)


    corpus = [dictionary.doc2bow(text) for text in texts]


    tfidf = models.TfidfModel(corpus)


    dictionary.save('tmp/dictionary.dict')
    corpora.MmCorpus.serialize('tmp/corpus.mm', corpus)
    tfidf.save("tmp/model.tfidf")

def search(query, threshold = 0.1):
    
    dictionary = corpora.Dictionary.load('tmp/dictionary.dict')
    corpus = corpora.MmCorpus('tmp/corpus.mm')
    tfidf = models.TfidfModel.load("tmp/model.tfidf")

    
    index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary))

    
    query_bow = dictionary.doc2bow(query.lower().split())
    sims = index[tfidf[query_bow]]

    
    results = {}

    for document_number, score in sorted(enumerate(sims), key=lambda x: x[1], reverse=True):
        print(len(filenames))
        if score > threshold:  
            title = filenames[document_number]
            if title not in results:
                results[title] = {'sentences': [], 'rank': score}
            sentence = documents[document_number]
            highlighted_sentence = highlight_terms(sentence, query.lower().split())
            results[title]['sentences'].append(highlighted_sentence)

    return results
