import math
import ast
import sys
import operator


word_count = {}
total_word_count = 0

data_path = '../data/'

f = open(data_path+'dictionary.txt', 'r')
for l in f:
	word = l.split()[0].lower()
	count = int(l.split()[1])
	word_count[word] = count
	total_word_count += count
f.close()

word_prob_dict = {}
for word, count in word_count.items():
	word_prob_dict[word] = float(word_count[word]) / total_word_count

# Load the modified dictionary
modified_dict = {}
f = open(data_path+'modified_dictionary.txt', 'r')
for l in f:
	ls = l.split()
	modified_dict[ls[0]] = set(ls[1:])
f.close()

char_count = {}
total_char_count = 0
f = open(data_path+'char_count.txt', 'r')
for l in f:
	char, count = l.split('\t')
	count = int(count)
	char_count[char] = count
	total_char_count += count
f.close()

f = open(data_path+'bigram_count.txt', 'r')
bigram_count = {}
tot_bigram_count = 0
for l in f:
	bigram = l.split()[0]
	count = int(l.split()[1])
	bigram_count[bigram] = count
	tot_bigram_count += count
f.close()

f = open(data_path+'rev_matrix', 'r')
s = f.read()
rev_count = ast.literal_eval(s)
f.close()

f = open(data_path+'add_matrix', 'r')
s = f.read()
add_count = ast.literal_eval(s)
f.close()

f = open(data_path+'sub_matrix', 'r')
s = f.read()
sub_count = ast.literal_eval(s)
f.close()

f = open(data_path+'del_matrix', 'r')
s = f.read()
del_count = ast.literal_eval(s)
f.close()

def find_matches_rec(word, words_sofar, found_parses, max_splits):
	if len(word) == 0:
		return found_parses.append(words_sofar)
	if max_splits == 0:
		return found_parses
	for i in range(1, len(word)+1):
		prefix = word[:i]
		suffix = word[i:]
		if prefix in word_count:
			find_matches_rec(suffix, words_sofar+[prefix], found_parses, max_splits-1)
	return found_parses

def find_matches(word, max_splits):
	found_parses = find_matches_rec(word, [], [], max_splits)
	probabilities = [sum(map(lambda w: math.log(word_prob_dict[w]), x)) for x in found_parses]
	suggestions = zip(found_parses, probabilities)
	suggestions.sort(key=lambda x: x[1], reverse=True)
	return suggestions

# def find_matches(word, max_splits):
# 	threshold = 5.5
# 	suggestions = _find_matches(word, max_splits)
# 	print suggestions
# 	print suggestions[0]
# 	print suggestions[0][1]
# 	if len(suggestions) > 0:
# 		base = suggestions[0][1]
# 		for i in xrange(len(suggestions)):
# 			if suggestions[i][1] > base + threshold:
# 				break
# 		suggestions = suggestions[:i]


def possible_words_delete(word):
	edit_list = set([word])
	for i in range(len(word)):
		edit_list.add(word[0:i] + word[i+1:])
		for j in range(i, len(word)):
			edit_list.add(word[0:i] + word[i+1:j] + word[j+1:])
			# for k in range(j, len(word)):
			# 	edit_list.add(word[0:i] + word[i+1:j] + word[j+1:k] + word[k+1:])
	edit_list.discard('')
	return edit_list



def word_probability(word):
	return (word_count[word]+2.0 if word in word_count else 2.0)/total_word_count

def deletion_probability(s, w, b):
	return min((w * del_count[s] + b if s in del_count else b)/(bigram_count[s]+5.0 if s in bigram_count else 5.0), 1.0)

def insertion_probability(s, w, b):
	return min((w * add_count[s] + b if s in add_count else b)/(char_count[s[0]]+5.0 if s[0] in char_count else 5.0), 1.0)

# s is the incorrect character
def substitution_probability(s, t, w, b):
	return min((w * sub_count[s+t] + b if s+t in sub_count else b)/(char_count[t]+5.0 if t in char_count else 5.0), 1.0)

# s is the correct string
def transpose_probability(s, w, b):
	return min((w * rev_count[s] + b if s in rev_count else b)/(bigram_count[s]+5.0 if s in bigram_count else 5.0), 1.0)


