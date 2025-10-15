
if __name__ == '__main__':

    qrelsfile = ''
    resultsfile = ''
    outputfile = ''
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-qrels':
            qrelsfile = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-results':
            resultsfile = sys.argv[i + 1]
            i = i + 1
        elif sys.argv[i] == '-output':
            outputfile = sys.argv[i + 1]
            i = i + 1
        i = i + 1
