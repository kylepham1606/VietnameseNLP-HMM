import re
import json
from collections import defaultdict


def read_sentences(file_name):
	file = open(file_name, 'rU', encoding='utf-8-sig')
	sentences = []
	for line in file:
		line = line.strip()
		if line == '':
			continue
		sentences.extend(sentence_segment(line))
		# print(sentence_segment(line))
	return sentences


def sentence_segment(data):
	sentences = []
	# pattern: letter + punctuation mark
	pattern = re.compile(r'(\S\s([.?!]$))|(\S\s:\s[A-Z]$)')
	# r'([.;:?!])\s+([A-Z])'
	eos = pattern.search(data)  # eos : end of sentence
	last_pos = 0
	pos = eos.start() if eos is not None else None  # eos.start() is the dot
	if pos is None:
		sentences.append(data)
	while pos is not None:
		sentence = data[last_pos:pos + 3]
		sentences.append(sentence)
		last_pos = last_pos + eos.end() - 1 if eos is not None else None
		eos = pattern.search(data[last_pos:])
		pos = last_pos + eos.start() if eos is not None else None
	return sentences


boundary_counter = defaultdict(lambda: 0)
continuation_counter = defaultdict(lambda: 0)


def nested_dict(n, type):
	if n == 1:
		return defaultdict(type)
	else:
		return defaultdict(lambda: nested_dict(n-1, type))


state_sequence_counter = nested_dict(3, int)


def bimorpheme_segment(sentence):
	sentence = sentence + ' '
	pattern = re.compile(r'(\s)|(\n)|_')
	# ([\.,!\?:;]*)
	eom = pattern.search(sentence)  # eom: end of morpheme
	last_pos = 0
	current_pos = eom.start() # if eom is not None else None  # eom.start() is the dot
	eom_next = pattern.search(sentence[current_pos+1:])
	next_pos = current_pos + eom_next.start() + 1 if eom_next is not None else None

	last_state_2 = '*'
	last_state_1 = '*'

	if sentence[current_pos] == ' ' or sentence[current_pos] == '\n':
		bimorpheme = sentence[last_pos:next_pos]
		boundary_counter[bimorpheme] += 1

		current_state = 'B'
		state_sequence_counter[last_state_2][last_state_1][current_state] += 1

	else:
		bimorpheme = sentence[last_pos:current_pos] + " " + sentence[current_pos+1:next_pos]
		continuation_counter[bimorpheme] += 1

		current_state = 'C'
		state_sequence_counter[last_state_2][last_state_1][current_state] += 1

	while next_pos is not None:
		last_pos = current_pos
		current_pos = next_pos
		eom_next = pattern.search(sentence[current_pos+1:])
		next_pos = current_pos + eom_next.start() + 1 if eom_next is not None else None

		last_state_2 = last_state_1
		last_state_1 = current_state

		if next_pos is not None:
			if sentence[current_pos] == ' ' or sentence[current_pos] == '\n':
				bimorpheme = sentence[last_pos+1:next_pos]
				boundary_counter[bimorpheme] += 1

				current_state = 'B'
				state_sequence_counter[last_state_2][last_state_1][current_state] += 1
			else:
				bimorpheme = sentence[last_pos+1:current_pos] + " " + sentence[current_pos + 1:next_pos]
				continuation_counter[bimorpheme] += 1

				current_state = 'C'
				state_sequence_counter[last_state_2][last_state_1][current_state] += 1
	return


emission_boundary = {}


def calculate_emission():
	for key in boundary_counter:
		emission_boundary[key] = boundary_counter[key] / (boundary_counter[key] + continuation_counter[key])

	for key2 in continuation_counter:
		emission_boundary[key2] = boundary_counter[key2] / (boundary_counter[key2] + continuation_counter[key2])


transition_probability = nested_dict(3, float)


def calculate_transition_probability():
	number_of_sequences = 0
	for key1 in state_sequence_counter:
		for key2 in state_sequence_counter[key1]:
			for key3 in state_sequence_counter[key2]:
				number_of_sequences += state_sequence_counter[key1][key2][key3]

	for key1 in state_sequence_counter:
		for key2 in state_sequence_counter[key1]:
			for key3 in state_sequence_counter[key2]:
				transition_probability[key1][key2][key3] = state_sequence_counter[key1][key2][key3] / number_of_sequences


def main():
	train_files = training_files()
	for file in train_files:
		sentences = read_sentences(file)
		# print(sentences)
		for sentence in sentences:
			bimorpheme_segment(sentence)
	calculate_emission()
	# for key in emission_boundary:
	# 	print("%s : %f" % (key, emission_boundary[key]))
	calculate_transition_probability()
	for key1 in state_sequence_counter:
		for key2 in state_sequence_counter[key1]:
			for key3 in state_sequence_counter[key2]:
				print('%s -> %s -> %s : %f' % (key1, key2, key3, transition_probability[key1][key2][key3]))

	data_dump_directory = {"TP": transition_probability, "EP": emission_boundary}

	with open('hmmmodel.txt', 'w', encoding='utf8') as fp:
		json.dump(data_dump_directory, fp, ensure_ascii=False)
	pass


def training_files():
	train_files = []

	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0001.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0002.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0003.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0004.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0005.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0006.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0007.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0008.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0009.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110001.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110002.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110003.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110004.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110005.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110006.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110007.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110008.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110009.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\140001.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\140002.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150001.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150002.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150003.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150004.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150005.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150006.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150007.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700003.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700004.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700005.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700006.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700007.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800011.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800012.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800013.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800014.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800015.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900001.txt.WS')
	'''train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900002.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900003.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900004.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900005.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900006.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900007.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900008.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900009.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900010.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900011.txt.WS')
	train_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900012.txt.WS')'''

	return train_files


if __name__ == '__main__':
	main()