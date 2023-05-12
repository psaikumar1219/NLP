import sys

number_of_arguments = len(sys.argv)

if number_of_arguments != 3:
	print("Please provide two arguments: ")
	print("1. Path to the input data folder where train/dev/test data are present. (Include / at the end)")
	print("2. Path to the destination folder to store output files. (Include / at the end)")
	print("Example: python Code.py ./data/ ./Output/")
	sys.exit()

input_folder_path = sys.argv[1]
output_folder_path = sys.argv[2]

if output_folder_path[len(output_folder_path)-1] != '/':
	print("Please include '/' at the end of Output path provided.")
	sys.exit()

# TASK 1 - Vocabulary Creation
# Creating vocabulary
import operator
try:
	train_data = open(input_folder_path + 'train','r')
except:
	print("Please check path provided. Trying to read file from path: " + str(input_folder_path + 'train'))
	sys.exit()

Lines = train_data.readlines()
vocabulary = {}
number_of_sentences = 1
for line in Lines:
	words = line[:-1].split("\t")
	if words[0]!="":
		word = words[1]
		tag = words[2]

		if word in vocabulary:
			vocabulary[word] += 1
		else:
			vocabulary[word] = 1
	else:
		number_of_sentences += 1

vocab_filter = {}
unknown_count = 0
unknown_word_set = set()
for word in vocabulary:
	if vocabulary[word]>3:
		vocab_filter[word] = vocabulary[word]
	else:
		unknown_count += vocabulary[word]
		unknown_word_set.add(word)

dictionary = dict( sorted(vocab_filter.items(), key=operator.itemgetter(1),reverse=True))

vocab_file = open(output_folder_path + 'vocab.txt','w')
index = 1
vocab_file.write(str("<unk>")+"\t"+str(index)+"\t"+str(unknown_count)+"\n")
unknown = "<unk>"
index += 1
for word in dictionary:
	vocab_file.write(str(word)+"\t"+str(index)+"\t"+str(dictionary[word])+"\n")
	index += 1
vocab_file.close()

print("Total size of vocabulary: "+ str(len(dictionary)))
print("Occurence of <unk> word: "+ str(unknown_count))


# TASK 2 - Model Learning
# Calculating emission probabilities
try:
	train_data = open(input_folder_path + 'train','r')
except:
	print("Please check path provided. Trying to read file from path: " + str(input_folder_path + 'train'))
	sys.exit()

emission_count = {}
tag_count = {}
Lines = train_data.readlines()
for line in Lines:
	words = line[:-1].split("\t")
	if words[0]!="":
		word = words[1]
		if word in unknown_word_set:
			word = unknown
		tag = words[2]

		key = tag + "~" + word
		if key in emission_count:
			emission_count[key] += 1
		else:
			emission_count[key] = 1

		if tag in tag_count:
			tag_count[tag] += 1
		else:
			tag_count[tag] = 1

emission = {}
for key in emission_count:
	numerator = emission_count[key]
	tag = key.split("~")[0]
	denominator = tag_count[tag]
	emission[key] = numerator/denominator


# Calculating transition probabilities
transition_count = {}
blank = "<blank>"
tag_count[blank] = number_of_sentences
prev_tag = blank
try:
	train_data = open(input_folder_path + 'train','r')
except:
	print("Please check path provided. Trying to read file from path: " + str(input_folder_path + 'train'))
	sys.exit()
Lines = train_data.readlines()

for line in Lines:
	words = line[:-1].split("\t")
	if words[0]!="":
		cur_tag = words[2]
		key = prev_tag + "~" + cur_tag
		prev_tag = cur_tag
		if key in transition_count:
			transition_count[key] += 1
		else:
			transition_count[key] = 1
	else:
		prev_tag = blank

transition = {}
for key in transition_count:
	numerator = transition_count[key]
	tag = key.split("~")[0]
	denominator = tag_count[tag]
	transition[key] = numerator/denominator


# Combining transition and emission paramters to a json and wiriting into a file as json object
import json

HMM_model = {}
HMM_model["transition"] = {}
HMM_model["emission"] = {}

for key in transition:
	states = key.split("~")
	prev_state = states[0]
	cur_state = states[1]
	new_key = "("+str(prev_state)+","+str(cur_state)+")"
	HMM_model["transition"][new_key] = transition[key]

for key in emission:
	states = key.split("~")
	prev_state = states[0]
	word = states[1]
	new_key = "("+str(prev_state)+","+str(word)+")"
	HMM_model["emission"][new_key] = emission[key]

hmm_model_json = json.dumps(HMM_model)

hmm_model_file = open(output_folder_path + 'hmm.json','w')
json.dump(hmm_model_json, hmm_model_file)
hmm_model_file.close()

print("Number of transition parameters: "+ str(len(transition)))
print("Number of emission parameters: "+ str(len(emission)))



# TASK 3 - Greedy Decoding with HMM
correct_match = 0
mis_match = 0

try:
	dev_data = open(input_folder_path + 'dev','r')
except:
	print("Please check path provided. Trying to read file from path: " + str(input_folder_path + 'dev'))
	sys.exit()

