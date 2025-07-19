import matplotlib.pyplot as plt
#%matplotlib inline

x = [1,2,3,4,5]
y = [10,30,25,35,55]

plt.title("Graph")
plt.xlabel("x-axis")
plt.ylabel("y-axis")


#plt.plot(x, y, color='r', alpha=0.5, label='line plot')
#plt.bar(x, y, color='b', alpha=0.5, label='bar plot')
plt.hist(x, y, color='g', alpha=0.5, label='histogram plot')


plt.legend()
plt.grid()
plt.show()
