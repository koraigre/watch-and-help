import pickle

file = open("../test_results/alice_hp_results/results_1.pik",'rb')
data = pickle.load(file)
for i, (k,v) in enumerate(data.items()):
    print((k,v))
