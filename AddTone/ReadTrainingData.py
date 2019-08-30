import os
import json
import re


"""
	Merge all the text files for training and testing into a single text file
"""
def training_files():
	train_files = []
	for file_name in os.listdir("TrainingData"):
		if file_name.endswith(".txt"):
			file_name = os.path.join("TrainingData", file_name)
			train_files.append(file_name)

	with open('full-text-corpus.txt', 'w', encoding='utf-8') as file_out:
		for file_name in train_files:
			with open(file_name, 'rU', encoding='utf-8') as file_in:
				for line in file_in:
					file_out.write(line)
	file_out.close()


"""
	Merge all the dictionary files for training into a single text file
"""
def dictionary_files():
	dict_files = []
	for file_name in os.listdir("TrainingData\\LexiconForEmission"):
		if file_name.endswith(".txt"):
			file_name = os.path.join("TrainingData\\LexiconForEmission", file_name)
			dict_files.append(file_name)

	with open('full-lexicon.txt', 'w', encoding='utf-8') as file_out:
		for file_name in dict_files:
			with open(file_name, 'rU', encoding='utf-8') as file_in:
				for line in file_in:
					line = line.lower()
					file_out.write(line)
	file_out.close()


"""
	Read the lines (ignoring blanks), given a file, and return them in a list
"""
def read_lines(file_name):
	file = open(file_name, 'rU', encoding='utf-8-sig')
	lines = []
	for line in file:
		line = line.strip()
		if line == '':
			continue
		lines.extend(line.lower())
		# lines.extend(chunk_segment(line))
		# print(sentence_segment(line))
	return lines


"""
	Remove Vietnamese tone from a line
"""
def remove_tone(line):
	line = re.sub(r'[áàảãạăắằẳẵặâấầẩẫậ]', 'a', line)
	line = re.sub('đ', 'd', line)
	line = re.sub(r'[éèẻẽẹêếềểễệ]', 'e', line)
	line = re.sub(r'[íìỉĩị]', 'i', line)
	line = re.sub(r'[óòỏõọôốồổỗộơớờởỡợ]', 'o', line)
	line = re.sub(r'[úùủũụưứừửữự]', 'u', line)
	line = re.sub(r'[ýỳỷỹỵ]', 'y', line)

	return line


"""
	Main method to run the program
"""
def main():
	print(remove_tone('Nhà thằng trộm điện thoại bị cháy !!! Chết con mẹ mày đi !!!'))


""" 
	Run the program 
"""
if __name__ == '__main__':
	main()

