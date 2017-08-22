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

two_count = {}
one_count = {}

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
			if (ls[i], ls[j]) in two_count:
				two_count[(ls[i], ls[j])] += count
			elif (ls[j], ls[i]) in two_count:
				two_count[(ls[j], ls[i])] += count
			else:
				two_count[(ls[i], ls[j])] = count
f.close()

f = open(data_path+'word_count.txt', 'w')
for word, count in one_count.items():
	f.write(word+'\t'+str(count)+'\n')
f.close()

f = open(data_path+'word_cooccurence_count.txt', 'w')
for (word1, word2), count in two_count.items():
	f.write(word1+'\t'+word2+'\t'+str(count)+'\n')
f.close()