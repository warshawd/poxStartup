import matplotlib.pyplot as plt
import pickle

counter = 0


for totalPortSelect in range(6, 20):
  for switchPortSelect in range(4, totalPortSelect):
    # if (totalPortSelect * switchPortSelect) % 2 != 0:
    #   continue
    # if totalPortSelect == switchPortSelect:
    #   continue

    k = totalPortSelect
    r = switchPortSelect

    try:
      with open('k' + str(k) + 'r' + str(r) + '.pickle', 'rb') as handle:
        graph = pickle.load(handle)
    except:
      continue
    kshort = graph[0]
    ecmp8 = graph[1]
    ecmp64 = graph[2]


    def create_bucket_xy(plots) :
      x = []
      y = []
      total = 0
      x.append(total)
      y.append(0)
      for i in range(len(plots)) :
        num = plots[i]
        if num == 0:
          continue
        x.append(total)
        y.append(i)
        total += num
        x.append(total)
        y.append(i)
      return x, y

    plt.figure(counter)
    x, y = create_bucket_xy(kshort)
    plt.plot(x, y, label="k-shortest paths")
    x, y = create_bucket_xy(ecmp8)
    plt.plot(x, y, label="ecmp8")
    x, y = create_bucket_xy(ecmp64)
    plt.plot(x, y, label="ecmp64")

    plt.xlabel('Rank of Link')
    plt.ylabel('# Distinct Paths Link is on')
    plt.axis([0, 3000, 0, 18])
    plt.grid(True)
    plt.legend(loc=2)
    plt.show()
    counter += 1
