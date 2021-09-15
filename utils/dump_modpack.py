import os
import json
import string

def remove_chars(string_:str):
    for char in string.punctuation:
        string_ = string_.replace(char, '')
    return string_.replace(' ', '-')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    modpack_json : dict = {
        'name'     : '',
        'versions' : [],
        'modrinth' : [],
        'github'   : [],
        'modified' : 0
    }
    print('Welcome to VILauncher CLI modpack dumper!')
    name : str = input('Modpack name (single word) > ').strip()
    modpack_json['name'] = remove_chars(name) if name else 'default'
    modpack_json['versions'] = input('Supported Minecraft versions (space separated) > ').strip().split()
    print('For Modrinth and Github you can use the greater than sign (>) to mark precedence. Example (mod_id>other_mod_id)')
    modpack_json['modrinth'] = input('Modrinth mod ids (space separated) > ').strip().split()
    modpack_json['github']   = input('Github repo names (needs releases) (space separated) > ').strip().split()
    modpack_json['modified'] = int(input('Is modified (integer) (Vanilla 0) (Forge 1) (Fabric 2) > ').strip())
    with open(modpack_json['name'] + '.json', 'w') as file:
        json.dump(modpack_json, file)