import math
import ast
import sys

data_path = '../data/'

ngram_dict = {}
total_cooccurence_count = 0
f = open(data_path+'word_cooccurence_count.txt', 'r')
for l in f:
	word1, word2, count = l.split()
	count = int(count)
	ngram_dict[(word1, word2)] = count
	total_cooccurence_count += count
f.close()

onegram_dict = {}
total_onegram_count = 0
f = open(data_path+'word_count.txt', 'r')
for l in f:
	word, count = l.split()
	count = int(count)
	onegram_dict[word] = count
	total_onegram_count += count
f.close()

common_confusion_sets = []
f = open(data_path+'common_confusion_set.txt', 'r')
for l in f:
	common_confusion_sets.append(set(l.split(',')))
f.close()

word_count = {}
total_word_count = 0
f = open(data_path+'dictionary.txt', 'r')
for l in f:
	word = l.split()[0].lower()
	count = int(l.split()[1])
	word_count[word] = count
	total_word_count += count
f.close()

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

def possible_words_delete(word):
	edit_list = set([word])
	for i in range(len(word)):
		edit_list.add(word[0:i] + word[i+1:])
		for j in range(i, len(word)):
			edit_list.add(word[0:i] + word[i+1:j] + word[j+1:])
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

def get_edit_candidates(query):
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


def cooccurence_count(s, t):
	if (s, t) in ngram_dict:
		return ngram_dict[(s, t)]
	elif (t, s) in ngram_dict:
		return ngram_dict[(t, s)]
	else:
		return 0

def occurence_count(s):
	if s in onegram_dict:
		return onegram_dict[s]
	else:
		return 0

def word_prior_probability(word):
	return (occurence_count(word)+0.5)/total_onegram_count

# P(word1 | word2)
def cooccurence_probability(word1, word2):
	return (cooccurence_count(word1, word2)+10.0)/(occurence_count(word2)+10.0)

def context_posterior_log_probability(context, word):
	ans = 0.0
	for c in context:
		ans += math.log(0.7*cooccurence_probability(c, word) + 0.3*word_probability(c))
	return ans

def corruption_probability(replacement, corruption, w, b):
	if corruption not in word_count:
		return word_dis(corruption, replacement, w, b)
	else:
		for s in common_confusion_sets:
			if replacement in s:
				if corruption in s:
					return 1.0/(len(s))
				break
		return word_dis(corruption, replacement, w, b)
	return word_dis(corruption, replacement, w, b)

def total_log_probability(corruption, context, replacement, w, b):
	return 0.1*context_posterior_log_probability(context, replacement) + 0.65*math.log(word_probability(replacement)) + 0.25*math.log(corruption_probability(replacement, corruption, w, b))
	# return context_posterior_log_probability(context, replacement) + math.log(word_probability(replacement)) + math.log(corruption_probability(replacement, corruption, w, b))
	# return 0.6*context_posterior_log_probability(context, replacement) + 0.4*math.log(word_probability(replacement))

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

def get_all_candidates(word):
	t = set()
	for s in common_confusion_sets:
		if word in s:
			t = s.copy()
			break
	t = t | set(get_edit_candidates(word))
	t.discard(word)
	return t

def get_ranked_candidates(corruption, context, w, b):
	replacements = get_all_candidates(corruption)
	probabilities = map(lambda x : total_log_probability(corruption, context, x, w, b), replacements)
	return sorted(zip(replacements, probabilities), key = lambda x : x[1], reverse = True)

stop_words = set(['a','about','above','after','again','against','all','am','an','and','any','are','arent','as','at','be','because','been','before','being','below','between','both','but','by','cant','cannot','could','couldnt','did','didnt','do','does','doesnt','doing','dont','down','during','each','few','for','from','further','had','hadnt','has','hasnt','have','havent','having','he','hed','hell','hes','her','here','heres','hers','herself','him','himself','his','how','hows','i','id','ill','im','ive','if','in','into','is','isnt','it','its','its','itself','lets','me','more','most','mustnt','my','myself','no','nor','not','of','off','on','once','only','or','other','ought','our','ours','ourselves','out','over','own','same','shant','she','shed','shell','shes','should','shouldnt','so','some','such','than','that','thats','the','their','theirs','them','themselves','then','there','theres','these','they','theyd','theyll','theyre','theyve','this','those','through','to','too','under','until','up','very','was','wasnt','we','wed','well','were','weve','were','werent','what','whats','when','whens','where','wheres','which','while','who','whos','whom','why','whys','with','wont','would','wouldnt','you','youd','youll','youre','youve','your','yours','yourself','yourselves'])

for s in sys.stdin:
	ls = normalize_text(s)
	found = False
	for i in range(len(ls)):
		l = ls[i]
		if l not in word_count:
			found = True
			print l,
			for p in get_ranked_candidates(l, [x for x in ls[:i]+ls[i+1:] if x not in stop_words], 0.5, 20)[:3]:
				print '\t'+p[0]+'\t'+str(p[1]),
			print ''
			break
	if not found:
		replacements = []
		mean_score = []
		for i in range(len(ls)):
			l = ls[i]
			replacements.append(get_ranked_candidates(l, [x for x in ls[i-3:i]+ls[i+1:i+4] if x not in stop_words], 0.5, 20)[:3])
			mean_score.append(sum([r[1] for r in replacements[-1]])/len(replacements[-1]))
		index = max(range(len(ls)), key = lambda i : mean_score[i])
		print ls[index],
		for p in replacements[index]:
			print '\t'+p[0]+'\t'+str(p[1]),
		print ''