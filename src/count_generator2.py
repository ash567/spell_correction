def has_special_characters(word):
	spl_characters = "@#$%^&*|\<=>/0123456789~`_+"
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

# building the modified dictionary
def possible_words_delete(word):
	edit_list = set([word])
	for i in range(len(word)):
		edit_list.add(word[0:i] + word[i+1:])
		for j in range(i, len(word)):
			edit_list.add(word[0:i] + word[i+1:j] + word[j+1:])
	edit_list.discard('')
	return edit_list

word_count = {}
total_word_count = 0

data_path = '../data/'

f = open(data_path+'w2_.txt', 'r')
for l in f:
	ls = l.split()
	ls[0] = int(ls[0])
	temp = normalize_text(ls[1])+normalize_text(ls[2])
	for w in temp:
		if w in word_count:
			word_count[w] += ls[0]
		else:
			word_count[w] = ls[0]
f.close()

f = open(data_path+'dictionary.txt', 'w')
for word, count in word_count.items():
	f.write(word+'\t'+str(count)+'\n')
f.close()

modified_dict = {}
for word, count in word_count.items():
	word_set = possible_words_delete(word)
	for word_mod in word_set:
		if word_mod in modified_dict:
			modified_dict[word_mod].add(word)
		else:
			modified_dict[word_mod] = set([word])

f = open(data_path+'modified_dictionary.txt', 'w')
for word, s in modified_dict.items():
	f.write(word)
	for item in s:
		f.write('\t' + item)
	f.write('\n')
f.close()

# -----------------------------------------------

char_count = {}
bigram_count = {}

f = open(data_path+'big.txt', 'r')
s = f.read()
f.close()
ls = normalize_text(s)
for l in ls:
	for c in l:
		if c in char_count:
			char_count[c] += 1
		else:
			char_count[c] = 1
	for c1, c2 in zip(l, l[1:]):
		if c1+c2 in bigram_count:
			bigram_count[c1+c2] += 1
		else:
			bigram_count[c1+c2] = 1
	if '#'+l[0] in bigram_count:
		bigram_count['#'+l[0]] += 1
	else:
		bigram_count['#'+l[0]] = 1

char_count['#'] = len(ls)


f = open(data_path+'char_count.txt', 'w')
for c, count in char_count.items():
	f.write(c+'\t'+str(count)+'\n')
f.close()
f = open(data_path+'bigram_count.txt', 'w')
for bg, count in bigram_count.items():
	f.write(bg+'\t'+str(count)+'\n')
f.close()
