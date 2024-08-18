import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# 生成示例数据
np.random.seed(0)
X = np.random.rand(100, 2)  # 100个数据点，每个点有2个特征

# K-means 聚类
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X)

# 输出
labels = kmeans.labels_  # 每个数据点的簇标签
centers = kmeans.cluster_centers_  # 聚类中心
inertia = kmeans.inertia_  # 簇内距离之和

# 将结果转换为DataFrame
df = pd.DataFrame(X, columns=['Feature1', 'Feature2'])
df['Cluster'] = labels

# 打印结果
print("Cluster Centers:\n", centers)
print("Inertia:", inertia)

# 可视化结果
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Feature1', y='Feature2', hue='Cluster', data=df, palette='viridis', alpha=0.6)
plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.75, label='Centers')
plt.title('K-means Clustering')
plt.legend()
plt.show()