prev_tag = blank
index = 1
Lines = dev_data.readlines()
for line in Lines:
	words = line[:-1].split("\t")
	if words[0]!="":
		word = words[1]
		if word in unknown_word_set:
			word = unknown
		correct_tag = words[2]

		pred_prob = 0
		pred_tag = blank # check for update if all zeroes
		for cur_tag in tag_count:
			transition_key = prev_tag + "~" + cur_tag
			trans_prob = 0.0000000000001
			if transition_key in transition:
				trans_prob = transition[transition_key]
			
			emission_key = cur_tag + "~" + word
			emiss_prob = 0.0000000000001
			if emission_key in emission:
				emiss_prob = emission[emission_key]

			if emiss_prob*trans_prob > pred_prob:
				pred_prob = emiss_prob*trans_prob
				pred_tag = cur_tag

		if pred_tag == correct_tag:
			correct_match += 1
		else:
			mis_match += 1

		prev_tag = pred_tag
		index += 1
	else:
		index = 1
		prev_tag = blank


print("Greedy Algorithm accuracy: "+ str(correct_match/(correct_match+mis_match)))

try:
	test_data = open(input_folder_path + 'test','r')
except:
	print("Please check path provided. Trying to read file from path: " + str(input_folder_path + 'test'))
	sys.exit()

greedy_output = open(output_folder_path + 'greedy.out','w')

prev_tag = blank
probability_increase = 0
index = 1
Lines = test_data.readlines()
for line in Lines:
	words = line[:-1].split("\t")
	if words[0]!="":
		word = words[1]
		if word in unknown_word_set:
			word = unknown

		pred_prob = 0
		pred_tag = blank
		for cur_tag in tag_count:
			transition_key = prev_tag + "~" + cur_tag
			trans_prob = 0.0000000000001
			if transition_key in transition:
				trans_prob = transition[transition_key]
			
			emission_key = cur_tag + "~" + word
			emiss_prob = 0.0000000000001
			if emission_key in emission:
				emiss_prob = emission[emission_key]

			if emiss_prob*trans_prob > pred_prob:
				pred_prob = emiss_prob*trans_prob
				pred_tag = cur_tag

		greedy_output.write(str(index)+"\t"+str(word)+"\t"+str(pred_tag)+"\n")

		prev_tag = pred_tag
		index += 1
	else:
		greedy_output.write("\n")
		index = 1
		prev_tag = blank

greedy_output.close()


# TASK 4 - Viterbi Decoding with HMM
correct_match = 0
mis_match = 0

try:
	dev_data = open(input_folder_path + 'dev','r')
except:
	print("Please check path provided. Trying to read file from path: " + str(input_folder_path + 'dev'))
	sys.exit()


tag_index = {}
index = 0
blank_index = -1
dot_index = -1
for key in tag_count:
	if key == blank:
		blank_index = index
	if key == ".":
		dot_index = index
	tag_index[index] = key
	index += 1


words_array = []
correct_tag = []
Lines = dev_data.readlines()
for line in Lines:
	words = line[:-1].split("\t")
	if words[0]!="":
		if words[1] in unknown_word_set:
			words_array.append(unknown)
		else:
			words_array.append(words[1])
		correct_tag.append(words[2])
	else:
		dp = [[-1 for _ in range(len(words_array))] for _ in range(len(tag_count))]

		# Initialising first column
		for i in range(len(tag_count)):
			cur_tag = tag_index[i]
			transition_key = blank + "~" + cur_tag
			trans_prob = 0.0000000000001
			if transition_key in transition:
				trans_prob = transition[transition_key]
			
			emission_key = cur_tag + "~" + words_array[0]
			emiss_prob = 0.0000000000001
			if emission_key in emission:
				emiss_prob = emission[emission_key]

			dp[i][0] = trans_prob*emiss_prob

		# Filling the entire table
		for word_index in range(1,len(words_array)):
			cur_word = words_array[word_index]

			for i in range(len(tag_count)):
				cur_tag = tag_index[i]
				max_prob = 0
				emission_key = cur_tag + "~" + cur_word
				emiss_prob = 0.0000000000001
				if emission_key in emission:
					emiss_prob = emission[emission_key]

				for j in range(len(tag_count)):
					prev_tag = tag_index[j]

					transition_key = prev_tag + "~" + cur_tag
					trans_prob = 0.0000000000001
					if transition_key in transition:
						trans_prob = transition[transition_key]

					max_prob = max(max_prob, dp[j][word_index-1]*emiss_prob*trans_prob)

				dp[i][word_index] = max_prob

		predict_tag_array = []

		column = len(words_array) - 1
		next_tag = -1
		max_prob = 0
		for i in range(len(tag_count)):
			if max_prob < dp[i][column]:
				max_prob = dp[i][column]
				next_tag = i

		if next_tag == -1:
			next_tag = dot_index

		predict_tag_array.append(tag_index[next_tag])

		for column in range(len(words_array)-2,-1,-1):
			next_word = words_array[column+1]
			max_prev_tag = blank_index
			store_max_prob = max_prob
			diff = 1
			for i in range(len(tag_count)):
				prev_tag = i
				cur_prob = dp[i][column]

				if cur_prob != 0:
					transition_key = tag_index[prev_tag] + "~" + tag_index[next_tag]
					trans_prob = 0.0000000000001
					if transition_key in transition:
						trans_prob = transition[transition_key]
					
					
					emission_key = tag_index[next_tag] + "~" + next_word
					emiss_prob = 0.0000000000001
					if emission_key in emission:
						emiss_prob = emission[emission_key]

					if diff > abs(cur_prob*(trans_prob*emiss_prob) - max_prob):
						diff = abs(cur_prob*(trans_prob*emiss_prob) - max_prob)
						max_prev_tag = prev_tag
						store_max_prob = cur_prob
			
			next_tag = max_prev_tag
			max_prob = store_max_prob

			predict_tag_array.append(tag_index[max_prev_tag])

		predict_tag_array.reverse()

		if len(predict_tag_array) != len(correct_tag):
			print("Wrong length")
			print("Predicted length: " + str(len(predict_tag_array)))
			print("Correct length: " + str(len(correct_tag)))
			
		else:
			for k in range(len(predict_tag_array)):
				if predict_tag_array[k] == correct_tag[k]:
					correct_match += 1
				else:
					mis_match += 1

		words_array = []
		correct_tag = []

