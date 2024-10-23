# Intro

This is a chess opening trainer, which as of now supports 4 openings with each 5 lines.

After the openings are completed, stockfish takes over and plays against you at an elo of about 1300. 

For Stockfish to work tho, you need to insert the path to your own stockfish binary on your computer in the main.py file.

## Setup

Create a python venv with python 3.8 or 3.12, also use these version to run the programm. For reference I used version 3.8.20. on my ubuntu system. But on my macOS system I used 3.12.7, otherwise it didnt work for whatever reason. Also for Windows using uv as a version manager I was able to run my program with python version=3.9.20. So try these versions first.

then run: 'pip install -r requirements.txt'

to then start the programm run: 'python main.py' 