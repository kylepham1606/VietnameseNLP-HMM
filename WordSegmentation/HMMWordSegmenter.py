import re
import json
from collections import defaultdict
import time

start_time = time.time()

# Load the HMM model with transition probabilities and emissions
with open('hmmmodel.txt', encoding='utf-8') as model_file:
	model_data = json.load(model_file)
	transition_probability = model_data["TP"]
	emission_boundary = model_data["EP"]


def read_sentences(file_name):
	file = open(file_name, 'rU', encoding='utf-8-sig')
	sentences = []
	for line in file:
		line = line.strip()
		if line == '':
			sentences.append('')
		else:
			sentences.extend(sentence_segment(line))
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


def bimorpheme_segment(sentence):
	sentence = sentence + ' '
	list_bimorphemes = []
	pattern = re.compile(r'(\s)|(\n)')
	# ([\.,!\?:;]*)
	eom = pattern.search(sentence)  # eom: end of morpheme
	last_pos = 0
	current_pos = eom.start() # if eom is not None else None  # eom.start() is the dot
	eom_next = pattern.search(sentence[current_pos+1:])
	next_pos = current_pos + eom_next.start() + 1 if eom_next is not None else None

	bimorpheme = sentence[last_pos:next_pos]
	list_bimorphemes.append(bimorpheme)

	while next_pos is not None:
		last_pos = current_pos
		current_pos = next_pos
		eom_next = pattern.search(sentence[current_pos+1:])
		next_pos = current_pos + eom_next.start() + 1 if eom_next is not None else None

		if next_pos is not None:
			bimorpheme = sentence[last_pos+1:next_pos]
			list_bimorphemes.append(bimorpheme)

	# print(list_bimorphemes)
	return list_bimorphemes


def nested_dict(n, type):
	if n == 1:
		return defaultdict(type)
	else:
		return defaultdict(lambda: nested_dict(n-1, type))

all_possible_states = ['B', 'C', '*']
b_or_c = ['B', 'C']

def viterbi(list_bimorphemes):
	probability = nested_dict(3, float)
	back_pointer = nested_dict(3, str)

	first_bimorpheme = list_bimorphemes[0]

	#### If the word is seen #####
	if first_bimorpheme in emission_boundary:
		probability['*']['B'][0] = transition_probability['*']['*']['B'] * emission_boundary[first_bimorpheme] * 10
		back_pointer['*']['B'][0] = '*'
		probability['*']['C'][0] = transition_probability['*']['*']['C'] * (1 - emission_boundary[first_bimorpheme]) * 10
		back_pointer['*']['C'][0] = '*'
	##### If the word is not seen #####
	else:
		print(first_bimorpheme)
		probability['*']['B'][0] = transition_probability['*']['*']['B'] * 10
		back_pointer['*']['B'][0] = '*'
		probability['*']['C'][0] = transition_probability['*']['*']['C'] * 10
		back_pointer['*']['C'][0] = '*'

	if len(list_bimorphemes) > 1:
		bimorpheme = list_bimorphemes[1]
		##### If the word is seen #####
		if bimorpheme in emission_boundary:
			max_value = -666
			current_back_pointer = ''
			for current_state in b_or_c:
				for previous_state_1 in b_or_c:
					probability_value = 0
					if current_state == 'B':
						probability_value = probability['*'][previous_state_1][0] * transition_probability['*'][previous_state_1]['B'] \
									 * emission_boundary[bimorpheme] * 10
					if current_state == 'C':
						probability_value = probability['*'][previous_state_1][0] * transition_probability['*'][previous_state_1]['C'] \
									 * (1 - emission_boundary[bimorpheme]) * 10
					if probability_value > max_value:
						max_value = probability_value
						current_back_pointer = '*'

					probability[previous_state_1][current_state][1] = max_value
					back_pointer[previous_state_1][current_state][1] = current_back_pointer

		##### If the word is not seen #####
		else:
			print(bimorpheme)
			for current_state in b_or_c:
				max_value = -666
				current_back_pointer = ''
				for previous_state_1 in b_or_c:
					probability_b_or_c = probability['*'][previous_state_1][0] * transition_probability['*'][previous_state_1][current_state] * 10
					if probability_b_or_c > max_value:
						max_value = probability_b_or_c
						current_back_pointer = '*'

					probability[previous_state_1][current_state][1] = max_value
					back_pointer[previous_state_1][current_state][1] = current_back_pointer

	index = 2

	while index < len(list_bimorphemes):
		bimorpheme = list_bimorphemes[index]
		##### If the word is seen #####
		if bimorpheme in emission_boundary:
			max_value = -666
			current_back_pointer = ''
			for current_state in b_or_c:
				for previous_state_1 in b_or_c:
					for previous_state_2 in b_or_c:
						probability_value = 0
						if current_state == 'B':
							probability_value = probability[previous_state_2][previous_state_1][index - 1] * transition_probability[previous_state_2][previous_state_1]['B'] \
										* emission_boundary[bimorpheme] * pow(10, 1)
						if current_state == 'C':
							probability_value = probability[previous_state_2][previous_state_1][index - 1] * transition_probability[previous_state_2][previous_state_1]['C'] \
										* (1 - emission_boundary[bimorpheme]) * pow(10, 1)
						if probability_value > max_value:
							max_value = probability_value
							current_back_pointer = previous_state_2

						probability[previous_state_1][current_state][index] = max_value
						back_pointer[previous_state_1][current_state][index] = current_back_pointer

		##### If the word is not seen #####
		else:
			print(bimorpheme)
			for state in b_or_c:
				max_value = -666
				current_back_pointer = ''
				for previous_state_1 in b_or_c:
					for previous_state_2 in b_or_c:
						probability_b_or_c = probability[previous_state_2][previous_state_1][index - 1] * transition_probability[previous_state_2][previous_state_1][state] * 10
						if probability_b_or_c > max_value:
							max_value = probability_b_or_c
							current_back_pointer = previous_state_2

						probability[previous_state_1][state][index] = max_value
						back_pointer[previous_state_1][state][index] = current_back_pointer

		index += 1

	##### Termination Step #####
	index = len(list_bimorphemes)
	state_sequence = list()

	max_possible_value = -666
	most_probable_state_1 = '*'
	most_probable_state_2 = '*'

	# If the sentence only has one bimorpheme
	if len(list_bimorphemes) == 1:
		for state_1 in b_or_c:
			if (index - 1) in probability['*'][state_1] and probability['*'][state_1][index - 1] > max_possible_value:
				# print('%s -> %s : %f' % (state_2, state_1, probability[state_2][state_1][index - 1]))
				max_possible_value = probability['*'][state_1][index - 1]
				most_probable_state_1 = state_1
				most_probable_state_2 = '*'
				state_sequence.append(most_probable_state_1)

	# If the sentence has at least two bimorphemes
	else:
		for state_1 in b_or_c:
			for state_2 in b_or_c:
				if (index - 1) in probability[state_2][state_1] and probability[state_2][state_1][
					index - 1] > max_possible_value:
					# print('%s -> %s : %f' % (state_2, state_1, probability[state_2][state_1][index - 1]))
					max_possible_value = probability[state_2][state_1][index - 1]
					most_probable_state_1 = state_1
					most_probable_state_2 = state_2
					state_sequence.append(most_probable_state_1)
					state_sequence.append(most_probable_state_2)


	counter = index - 3
	current_state = most_probable_state_1
	previous_state_1 = most_probable_state_2

	while counter >= 0:
		temp_previous_state_1 = back_pointer[previous_state_1][current_state][counter + 2]
		current_state = previous_state_1
		previous_state_1 = temp_previous_state_1
		counter -= 1
		state_sequence.append(previous_state_1)

	state_sequence.reverse()
	# print(state_sequence)
	return state_sequence


