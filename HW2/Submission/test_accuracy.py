# Test greedy accuracy
dev_data = open('C:/Users/Sai Kumar Peddholla/Desktop/MS/2/NLP/Home Works/HW2/Question/data/dev','r')
greedy_output = open('greedy.out','r')

dev_lines = dev_data.readlines()
greedy_lines = greedy_output.readlines()

mis_match = 0
correct_match = 0
line_count = 0
for i in range(len(dev_lines)):
	dev_words = dev_lines[i][:-1].split("\t")
	greedy_words = greedy_lines[i][:-1].split("\t")

	if dev_words[0]!="" and greedy_words[0]!="":
		if dev_words[1]==greedy_words[1]:
			if dev_words[2]==greedy_words[2]:
				correct_match += 1
			else:
				mis_match += 1
		else:
			print("word mis_match",str(i))
			break
	elif dev_words[0]!="" and greedy_words[0]=="":
		print("line mis_match",str(i))
	elif dev_words[0]=="" and greedy_words[0]!="":
		print("line mis_match",str(i))
	else:
		line_count += 1

print(line_count)
print(correct_match/(mis_match+correct_match))
print(correct_match)
print(mis_match)
print(correct_match+mis_match)