# Ask if corrent == incorrent returns the maximum value (now with weights there are not probabilities)
# Hence I have made some changes
def edit_probability(correct, incorrect, w, b):
	if(correct == incorrect):
		return 1.0
	if len(correct) > len(incorrect):
		return deletion_probability(correct, w, b)
	elif len(correct) < len(incorrect):
		return insertion_probability(incorrect, w, b)
	elif len(correct) == len(incorrect) == 1:
		return substitution_probability(incorrect, correct, w, b)
	else:
		return transpose_probability(correct, w, b)

def get_candidates(query):
	candidates = set()
	query_derivatives = possible_words_delete(query)
	for w in query_derivatives:
		if w in modified_dict:
			candidates = candidates | modified_dict[w]
	return candidates

def word_dis(query, word, w, b):
	len_q = len(query)
	len_w = len(word)
	edit_mat = [[0.0 for j in xrange(len_q + 1)] for i in xrange(len_w + 1)]
	edit_mat[0][0] = 1.0
	for i in xrange(1, len_w + 1):
		edit_mat[i][0] = edit_probability('#', '#' + word[i-1], w, b) * edit_mat[i-1][0]
	edit_mat[0][1] = edit_probability('#' + query[0], '#', w, b)
	for j in xrange(2, len_q + 1):
		edit_mat[0][j] = edit_probability(query[j-2:j], query[j-2:j-1], w, b) * edit_mat[0][j-1]
	for i in xrange(1, len_w + 1):
		for j in xrange(1, len_q + 1):
			edit_mat[i][j] = edit_probability(query[j-1], word[i-1], w, b) * edit_mat[i-1][j-1]
			edit_mat[i][j] = edit_mat[i][j] + edit_probability(query[j-1], query[j-1] + word[i-1], w, b) * edit_mat[i-1][j] 
			edit_mat[i][j] = edit_mat[i][j] + edit_probability(word[i-1] + query[j-1], word[i-1], w, b) * edit_mat[i][j-1]
			edit_mat[i][j] = edit_mat[i][j] + (edit_probability(query[j-2] + query[j-1], word[i-2] + word[i-1], w, b) * edit_mat[i-2][j-2] if( (j-1 > 0) and (i-1 > 0) and (query[j-2] + query[j-1] == word[i-1] + word[i-2])) else 0)
	return (edit_mat[len_w][len_q])


def tot_prob(query, word, w, b, lda):
	return math.log(word_probability(word)) * lda +  math.log(word_dis(query, word, w, b))

def tot_prob2(query, word, w, b, lda):
	return math.log(word_probability(word)) +  math.log(word_dis(query, word, w, b))

def get_best_replacements(query, w, b, lda, n = 100):
	return sorted(list(get_candidates(query)), key = lambda x : tot_prob(query, x, w, b, lda), reverse = True)[:n]




# S = ['likethis', 'wickedwizard', 'liquidweather', 'driveourtrucks', 'gocompact', 'slimprojector', 'farsidebag']
# for s in S:
# 	for c, p in find_matches(s, 3):
# 		print c, p
# 	print '\n'



w = 0.5
b = 20
lda = 1.5
no_can = 10
no_can1 = 3
maxlim = 10

