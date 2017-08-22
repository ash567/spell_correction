def has_special_characters(word):
	spl_characters = "@#$%^&*|\<=>/0123456789~`_+-"
	return any(map(lambda x: x in spl_characters, word))

def normalize_word(word):
	if has_special_characters(word):
		return ""
	else:
		return ''.join([w for w in word.lower() if w.isalpha()])

def normalize_text(s):
	ls = s.split()
	ls = [l.split('-') for l in ls]
	ls = [l_ for l in ls for l_ in l]
	ls = [normalize_word(w) for w in ls]
	ls = [w for w in ls if w != ""]
	return ls

data_path = '../data/'

# two_count = {}
one_count = {}
adjacency_list = {}

f = open(data_path+'w3_.txt', 'r')
for l in f:
	count, w1, w2, w3 = l.split()
	count = int(count)
	ls = normalize_text(w1)+normalize_text(w2)+normalize_text(w3)
	for i in range(len(ls)):
		if ls[i] in one_count:
			one_count[ls[i]] += count
		else:
			one_count[ls[i]] = count
		for j in range(i):
			# if (ls[i], ls[j]) in two_count:
			# 	two_count[(ls[i], ls[j])] += count
			# elif (ls[j], ls[i]) in two_count:
			# 	two_count[(ls[j], ls[i])] += count
			# else:
			# 	two_count[(ls[i], ls[j])] = count
			if ls[i] not in adjacency_list:
				adjacency_list[ls[i]] = {}
			if ls[j] not in adjacency_list:
				adjacency_list[ls[j]] = {}
			if ls[j] not in adjacency_list[ls[i]]:
				adjacency_list[ls[i]][ls[j]] = count
			else:
				adjacency_list[ls[i]][ls[j]] += count
			if ls[i] not in adjacency_list[ls[j]]:
				adjacency_list[ls[j]][ls[i]] = count
			else:
				adjacency_list[ls[j]][ls[i]] += count
f.close()


counter = 1

f = open(data_path+'word_cooccurence_count.txt', 'w')

for w1, l1 in adjacency_list.items():
	print counter
	counter += 1
	adjacency_list_temp = l1.copy()
	for w2, count12 in l1.items():
		for w3, count23 in adjacency_list[w2].items():
			if w3 not in adjacency_list_temp:
				adjacency_list_temp[w3] = 0
			adjacency_list_temp[w3] += int(float(count12*count23)/one_count[w2]/2)
	for w2, count in adjacency_list_temp.items():
		if w1 < w2 and count > 0:
			f.write(w1+'\t'+w2+'\t'+str(count)+'\n')
f.close()


f = open(data_path+'word_count.txt', 'w')
for word, count in one_count.items():
	f.write(word+'\t'+str(count)+'\n')
f.close()
# f = open(data_path+'word_cooccurence_count.txt', 'w')
# for (word1, word2), count in two_count.items():
# 	f.write(word1+'\t'+word2+'\t'+str(count)+'\n')
# f.close()

# for w1, l1 in adjacency_list_modified.items():
# 	for w2, count in l1.items():
# 		if w1 < w2:
# 			f.write(w1+'\t'+w2+'\t'+str(count)+'\n')
# f.close()