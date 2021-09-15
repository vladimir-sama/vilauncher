import os
import glob

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    os.chdir('..')
    file : str
    files = [file for file in glob.glob('**/**.py', recursive=True) if not file.startswith('utils')]
    total_lines = 0
    for py in files:
        with open(py) as file:
            total_lines = total_lines + len(file.readlines()) + 1
    print(len(files), 'files,', total_lines, 'lines total')