single_letter_penalty = 10
double_letter_penalty = 5
single_letter = ['f', 'l', 'e', 'u', 'y', 'n', 'g', 'w', 'p', 'b', 'r', 'k', 'd', 't', 'm', 'v', 'o', 'h', 'x', 'q', 'j', 'c', 'z']
double_letter = ['ib', 'fw', 'ol', 'qt', 'ot', 'ft', 'fa', 'vx', 'gk', 'sp', 'st', 'sv', 'qi', 'tt', 'tl', 'tj', 'lr', 'hu', 'hj', 'hl', 'eh', 'fb', 'ac', 'ae', 'ag', 'af', 'ah', 'ak', 'ao', 'aq', 'ap', 'ar', 'au', 'aw', 'ax', 'bd', 'bf', 'ba', 'bb', 'bc', 'bo', 'bi', 'bj', 'bk', 'bt', 'bu', 'bv', 'bs', 'ck', 'cj', 'ch', 'cn', 'cm', 'cl', 'cc', 'cb', 'cg', 'cf', 'ce', 'cd', 'cy', 'cs', 'cr', 'cp', 'cu', 'ct', 'ir', 'iu', 'ic', 'dl', 'dj', 'dh', 'di', 'db', 'dv', 'dw', 'dt', 'du', 'ds', 'dp', 'em', 'en', 'ej', 'ee', 'eg', 'ea', 'ec', 'eb', 'ex', 'eu', 'et', 'ew', 'es', 'er', 'vc', 'mb', 'vf', 'mm', 'vp', 'vu', 'vw', 'fp', 'fr', 'fs', 'fu', 'fx', 'fy', 'fe', 'fg', 'fi', 'fl', 'fm', 'gw', 'gt', 'gs', 'gr', 'gq', 'gp', 'ge', 'gc', 'ga', 'gm', 'gl', 'gi', 'hz', 'hr', 'hs', 'hq', 'hw', 'ht', 'ho', 'hm', 'hb', 'hc', 'ha', 'hg', 'hd', 'ix', 'iq', 'ip', 'iv', 'ii', 'ik', 'im', 'io', 'ia', 'ie', 'id', 'ig', 'jt', 'ju', 'jv', 'jw', 'jp', 'jq', 'jr', 'jm', 'jo', 'jj', 'jk', 'jd', 'je', 'jb', 'ji', 'jc', 'wr', 'kc', 'kb', 'ka', 'kg', 'ke', 'kd', 'kj', 'ki', 'ks', 'ku', 'lg', 'le', 'lb', 'lc', 'la', 'lo', 'll', 'lm', 'lj', 'lh', 'lt', 'lu', 'lp', 'lx', 'ly', 'wc', 'wv', 'md', 'mc', 'ml', 'mo', 'mi', 'mu', 'mw', 'mp', 'mx', 'ld', 'nj', 'nl', 'nc', 'nd', 'ne', 'ny', 'np', 'nr', 'ns', 'nu', 'nv', 'li', 'oj', 'oc', 'ob', 'ox', 'ou', 'os', 'op', 'og', 'pr', 'pv', 'pt', 'pa', 'pf', 'pg', 'pd', 'pe', 'pk', 'ph', 'pi', 'pn', 'pl', 'pm', 'oy', 'qu', 'qx', 'qb', 'qm', 'wt', 'xm', 'xp', 'rt', 'ru', 'rv', 'rw', 'rr', 'rs', 'rx', 'ry', 'rd', 're', 'rf', 'ra', 'rb', 'rc', 'rl', 'rn', 'ro', 'rh', 'ri', 'rj', 'ss', 'sw', 'su', 'si', 'sh', 'sn', 'sm', 'sc', 'sb', 'sa', 'sf', 'se', 'sd', 'ty', 'tu', 'tr', 'tm', 'tk', 'th', 'ti', 'td', 'te', 'tb', 'tc', 'ta', 'sr', 'sl', 'jg', 'ja', 'ut', 'uw', 'ur', 'um', 'ui', 'uh', 'uc', 'zz', 'lf', 'va', 've', 'vi', 'vo', 'vr', 'wb', 'wa', 'wj', 'wi', 'wh', 'ww', 'wu', 'ep', 'xi', 'xl', 'xy', 'xv', 'xt', 'yu', 'yt', 'yo', 'ye', 'pu', 'xu', 'mf', 'mh', 'mk', 'ci', 'cw', 'aa', 'ab', 'aj', 'ps', 'px', 'nh', 'ni', 'nm', 'nw', 'js', 'mj', 'bg', 'oa', 'oz', 'hf', 'qe', 'bm', 'br', 'xo', 'il', 'cv', 'pj', 'po', 'pp', 'pq', 'da', 'qd']

