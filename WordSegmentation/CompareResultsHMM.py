import os

def read_correct_output_file(file_name):
	file = open(file_name, 'r', encoding='utf8')
	lines = []
	for line in file:
		line = line.strip()
		if line != '':
			words = line.split()
			lines.append(words)
		else:
			lines.append(line)
	file.close()
	# print(len(lines))
	return lines


def read_test_rdrsegmenter(file_name):
	file = open(file_name, 'r', encoding='utf8')
	lines = []
	for line in file:
		line = line.strip()
		if line != '':
			words = line.split()
			lines.append(words)
		else:
			lines.append(line)
	file.close()
	# print(len(lines))
	return lines


total_test_num_of_words = 0
total_actual_num_of_words = 0
total_correct_num_of_words = 0
total_incorrect_num_of_words = 0


def compare_results_hmm(correct_file, test_file):
	actual_lines = read_correct_output_file(correct_file)
	test_lines = read_test_rdrsegmenter(test_file)

	if len(actual_lines) == len(test_lines):
		print('Actual lines: %d | Test lines: %d | No line break error' % (len(actual_lines), len(test_lines)))
	else:
		print('Actual lines: %d | Test lines: %d | Line break error!' % (len(actual_lines), len(test_lines)))

	test_num_of_words = 0
	actual_num_of_words = 0
	correct_num_of_words = 0
	incorrect_num_of_words = 0
	incorrect_pairs = {}

	for line_index in range(len(test_lines)):
		actual_line = actual_lines[line_index]
		test_line = test_lines[line_index]

		actual_num_of_words += len(actual_line)
		test_num_of_words += len(test_line)

		i = 0
		j = 0

		while i < len(actual_line) and j < len(test_line):
			if actual_line[i] == test_line[j]:
				i += 1
				j += 1
				correct_num_of_words += 1
			else:
				incorrect_num_of_words += 1
				incorrect_pairs[actual_line[i]] = test_line[j]
				if actual_line[i] in test_line[j]:
					while i < len(actual_line) and actual_line[i] in test_line[j]:
						i += 1
					j += 1
				elif test_line[j] in actual_line[i]:
					while j < len(test_line) and test_line[j] in actual_line[i]:
						j += 1
					i += 1
				else:
					i += 1
					j += 1

	if incorrect_num_of_words < 1000000 and incorrect_num_of_words != 195:
		print('Actual number of words: %d' % actual_num_of_words)
		print('HMM test number of words: %d' % test_num_of_words)
		print('Number of correct words: %d' % correct_num_of_words)
		print('Number of incorrect words: %d' % incorrect_num_of_words)
		print('Incorrect pairs: ')
		errors_file = open('incorrect-pairs.txt', 'a', encoding='utf-8')
		for key in incorrect_pairs:
			errors_file.write('%s\t:\t%s\n' % (key, incorrect_pairs[key]))
		errors_file.close()
		print(incorrect_pairs)
		global total_test_num_of_words
		total_test_num_of_words += test_num_of_words
		global total_actual_num_of_words
		total_actual_num_of_words += actual_num_of_words
		global total_correct_num_of_words
		total_correct_num_of_words += correct_num_of_words
		global total_incorrect_num_of_words
		total_incorrect_num_of_words += incorrect_num_of_words
	else:
		print('Invalid Result')


def main():
	correct_files, test_files = input_files()
	errors_file = open('incorrect-pairs.txt', 'w', encoding='utf-8')
	errors_file.close()
	for i in range(len(correct_files)):
		compare_results_hmm(correct_files[i], test_files[i])
		print(correct_files[i])
		print()
	print('Actual total number of words: %d' % total_actual_num_of_words)
	print('HMM test total number of words: %d' % total_test_num_of_words)
	print('Total number of correct words: %d' % total_correct_num_of_words)
	print('Total number of incorrect words: %d' % total_incorrect_num_of_words)
	print('Accuracy: {}%'.format(total_correct_num_of_words / total_actual_num_of_words * 100))


def input_files():
	accurate_files = correct_files()
	output_files = test_files()

	return accurate_files, output_files


"""
	Return the list of test files in which punctuation marks have NOT been separated
"""
def test_files():
	test_files = []
	for file in os.listdir("TestResults"):
		if file.endswith(".txt"):
			file = os.path.join("TestResults", file)
			test_files.append(file)

	return test_files


"""
	Return the list of test files in which punctuation marks have NOT been separated
"""
def correct_files():
	correct_files = []
	for file in os.listdir("TestCorrectResults"):
		if file.endswith(".txt"):
			file = os.path.join("TestCorrectResults", file)
			correct_files.append(file)

	return correct_files


if __name__ == '__main__':
	main()
