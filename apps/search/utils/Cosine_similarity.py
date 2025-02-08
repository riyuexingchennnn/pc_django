import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# 数据清洗
def preprocess(text):
    # 使用 jieba 分词
    words = jieba.cut(text)
    return " ".join(words)  # 返回空格分割的词汇


def cos_similarity(sentence1, sentence2):
    sentence1 = preprocess(sentence1)
    sentence2 = preprocess(sentence2)

    # print('***************************************************')
    # print(sentence1+'*************'+sentence2)
    # print('***************************************************')

    # 创建 TF-IDE 向量
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([sentence1, sentence2])

    # 计算余弦相似度
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    # print("两句话的余弦相似度：", similarity[0][0])

    return similarity
