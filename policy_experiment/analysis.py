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
    watch_list = ['policy.add-both',
            'policy.add-enemymove',
            'policy.add-enemyprot',
            #'policy.fast-policy',
            'policy.add-frd-emy-x-move-prot'
            ]

    plot_list = []
    for folder in watch_list:
        a = load_log_file(folder+'/log.txt')
        a = a[a<1]
        a = smooth(a)
        f, = plt.plot(a)
        plot_list.append(f)

    plt.legend(plot_list, watch_list, loc=4)
    plt.show()