# merger
def merger(word, w, b, lda, no_can, no_can1):
	# threshold
	thr = 0.0
	factor = 1.0

	replacement_word = get_best_replacements(word, w, b, lda, no_can)
	word_prob = []
	word_prob_with_lda = []
	for candidate_word in replacement_word:
		word_prob.append(tot_prob2(word, candidate_word, w, b, lda))
		word_prob_with_lda.append(tot_prob(word, candidate_word, w, b, lda))

	final_word_list = zip(map(lambda x:[x], replacement_word), word_prob_with_lda)
	final_word_list = sorted(final_word_list, key = lambda x: x[1], reverse = True)

	# print word_list
	# print
	phrases_list = find_matches(word, no_can1)[:maxlim]
	phrases = map(lambda x:x[0], phrases_list)
	phrases_prob = map(lambda x:x[1], phrases_list)
	# print phrases

	p = 0
	while(p < len(replacement_word)):
		if word == replacement_word[p]:
			break
		p = p + 1

	p = p if p < len(replacement_word) else -1

	q = 0
	while(q < len(phrases)):
		if [word] == phrases[q]:
			break
		q = q + 1
	q = q if q < len(phrases) else -1


	if (p >= 0 and q >= 0):
		factor = word_prob[p]/phrases_prob[q]
		thr = 1.0
		phrases = phrases[:q] + phrases[q+1:]
		phrases_prob = phrases_prob[:q] + phrases_prob[q+1:]
	else:
		factor = 1
		thr = 4

	word_prob = map(lambda x: factor * x + thr, word_prob)

	for i in xrange(len(phrases)):
		for j in xrange(len(phrases[i])):
			if(phrases[i][j] in single_letter):
				phrases_prob[i] = phrases_prob[i] - single_letter_penalty
			elif(phrases[i][j] in double_letter):
				phrases_prob[i] = phrases_prob[i] - double_letter_penalty

	replacement_word = map(lambda x: [x], replacement_word)
	word_list = zip(replacement_word, word_prob)

	phrases_list = zip(phrases, phrases_prob)
	total_words = phrases_list + word_list
	total_words = sorted(total_words, key = lambda x: x[1], reverse = True)
	single_index_list = [i for i in xrange(len(total_words)) if len(total_words[i][0]) == 1]
	for i in xrange(len(single_index_list)):
		total_words[single_index_list[i]] = final_word_list[i]

	return total_words


def get_string(s):
	if(s == ''):
		return ''
	st = s[0]
	for w in s[1:]:
		st = st + ' ' + w
	return st

def has_special_characters(word):
	spl_characters = "@#$%^&*|\<=>/0123456789~`_+-"
	return any(map(lambda x: x in spl_characters, word))

def normalize_word(word):
	if has_special_characters(word):
		return ""
	else:
		return ''.join([w for w in word.lower() if w.isalpha()])


for word in sys.stdin:
	# TODO
	# Normalize the text
	# when I give enter and all it gives error.


	# if(word in modified_dict):
	# 	print modified_dict[word]
	# replacement_word = get_best_replacements(word, w, b, lda, no_can)
	# prob_list = []
	# for candidate_word in replacement_word:
	# 	prob_list.append(tot_prob2(word, candidate_word, w, b, lda))
	# word_list = zip(replacement_word, prob_list)
	# print word_list
	# print
	# phrases = find_matches(word, no_can1)
	# print phrases
	# print
	word = normalize_word(word)
	if word == '':
		continue
	corrections =  merger(word, w, b, lda, no_can, no_can1)
	corrections = corrections[:no_can]

	# print corrections
	print_string = word
	for x in corrections:
		print_string = print_string + '\t' + get_string(x[0]) + '\t' + str(x[1])
	print print_string

# ------------------
# Testing which w and b are the best

# f = open('Big_test_set', 'r')
# d = []
# count  = 0

# for l in f:
# 	tup = l.split()
# 	if tup[0].lower() not in word_count and tup[1].lower() in word_count:
# 		count = count + 1
# 		d.append((tup[0].lower(), tup[1].lower()))

# window = 5
# d = d[:]

# def get_score(w, b, lda, frame):
# 	count = 0
# 	score = 0.0
# 	for tup in d:
# 		candidates = get_best_replacements(tup[0], w, b, lda, frame)
# 		for i in xrange(len(candidates)):
# 			curr_score = 0.0
# 			if tup[1] == candidates[i]:
# 				curr_score = 1.0/(i+1)
# 				break
# 		if curr_score == 0.0:
# 			print tup[0], tup[1]
# 		score = curr_score + score
# 		if tup[1] in candidates[:window]:
# 			count = count + 1
# 	return (score/len(d), count)


# # l_w = [10**-2, 10**-1, 1, 10, 100]
# # l_b = [10**-2, 10**-1, 1, 10, 100]

# w = 0.5
# b = 20
# lda = 1.5

# frame = 10
# wb_list = []
# score_max = 0
# print get_score(w, b, lda, frame)

# score_mat = [[0 for i in xrange(len(l_b))] for j in xrange(len(l_w))]

# i = 0
# for w in l_w:
# 	j = 0
# 	for b in l_b:
# 		score = get_score(w, b, frame)
# 		if(score_max < score):
# 			score_max = score
# 			wb_list = [(w, b)]
# 		elif(score_max == score):
# 			wb_list.append((w, b))
# 		score_mat[i][j] = score
# 		j = j + 1
# 	i = i + 1


# print score_mat
# print score_max
# print wb_list