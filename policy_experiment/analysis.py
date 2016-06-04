import numpy as np
import matplotlib.pyplot as plt


def load_log_file(file_path):
    fh = open(file_path)
    s = fh.readlines()
    accuarcy = np.zeros((len(s),))
    for i in range(len(s)):
        accuarcy[i] = float(s[i][-5:-1])

    return accuarcy

def smooth(array, window=250):
    count = 0
    for i in range(1, window):
        count += array[i:i-window]
    count /= window
    return count


if __name__=='__main__':
    watch_list = [
            #'policy.orign',
            #'policy.add-enemymove',
            #'policy.add-enemyprot',
            'policy.add-all',
            'policy.fast-policy',
            'policy.resNet.add-all',
            'policy.pip.add-all',
            'policy.fc.add-all'
            ]

    plot_list = []
    for folder in watch_list:
        a = load_log_file(folder+'/log.txt')
        a = a[a<1]
        a = smooth(a)
        f, = plt.plot(a)
        plot_list.append(f)

    plt.legend(plot_list, watch_list, loc=4)
    plt.xlim(xmin=0, xmax=10000)
    plt.xlabel('epoch')
    plt.ylabel('accuracy')

    # plt.title('Validation Accuracy for Different Feature')
    plt.title('Validation Accuracy for Different Model')

    plt.show()
