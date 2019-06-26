import numpy as np
import pandas as pd
from sklearn import neighbors
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.feature_extraction import DictVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix


# leave one out
def knn_training_validation_loo_1(df, n_neighbors):
    X = df.drop('grade', axis=1)
    Y = df['grade']
    right_num = 0
    X_train, X_test, y_train, y_test = train_test_split(X, Y)
    # scaler = StandardScaler()
    # scaler.fit(X_train)
    # X_train = scaler.transform(X_train)
    # X_test = scaler.transform(X_test)

    clf = neighbors.KNeighborsClassifier(n_neighbors, weights="distance")
    clf.fit(X_train, y_train)
    predictions  = clf.predict(X_test)

    # accurate = right_num / data.shape[0]
    print(confusion_matrix(y_test, predictions))
    print(classification_report(y_test, predictions))

    # return accurate


# leave one out
def knn_training_validation_loo(data, n_neighbors):
    np.random.shuffle(data)
    X = data[:, :-1]
    Y = data[:, -1]
    right_num = 0
    loo = LeaveOneOut()
    for train_idx, valid_idx in loo.split(data):
        trainX, validX = X[train_idx], X[valid_idx]
        trainY, validY = Y[train_idx], Y[valid_idx]

        clf = neighbors.KNeighborsClassifier(n_neighbors, weights="distance")
        clf.fit(trainX, trainY)
        predictY = clf.predict(validX)

        if predictY[0] == validY[0]:
            right_num += 1

    accurate = right_num / data.shape[0]
    return accurate


def knn_training(feature_list):
    K = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 29, 31]
    best_k = -1
    best_arr = 0.
    for k in K:

        avg_accurate = knn_training_validation_loo(feature_list, k)
        print("k = %s, average accurate is %s" % (k, avg_accurate))

        if avg_accurate > best_arr:
            best_k = k
            best_arr = avg_accurate

    print("best k is %s, best accurate is %s" % (best_k, best_arr))


def test():
    FEATURE_NAME = [
        "PhoneDefectCount",
        # surface AA
        "AADefectCount",
        # scratch on surface AA
        "AAScratchCount",
        "AASMaxLength", "AASMinLength", "AASMeanLength",
        "AASMaxWidth", "AASMinWidth", "AASMeanWidth",
        "AASMaxArea", "AASMinArea", "AASMeanArea",
        "AASMaxContrast", "AASMinContrast", "AASMeanContrast",
        # nick on surface AA
        "AANickCount",
        "AANMaxLength", "AANMinLength", "AANMeanLength",
        "AANMaxWidth", "AANMinWidth", "AANMeanWidth",
        "AANMaxArea", "AANMinArea", "AANMeanArea",
        "AANMaxContrast", "AANMinContrast", "AANMeanContrast",
        # crack on surface AA
        "AACrackCount",
        "AACMaxLength", "AACMinLength", "AACMeanLength",
        "AACMaxWidth", "AACMinWidth", "AACMeanWidth",
        "AACMaxArea", "AACMinArea", "AACMeanArea",
        "AACMaxContrast", "AACMinContrast", "AACMeanContrast",
        # pindotgroup on surface AA
        "AAPinDotGroupCount",
        "AAPMaxLength", "AAPMinLength", "AAPMeanLength",
        "AAPMaxWidth", "AAPMinWidth", "AAPMeanWidth",
        "AAPMaxArea", "AAPMinArea", "AAPMeanArea",
        "AAPMaxContrast", "AAPMinContrast", "AAPMeanContrast",
        # distance variance
        "AADistanceVar",
        # additional feature1
        "AAAddFeat1",

        # surface A
        "ADefectCount",
        # scratch on surface A
        "AScratchCount",
        "ASMaxLength", "ASMinLength", "ASMeanLength",
        "ASMaxWidth", "ASMinWidth", "ASMeanWidth",
        "ASMaxArea", "ASMinArea", "ASMeanArea",
        "ASMaxContrast", "ASMinContrast", "ASMeanContrast",
        # nick on surface A
        "ANickCount",
        "ANMaxLength", "ANMinLength", "ANMeanLength",
        "ANMaxWidth", "ANMinWidth", "ANMeanWidth",
        "ANMaxArea", "ANMinArea", "ANMeanArea",
        "ANMaxContrast", "ANMinContrast", "ANMeanContrast",
        # crack on surface A
        "ACrackCount",
        "ACMaxLength", "ACMinLength", "ACMeanLength",
        "ACMaxWidth", "ACMinWidth", "ACMeanWidth",
        "ACMaxArea", "ACMinArea", "ACMeanArea",
        "ACMaxContrast", "ACMinContrast", "ACMeanContrast",
        # pindotgroup on surface A
        "APinDotGroupCount",
        "APMaxLength", "APMinLength", "APMeanLength",
        "APMaxWidth", "APMinWidth", "APMeanWidth",
        "APMaxArea", "APMinArea", "APMeanArea",
        "APMaxContrast", "APMinContrast", "APMeanContrast",
        # distance variance
        "ADistanceVar",
        # additional feature1
        "AAddFeat1",

        # surface B
        "BDefectCount",
        # scratch on surface B
        "BScratchCount",
        "BSMaxLength", "BSMinLength", "BSMeanLength",
        "BSMaxWidth", "BSMinWidth", "BSMeanWidth",
        "BSMaxArea", "BSMinArea", "BSMeanArea",
        "BSMaxContrast", "BSMinContrast", "BSMeanContrast",
        # nick on surface B
        "BNickCount",
        "BNMaxLength", "BNMinLength", "BNMeanLength",
        "BNMaxWidth", "BNMinWidth", "BNMeanWidth",
        "BNMaxArea", "BNMinArea", "BNMeanArea",
        "BNMaxContrast", "BNMinContrast", "BNMeanContrast",
        # crack on surface B
        "BCrackCount",
        "BCMaxLength", "BCMinLength", "BCMeanLength",
        "BCMaxWidth", "BCMinWidth", "BCMeanWidth",
        "BCMaxArea", "BCMinArea", "BCMeanArea",
        "BCMaxContrast", "BCMinContrast", "BCMeanContrast",
        # pindotgroup on surface B
        "BPinDotGroupCount",
        "BPMaxLength", "BPMinLength", "BPMeanLength",
        "BPMaxWidth", "BPMinWidth", "BPMeanWidth",
        "BPMaxArea", "BPMinArea", "BPMeanArea",
        "BPMaxContrast", "BPMinContrast", "BPMeanContrast",
        # distance variance
        "BDistanceVar",
        # additional feature1
        "BAddFeat1",

        # measurement discoloration
        "Rear_Cam", "Logo", "Switch", "Mic",
        "grade",
    ]
    db = np.loadtxt(open('train_data.csv'), delimiter=',', skiprows=1)
    samples_df = pd.DataFrame(db, columns=FEATURE_NAME)
    for i in range(11, 31, 3):
        print('k is {}'.format(i))
        knn_training_validation_loo_1(samples_df, i)
    # print("best accurate is %s" % (accurate))
    # knn_training(samples_df.values)


