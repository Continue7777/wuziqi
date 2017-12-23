import copy
a = {1:'12',2:'13'}
b = copy.deepcopy(a)
a['3'] = 4
print b