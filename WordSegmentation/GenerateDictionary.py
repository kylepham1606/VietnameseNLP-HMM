import re

input_file = open('idfs.popular', 'rU', encoding='utf-8')
output_file = open('dictionary2.txt', 'w', encoding='utf-8')

for line in input_file:
	pattern = re.compile(r'\t')
	pattern_2 = re.compile(r'[À-ưẠ-ỹ]')
	pattern_3 = re.compile(r'\t')
	# r'([.;:?!])\s+([A-Z])'
	eos = pattern.search(line)  # eos : end of sentence
	pos = eos.start() if eos is not None else None  # eos.start() is the dot
	if pos is not None:
		key = line[:pos]

		eos_2 = pattern_3.search(line[pos+1:])
		pos_2 = pos + 1 + eos_2.start()
		occurences = int(line[pos_2 + 1:])
		print(occurences)
		tone = pattern_2.search(key)

		if occurences > 30000 or tone is not None:
			output_file.write(key)
			output_file.write('\n')
			if 'qui' in key:
				output_file.write(re.sub('qui', 'quy', key))
				output_file.write('\n')
			if 'quí' in key:
				output_file.write(re.sub('quí', 'quý', key))
				output_file.write('\n')
			if 'quỉ' in key:
				output_file.write(re.sub('quỉ', 'quỷ', key))
				output_file.write('\n')
			if 'quĩ' in key:
				output_file.write(re.sub('quĩ', 'quỹ', key))
				output_file.write('\n')
			if 'quì' in key:
				output_file.write(re.sub('quì', 'quỳ', key))
				output_file.write('\n')
			if 'quị' in key:
				output_file.write(re.sub('quị', 'quỵ', key))
				output_file.write('\n')