def grade(filename):
    pass


# generate fake data
r = {
    'All-A-ALL': 0,
    'All-A-Major': 0,
    'All-AA-ALL': 0,
    'All-AA-Major': 0,
    'All-AA-Zone1': 0,
    'All-AA-Zone2': 0,
    'All-AA-Zone3': 0,
    'All-AA-Zone4': 0,
    'All-AA-Zone5': 0,
    'All-B-ALL': 0,
    'All-B-Major': 0,
    'All-C-ALL': 0,
    'All-C-Major': 0,
    'Discoloration-B-Area1': 0,
    'Discoloration-B-Logo': 0,
    'Discoloration-B-Mic': 0,
    'Discoloration-B-Rear_Cam': 0,
    'Discoloration-B-Switch': 0,
    'Nick-A-Minor': 0,
    'Nick-A-Other1': 0,
    'Nick-A-Other2': 0,
    'Nick-A-S': 0,
    'Nick-AA-Minor': 0,
    'Nick-AA-Other1': 0,
    'Nick-AA-Other2': 0,
    'Nick-B-Major': 0,
    'Nick-B-MajorC': 0,
    'Nick-B-Minor': 0,
    'Nick-B-MinorC': 0,
    'Nick-B-Other1': 0,
    'Nick-B-Other2': 0,
    'Nick-B-OtherC': 0,
    'Nick-B-S': 0,
    'PinDotGroup-A-10x10': 0,
    'PinDotGroup-B-10x10': 0,
    'PinDotGroup-B-10x40': 0,
    'PinDotGroup-B-Other': 0,
    'Scratch-A-Minor': 0,
    'Scratch-A-Other1': 0,
    'Scratch-A-Other2': 0,
    'Scratch-A-Other3': 0,
    'Scratch-A-S1': 0,
    'Scratch-A-S2': 0,
    'Scratch-AA-Major': 0,
    'Scratch-AA-Minor': 0,
    'Scratch-AA-Other1': 0,
    'Scratch-AA-Other2': 0,
    'Scratch-AA-S': 0,
    'Scratch-B-Major': 0,
    'Scratch-B-Minor': 0,
    'Scratch-B-Other1': 0,
    'Scratch-B-Other2': 0,
    'Scratch-B-Other3': 0,
    'Scratch-B-S1': 0,
    'Scratch-B-S2': 0,
    'vzw': 0
}
