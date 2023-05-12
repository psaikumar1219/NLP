Please find instructions below to run the Code.

Open command prompt and move to the directory where Code.py file is present.

Execute below command to execute the code:

Command: python Code.py "<Path to Data folder (where train/test/dev files are present)>" "<Path to a destination folder where output files need to be stored>"

Example: python Code.py ./data/ ./Output/

Note for two path arguments:
1. Include "/" at the end of Path to the input data folder.
2. Include "/" at the end of Path to the destination folder.

Input folder Structure:

Data:
---> train
---> test
---> dev

After execution of the program. Destination path should contain following files:

Output:
---> greedy.out
---> viterbi.out
---> hmm.json
---> vocab.txt
