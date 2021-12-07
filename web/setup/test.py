from sklearn.cluster import KMeans
import numpy as np
X = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
kmeans.labels_
print(kmeans.labels_)
cluster_assignment = kmeans.labels_

print(cluster_assignment)
clustered_sentences = [[] for i in range(2)]
for sentence_id, cluster_id in enumerate(cluster_assignment):
    print(sentence_id)
    print(cluster_id)
    clustered_sentences[cluster_id].append(X[sentence_id])

print(clustered_sentences)
    
clusters_list = []
for i, cluster in enumerate(clustered_sentences):
    sents = []
    for a in cluster:
        sents.append(a)
    clusters_list.append({ 'sents': sents, 'index': i })

print(clusters_list)
print(kmeans.cluster_centers_)