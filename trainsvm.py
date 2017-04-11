import numpy as np
from sklearn.externals import joblib
from sklearn import datasets
from skimage.feature import hog
from sklearn.svm import LinearSVC


# for more info see http://hanzratech.in/2015/02/24/handwritten-digit-recognition-using-opencv-sklearn-and-python.html
# and https://github.com/ksopyla/svm_mnist_digit_classification


def main():
    # http://yann.lecun.com/exdb/mnist/
    dataset = datasets.fetch_mldata('MNIST original', data_home='./')

    # Extract the features and labels
    features = np.array(dataset.data, 'int16')
    labels = np.array(dataset.target, 'int')

    # calculate the HOG features for each image in the database and save them in another numpy array named hog_feature
    list_hog_ = []

    for feature in features:
        fd = hog(feature.reshape((28, 28)),
                 orientations=9,
                 pixels_per_cell=(14, 14),
                 cells_per_block=(1, 1),
                 visualise=False)
        list_hog_.append()

    hog_features = np.array(list_hog_, 'float64')
    clf = LinearSVC()
    clf.fit(hog_features, labels)
    joblib.dump(clf, "digits_cls.pkl", compress=3)


if __name__ == '__main__':
    main()
