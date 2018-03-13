import flow
from sys import argv
from matplotlib.path import Path
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import pickle

polygon = None
savedpolys = pickle.load(open('savedpolys.txt', 'rb'))
oldpolys = pickle.load(open('oldpolys.txt', 'rb'))
polytype = raw_input('(r)andom, (s)aved, (p)revious, or (n)ew polygon?\n')
if polytype == 'r':
	num = int(raw_input('How many vertices?\n'))
	polygon = flow.rand_poly(num)
elif polytype == 'p':
	n = raw_input('Which previous polygon do you want? (1-10)\n')
	n = int(n)
	polygon = oldpolys[n-1]
	flow.set_poly(polygon)
elif polytype == 'n':
	num = int(raw_input('How many vertices?\n'))
	polygon = flow.prompt(num)
elif polytype == 's':
	name = raw_input('Please enter the name of the polygon\n')
	for i in range(0, len(savedpolys[0])):
		if savedpolys[0][i] == name:
			polygon = savedpolys[1][i]
			flow.set_poly(polygon)	
			break
	if polygon == None:
		print('Polygon not found\n')

if polygon != None:
	oldpolys.insert(0,polygon)
	if len(oldpolys) > 10:
		del oldpolys[10]

pickle.dump(oldpolys, open('oldpolys.txt', 'wb'))
temp = polygon.copy()

flowtype = raw_input('(c)urvature, (t)angential, chow-(g)lickenstein, (r)enormalized chow-glickenstein, r(s)cg, or (m)odified curvature flow\n')
if flowtype == 'g':
	fig = flow.setup('glickenstein')
elif flowtype == 'r':
	fig = flow.setup('renormglick')
elif flowtype == 'c':
	fig = flow.setup('curvature')
elif flowtype == 't':
	fig = flow.setup('tangent')
elif flowtype == 's':
	fig = flow.setup('rscg')
elif flowtype =='m':
	fig = flow.setup('modified')
elif flowtype == 'o':
	fig = flow.setup('other')

#to change the speed of the animation change interval
anim = animation.FuncAnimation(fig, flow.animate, 100, repeat = True, blit = True, interval = 100)

#in order to save the animation as an mp4, remove the comment from the next line
#anim.save('polygon.mp4', fps = 10)

#displays the animation
plt.show()

#displays the graph of the isoperimetric ratio
flow.iso_plot()

#save = raw_input('Would you like to save this polygon? (y/n)\n')
#if save == 'y':
#	name = raw_input("Please name you polygon\n")
#	savedpolys[0].append(name)
#	savedpolys[1].append(temp)	
#pickle.dump(savedpolys, open('savedpolys.txt', 'wb'))