def segment_sentence(list_bimorphemes, state_sequence):
	segmented_sentence = ''
	state_position = 0
	if len(list_bimorphemes) == 0 or list_bimorphemes[0] == ' ':
		return ''
	for bimorpheme in list_bimorphemes:
		first_morpheme = bimorpheme.split()[0]
		if state_sequence[state_position] == '*':
			print('* state detected!')
		if state_sequence[state_position] == 'B':
			segmented_sentence += first_morpheme + ' '
		if state_sequence[state_position] == 'C':
			segmented_sentence += first_morpheme + '_'
		state_position += 1
	if len(list_bimorphemes[state_position - 1].split()) != 1:
		segmented_sentence += list_bimorphemes[state_position - 1].split()[1]

	return segmented_sentence


def write_on_file(sentences, file_name):
	file = open(file_name, 'w', encoding='utf-8')
	file.write('\n'.join(sentences))
	file.close()


def main():
	input_files = test_files()
	output_files = test_output_files()
	for file_index in range(len(input_files)):
		sentences = read_sentences(input_files[file_index])
		segmented_lines = []
		for sentence in sentences:
			if sentence == '':
				segmented_lines.append(sentence)
			else:
				list_bimorphemes = bimorpheme_segment(sentence)
				state_sequence = viterbi(list_bimorphemes)
				segmented_sentence = segment_sentence(list_bimorphemes, state_sequence)
				segmented_lines.append(segmented_sentence)
			write_on_file(segmented_lines, output_files[file_index])

	end_time = time.time()
	print('Time for word segmentation: %f' % ((end_time - start_time) * 1000))


def test_files():
	test_files = []

	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0001.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0002.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0003.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0004.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0005.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0006.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0007.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0008.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\10-0009.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110001.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110002.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110003.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110004.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110005.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110006.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110007.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110008.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\110009.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\140001.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\140002.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150001.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150002.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150003.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150004.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150005.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150006.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\150007.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700003.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700004.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700005.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700006.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\700007.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800011.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800012.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800013.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800014.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\800015.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900001.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900002.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900003.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900004.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900005.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900006.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900007.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900008.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900009.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900010.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900011.txt')
	test_files.append(
		'C:\\VTCC\\Test\\Vietnamese-word-segmentation-tool-master\\Vietnamese-word-segmentation-tool-master\\Datasets-Example\\Input\\900012.txt')

	return test_files


def test_output_files():
	output_files = []
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0001.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0002.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0003.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0004.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0005.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0006.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0007.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0008.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\10-0009.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110001.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110002.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110003.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110004.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110005.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110006.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110007.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110008.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\110009.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\140001.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\140002.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\150001.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\150002.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\150003.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\150004.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\150005.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\150006.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\150007.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\700003.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\700004.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\700005.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\700006.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\700007.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\800011.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\800012.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\800013.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\800014.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\800015.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900001.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900002.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900003.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900004.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900005.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900006.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900007.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900008.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900009.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900010.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900011.txt')
	output_files.append('C:\\Users\\phamp\\PycharmProjects\\WordSegmentation\\TestResults\\900012.txt')

	return output_files


if __name__ == '__main__':
	main()