print("Vierbi Algorithm accuracy: "+ str(correct_match/(correct_match+mis_match)))


try:
	test_data = open(input_folder_path + 'test','r')
except:
	print("Please check path provided. Trying to read file from path: " + str(input_folder_path + 'test'))
	sys.exit()

viterbi_output = open(output_folder_path + 'viterbi.out','w')
words_array = []
count = 0
Lines = test_data.readlines()
for line in Lines:
	count += 1
	words = line[:-1].split("\t")
	if words[0]!="":
		if words[1] in unknown_word_set:
			words_array.append(unknown)
		else:
			words_array.append(words[1])
	else:
		dp = [[-1 for _ in range(len(words_array))] for _ in range(len(tag_count))]

		# Initialising first column
		for i in range(len(tag_count)):
			cur_tag = tag_index[i]
			transition_key = blank + "~" + cur_tag
			trans_prob = 0.0000000000001
			if transition_key in transition:
				trans_prob = transition[transition_key]
			
			emission_key = cur_tag + "~" + words_array[0]
			emiss_prob = 0.0000000000001
			if emission_key in emission:
				emiss_prob = emission[emission_key]

			dp[i][0] = trans_prob*emiss_prob

		# Filling the entire table
		for word_index in range(1,len(words_array)):
			cur_word = words_array[word_index]

			for i in range(len(tag_count)):
				cur_tag = tag_index[i]
				max_prob = 0
				emission_key = cur_tag + "~" + cur_word
				emiss_prob = 0.0000000000001
				if emission_key in emission:
					emiss_prob = emission[emission_key]

				for j in range(len(tag_count)):
					prev_tag = tag_index[j]

					transition_key = prev_tag + "~" + cur_tag
					trans_prob = 0.0000000000001
					if transition_key in transition:
						trans_prob = transition[transition_key]

					max_prob = max(max_prob, dp[j][word_index-1]*emiss_prob*trans_prob)

				dp[i][word_index] = max_prob

		predict_tag_array = []

		column = len(words_array) - 1
		next_tag = -1
		max_prob = 0
		for i in range(len(tag_count)):
			if max_prob < dp[i][column]:
				max_prob = dp[i][column]
				next_tag = i

		if next_tag == -1:
			next_tag = dot_index

		predict_tag_array.append(tag_index[next_tag])

		for column in range(len(words_array)-2,-1,-1):
			next_word = words_array[column+1]
			max_prev_tag = blank_index
			store_max_prob = max_prob
			diff = 1
			for i in range(len(tag_count)):
				prev_tag = i
				cur_prob = dp[i][column]

				if cur_prob != 0:
					transition_key = tag_index[prev_tag] + "~" + tag_index[next_tag]
					trans_prob = 0.0000000000001
					if transition_key in transition:
						trans_prob = transition[transition_key]
					
					
					emission_key = tag_index[next_tag] + "~" + next_word
					emiss_prob = 0.0000000000001
					if emission_key in emission:
						emiss_prob = emission[emission_key]

					if diff > abs(cur_prob*(trans_prob*emiss_prob) - max_prob):
						diff = abs(cur_prob*(trans_prob*emiss_prob) - max_prob)
						max_prev_tag = prev_tag
						store_max_prob = cur_prob
			
			next_tag = max_prev_tag
			max_prob = store_max_prob

			predict_tag_array.append(tag_index[max_prev_tag])

		predict_tag_array.reverse()

		for k in range(len(predict_tag_array)):
			viterbi_output.write(str(k+1)+"\t"+str(words_array[k])+"\t"+str(predict_tag_array[k])+"\n")

		# print("check")
		viterbi_output.write("\n")

		words_array = []

for k in range(len(predict_tag_array)):
	viterbi_output.write(str(k+1)+"\t"+str(words_array[k])+"\t"+str(predict_tag_array[k])+"\n")

viterbi_output.close()
