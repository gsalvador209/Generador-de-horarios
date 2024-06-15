 
n = [3,3,3]
z = [3,3,3]

n.reverse()
z.reverse()
v = []
v_i = 1
for i in range(len(z)):
    v.append(v_i)
    v_i *= z[i]

id=0
for i in range(len(n)):
    if i != 0:
        id += (n[i]-1)*v[i]
    else:
        id += n[i]*v[i]
    #print(str(n[i]) + " * " + str(v[i]) + " = " + str(n[i]*v[i]))

print(str(v))
print(id)