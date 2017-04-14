import numpy as np
from sklearn.externals import joblib
from sklearn import datasets
from skimage.feature import hog
from sklearn.svm import LinearSVC


def main():
    dataset = datasets.fetch_mldata('MNIST Original')
    features = np.array(dataset.data, 'int16')
    labels = np.array(dataset.target, 'int')

    hogfds = []
    for feature in features:
        fd = hog(feature.reshape((28, 28)),
                 orientations=9,
                 pixels_per_cell=(14, 14),
                 cells_per_block=(1, 1),
                 visualise=False,
                 block_norm='L2-Hys')
        hogfds.append(fd)

    hogFeatures = np.array(hogfds, 'float64')

    svmClassifier = LinearSVC()
    svmClassifier.fit(hogFeatures, labels)
    joblib.dump(svmClassifier, 'svmClassifier.pkl', compress=3)


if __name__ == '__main__':
    main()
