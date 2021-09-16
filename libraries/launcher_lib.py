import os
import sys
import json
import shutil
import platform
import requests
import subprocess
import minecraft_launcher_lib as mc_lib
from github import Github

library_name : str = 'VILauncher Library'
library_version : str = '0.05'

CODE_VANILLA : int = 0
CODE_FORGE : int   = 1
CODE_FABRIC : int  = 2

# GET FUNCTIONS

def get_java_exec(): # FIND JAVA EXECUTABLE
    return shutil.which('java')

def get_versions_online(show_snapshots:bool, show_old:bool): # LIST MINECRAFT VERSIONS WITH FILTER
    ls : list = []
    try:
        ls = mc_lib.utils.get_version_list()
    except:
        pass
    if not show_snapshots:
        ls = filter_snapshots(ls)
    if not show_old:
        ls = filter_old(ls)
    return ls

def get_versions_installed(mc_dir:str): # SHORTCUT
    try:
        return mc_lib.utils.get_installed_versions(mc_dir)
    except:
        pass
    return []

def get_account_types(): # GET AVAILABLE ACCOUNT TYPES
    return ['mojang', 'tlauncher']

# FILTERS

def is_valid_version(version:str, mc_dir:str): # SHORTCUT
    return mc_lib.utils.is_version_valid(version, mc_dir)

def filter_snapshots(version_list:list): # FILTER VERSIONS
    ls = []
    for version in version_list:
        if not 'rc' in version.get('id') and '.' in version.get('id') and not 'pre' in version.get('id').lower():
            ls.append(version)
    return ls
    
def filter_old(version_list:list): # FILTER VERSIONS
    ls = []
    for version in version_list:
        if not version.get('id').startswith('a') and not version.get('id').startswith('b') and not version.get('id').startswith('c'):
            ls.append(version)
    return ls

def ls_fabric_version(version_list:list): # LIST FABRIC VERSIONS FROM LIST
    fabric_list = []
    for version in version_list:
        if mc_lib.fabric.is_minecraft_version_supported(version):
            fabric_list.append(version)
    return fabric_list

def ls_forge_version(version_list:list): # LIST FORGE VERSIONS FROM LIST
    forge_list = []
    for version in version_list:
        if mc_lib.forge.find_forge_version(version):
            forge_list.append(version)
    return forge_list

# MINECRAFT LAUNCH

def get_natives_string(lib:dict): # IDK
    arch = '64'

    natives_file=''
    if not 'natives' in lib:
        return natives_file

    if 'windows' in lib['natives'] and platform.system() == 'Windows':
        natives_file = lib['natives']['windows'].replace('${arch}', arch)
    elif 'osx' in lib['natives'] and platform.system() == 'Darwin':
        natives_file = lib['natives']['osx'].replace('${arch}', arch)
    elif 'linux' in lib['natives'] and platform.system() == 'Linux':
        natives_file = lib['natives']['linux'].replace('${arch}', arch)

    return natives_file

def rule_says_yes(rule:dict):
    use_lib = None
    if rule['action'] == 'allow':
        use_lib = False
    elif rule['action'] == 'disallow':
        use_lib = True

    if 'os' in rule:
        for key, value in rule['os'].items():
            os = platform.system()
            if key == 'name':
                if value == 'windows' and not os == 'Windows':
                    return use_lib
                elif value == 'osx' and not os == 'Darwin':
                    return use_lib
                elif value == 'linux' and not os == 'Linux':
                    return use_lib
            elif key == 'arch':
                if value == 'x86' and not platform.architecture()[0] == '32bit':
                    return use_lib

    return not use_lib

def should_use_library(lib:dict): # IDK
    if not 'rules' in lib:
        return True
    for rule in lib['rules']:
        if rule_says_yes(rule):
            return True
    return False

def get_classpath(lib:dict, mc_dir:str, callback:dict, user_type:str): # IDK
    cp = []

    mc_lib.install.install_libraries(lib, mc_dir, callback)

    for library in lib['libraries']:
        if not should_use_library(library):
            continue

        lib_domain, lib_name, lib_version = library['name'].split(':')
        
        jar_path = os.path.join(mc_dir, 'libraries', '/'.join(lib_domain.split('.')), lib_name, lib_version)
        if user_type == 'tlauncher':
            if 'patchy' in jar_path:
                cp.append(os.path.join(mc_dir, 'libraries', 'org', 'tlauncher', 'patchy', '1.2.3', 'patchy-1.2.3.jar'))
                continue
            elif 'authlib' in jar_path:
                cp.append(os.path.join(mc_dir, 'libraries', 'org', 'tlauncher', 'authlib', '2.0.28.1', 'authlib-2.0.28.1.jar'))
                continue
        native = get_natives_string(library)
        jar_file = lib_name + '-' + lib_version + '.jar'
        if native:
            jar_file = lib_name + '-' + lib_version + '-' + native + '.jar'

        cp.append(os.path.join(jar_path, jar_file))
    cp.append(os.path.join(mc_dir, 'versions', lib['id'], lib['id'] + '.jar'))

    return os.pathsep.join(cp)

def install_version(version:str, mc_dir:str, callback:dict, version_type:int, launcher_dir:str): # INSTALL VERSION VANILLA AND MODIFIED IF MODIFIED
    installed = [version_.get('id') for version_ in get_versions_installed(mc_dir)]
    version_formated : str = version
    if 'fabric' in version.lower():
        version_type = CODE_FABRIC
        version_formated = version.lstrip('Fabric ').split('-')[-1]
    elif 'forge' in version.lower():
        version_type = CODE_FORGE
        version_formated = version.lstrip('Forge ').split('-')[0]
    launch_version : str = version
    tl_skin_path : str = install_tl_skin(version_formated, mc_dir, version_type, callback, launcher_dir)

    modified_string = ''
    if not version_formated in installed:
        try:
            mc_lib.install.install_minecraft_version(version_formated, mc_dir, callback)
        except:
            pass
    if version_type == CODE_FABRIC:
        try:
            if mc_lib.fabric.is_minecraft_version_supported(version_formated):
                latest_loader = mc_lib.fabric.get_latest_loader_version()
                launch_version = 'fabric-loader-' + latest_loader + '-' + version_formated
                modified_string = ' + Fabric (' + latest_loader + ')'
                if not launch_version in installed:
                    mc_lib.fabric.install_fabric(version_formated, mc_dir, latest_loader, callback)
            else:
                return ['Fabric', 'This Fabric version (' + version_formated + ') is not supported']
        except:
            pass
    elif version_type == CODE_FORGE:
        try:
            forge_version = mc_lib.forge.find_forge_version(version_formated)
            launch_version = version_formated + '-forge-' + forge_version.split('-')[1]
            modified_string = ' + Forge (' + forge_version + ')'
            if mc_lib.forge.supports_automatic_install(forge_version):
                if not launch_version in installed:
                    mc_lib.forge.install_forge_version(forge_version, mc_dir, callback)
            else:
                return ['Forge', 'This Forge version (' + forge_version + ') does not support automatic install']
        except:
            pass
    if not launch_version in installed:
        return [[launch_version, tl_skin_path], 'Install', 'Minecraft version (' + version + ')' + modified_string + ' installed']
    return [[launch_version, tl_skin_path]]

def get_game_args(version_json:dict): # REMOVE UNNECESSARY GAME ARGUMENTS
    one_args = [arg for arg in version_json['arguments']['game'] if isinstance(arg, str)]
    dict_args = [arg for arg in version_json['arguments']['game'] if isinstance(arg, dict)]
    ignore_args = [
        '--username', '${auth_player_name}',
        '--version', '${version_name}',
        '--gameDir', '${game_directory}',
        '--assetsDir', '${assets_root}',
        '--assetIndex', '${assets_index_name}',
        '--uuid', '${auth_uuid}',
        '--accessToken', '${auth_access_token}',
        '--userType', '${user_type}',
        '--versionType', '${version_type}',
        '--width', '--demo'
    ]
    new_args = []
    for arg in dict_args:
        if 'value' in arg.keys():
            if isinstance(arg['value'], str):
                if not arg['value'] in ignore_args:
                    new_args.append(arg['value'])
            else:
                if not arg['value'][0] in ignore_args:
                    new_args = new_args + arg['value']
    for arg in one_args:
        if not arg in ignore_args:
            new_args.append(arg)
    return new_args
    
def launch(mc_dir:str, version:str, username:str, uuid:str, access_token:str, user_type:str, java_args:list, callback:dict, launcher_data:tuple): # LAUNCH MINECRAFT VERSION
    # CALL INSTALL VERSION AND INSTALL TLSKINCAPE BEFORE AS REQUIRED BEFORE THIS FUNCTION
    minecraft_dir : str = mc_dir
    default_jvm : list = [
        '-Djava.library.path=',
        '-Dminecraft.launcher.brand=',
        '-Dminecraft.launcher.version='
    ]
    client_json : dict = {}
    original_client_json : dict = {}
    original_inherit_json : dict = {}
    java_executable : str = get_java_exec()
    natives_dir : str = os.path.join(minecraft_dir, 'versions', version, 'natives')
    with open(os.path.join(minecraft_dir, 'versions', version, version + '.json')) as file:
        client_json = json.load(file)
        original_client_json = client_json.copy()
    asset_index : str = ''
    additional_args : list = [
        '-XX:+IgnoreUnrecognizedVMOptions',
        '-XX:+UnlockExperimentalVMOptions',
        '-Dfml.ignoreInvalidMinecraftCertificates=true',
        '-Dfml.ignorePatchDiscrepancies=true',
        '-Djava.net.preferIPv4Stack=true',
        '--add-exports=java.base/sun.security.util=ALL-UNNAMED',
        '--add-exports=jdk.naming.dns/com.sun.jndi.dns=java.naming',
        '--add-opens=java.base/java.util.jar=ALL-UNNAMED'
    ]
    
    if 'assetIndex' in client_json.keys():
        asset_index = client_json['assetIndex']['id']
    else:
        with open(os.path.join(minecraft_dir, 'versions', client_json['inheritsFrom'], client_json['inheritsFrom'] + '.json')) as file:
            inherit_json : dict = json.load(file)
            original_inherit_json = inherit_json.copy()
            asset_index = inherit_json['assetIndex']['id']
            inherit_json.update(client_json)
            client_json = inherit_json
            client_json['libraries'] = original_inherit_json['libraries'] + original_client_json['libraries']

    jvm_args : list = []
    if 'fabric' in client_json['id']:
        jvm_args.append('-DFabricMcEmu=net.minecraft.client.main.Main')

    class_path : str = get_classpath(client_json, minecraft_dir, callback, user_type)
    main_class : str = client_json['mainClass']
    version_type : str = client_json['type']

    game_args : list = ['--username', username, '--version', version, '--gameDir', minecraft_dir, '--assetsDir', os.path.join(minecraft_dir, 'assets'), '--assetIndex', asset_index, '--uuid', uuid, '--accessToken', access_token, '--userType', user_type, '--versionType', version_type]
        
    command : list = [java_executable] + java_args + jvm_args + additional_args
    command.extend([default_jvm[0] + natives_dir, default_jvm[1] + launcher_data[0], default_jvm[2] + launcher_data[1], '-cp', class_path, main_class])
    command.extend(game_args)
    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    return process

# TLAUNCHER

def install_tl_skin(version:str, mc_dir:str, version_type:int, callback:dict, launcher_dir:str): # INSTALL TLAUNCHER LIBRARIES AND MOD
    file_name : str = os.path.join(launcher_dir, 'json', 'tl.json')
    tl_json : dict = {}
    try:
        tl_json = requests.get('http://repo.tlauncher.org/update/downloads/libraries/org/tlauncher/authlib/libraries-1.7.json', headers={'user-agent': mc_lib.helper.get_user_agent()}).json()
        with open(file_name, 'w') as file:
            json.dump(tl_json, file)
    except:
        if not os.path.isfile(file_name):
            return ''
        with open(file_name) as file:
            tl_json = json.load(file)
    check_mods : list = tl_json['additionalMods']
    check_versions : list = tl_json['tlauncherSkinCapeVersion']
    libraries : list = tl_json['libraries']
    previous_index : int = 0
    callback.get('setMax', mc_lib.helper.empty)(len(libraries + check_mods))
    search : list = [version]
    exclude : list = ['optifine']
    if version_type == CODE_FABRIC:
        search.append('fabric')
    elif version_type == CODE_FORGE:
        search.append('forge')
    else:
        exclude.append('fabric')
        exclude.append('forge')
    for index, lib in enumerate(libraries):
        supported : bool = True
        if 'supports' in lib.keys():
            found : bool = False
            for version_ in lib['supports']:
                should_continue : bool = False
                for term in search:
                    if not term in version_.lower():
                        should_continue = True
                for term in exclude:
                    if term in version_.lower():
                        should_continue = True
                if should_continue:
                    previous_index = index
                    callback.get('setProgress', mc_lib.helper.empty)(index)
                    continue
                found = True
            if not found:
                supported = False
        if supported:
            full_path_lib : str = os.path.join(mc_dir, 'libraries', lib['artifact']['path'])
            try:
                mc_lib.helper.download_file(lib['artifact']['url'], full_path_lib, {}, lib['artifact']['sha1'])
            except:
                pass
        previous_index = index
        callback.get('setProgress', mc_lib.helper.empty)(index)
    found_version : str = ''
    for mod in check_versions:
        should_continue : bool = False
        for term in search:
            if not term in mod.lower():
                should_continue = True
        for term in exclude:
            if term in mod.lower():
                should_continue = True
        if should_continue:
            continue
        found_version = mod
        break
    if not found_version:
        return ''
    for index, mod in enumerate(check_mods):
        if not found_version in mod['supports']:
            callback.get('setProgress', mc_lib.helper.empty)(previous_index + index)
            continue
        full_path : str = os.path.join(mc_dir, 'libraries', mod['artifact']['path'])
        try:
            mc_lib.helper.download_file(mod['artifact']['url'], full_path, {}, mod['artifact']['sha1'])
        except:
            pass
        callback.get('setProgress', mc_lib.helper.empty)(len(libraries + check_mods))
        return full_path
    return ''

# MODPACKS

def apply_modpack(mc_dir:str, modpack_dir:str, modpack:str, remove:bool): # CHANGES MODPACK
    if remove: # REMOVES MODPACK AND RESTORES TEMP MOD DIR
        if os.path.isdir(os.path.join(mc_dir, 'mods')):
            os.rename(os.path.join(mc_dir, 'mods'), os.path.join(mc_dir, modpack))
            shutil.move(os.path.join(mc_dir, modpack), modpack_dir)

        if os.path.isdir(os.path.join(mc_dir, 'temp_mods')):
            os.rename(os.path.join(mc_dir, 'temp_mods'), os.path.join(mc_dir, 'mods'))
    else: # MOVES CURRENT MODS TO TEMP DIR AND APPLIES MODPACK
        if os.path.isdir(os.path.join(mc_dir, 'mods')):
            os.rename(os.path.join(mc_dir, 'mods'), os.path.join(mc_dir, 'temp_mods'))

        if os.path.isdir(os.path.join(modpack_dir, modpack)):
            shutil.move(os.path.join(modpack_dir, modpack), mc_dir)
            os.rename(os.path.join(mc_dir, modpack), os.path.join(mc_dir, 'mods'))

def download_modpack(modlist:dict, download_dir:str, version_formated:str, callback:dict, github_token:str): # DOWNLOADS A VILAUNCHER MODPACK RETURNS SUCCESS
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)
    modrinth_list : list = modlist['modrinth']
    github_list : list = modlist['github']
    if len(os.listdir(download_dir)) >= len(modrinth_list + github_list):
        return True
    callback.get('setMax', mc_lib.helper.empty)(len(modrinth_list + github_list))
    previous_index : int = 0
    for index, mod_id in enumerate(modrinth_list):
        final : dict = find_modrinth(mod_id, version_formated)
        if not final:
            return False
        if not download_modrinth_mod(final, download_dir):
            return False
        callback.get('setProgress', mc_lib.helper.empty)(index)
        previous_index = index
    for index, mod_info in enumerate(github_list):
        final : tuple = find_github(mod_info[0], github_token, mod_info[1])
        if not final:
            return False
        if not download_github(final[0], os.path.join(download_dir, final[1]), final[2]):
            return False
        callback.get('setProgress', mc_lib.helper.empty)(previous_index + index)
    return True

# GITHUB

def find_github(repo_string:str, token:str, strings:list): # HELPER DOWNLOAD MODPACK
    git = Github(token)
    for n_repo in repo_string.split('>'):
        repo = git.get_repo(n_repo)
        for release in repo.get_releases():
            for asset in release.get_assets():
                asset_name = asset.name
                if all(string in asset_name for string in strings):
                    return (asset.url, asset_name, asset.raw_headers)
    return ()

def download_github(url:str, destination:str, headers:dict): # HELPER DOWNLOAD MODPACK
    return download_file(url, destination, '', headers)

# MODRINTH

def find_modrinth(mod_id_unformated:str, version_formated:str): # HELPER DOWNLOAD MODPACK
    for mod_id in mod_id_unformated.split('>'):
        mod : dict = {}
        try:
            mod = requests.get('https://api.modrinth.com/api/v1/mod/' + mod_id).json()
        except:
            continue
        candidates : list = []
        for version in mod['versions']:
            version_info : dict = {}
            try:
                version_info = requests.get('https://api.modrinth.com/api/v1/version/' + version).json()
            except:
                continue
            if 'fabric' in version_info['loaders']:
                if version_formated in version_info['game_versions']:
                    candidates.append(version_info)
        final : dict = {}
        if candidates:
            final = candidates[0]
        for version in candidates:
            date : list = version['date_published'][:10].split('-')
            if int(date[0]) > int(final['date_published'][:10].split('-')[0]):
                final = version
            elif int(date[0]) == int(final['date_published'][:10].split('-')[0]):
                if int(date[1]) > int(final['date_published'][:10].split('-')[1]):
                    final = version
                elif int(date[1]) == int(final['date_published'][:10].split('-')[1]):
                    if int(date[2]) >= int(final['date_published'][:10].split('-')[2]):
                        final = version
        if final:
            return final
    return {}

def download_modrinth_mod(version_json:dict, download_dir:str): # HELPER DOWNLOAD MODPACK
    destination : str = os.path.join(download_dir, version_json['files'][0]['filename'])
    if os.path.isfile(destination):
        return destination
    try:
        mc_lib.helper.download_file(version_json['files'][0]['url'], destination, {}, version_json['files'][0]['hashes']['sha1'])
    except:
        return ''
    return destination

# Utils

def set_ram(minimum_ram:int, maximum_ram:int, scale:str): # HELPER GET RAM ARGUMENT
    return ['-Xms' + str(minimum_ram) + scale, '-Xmx' + str(maximum_ram) + scale]

def download_file(url:str, path:str, sha1:str, headers:dict): # HELPER REPLACEMENT
    if os.path.isfile(path):
        if not sha1:
            return False
        elif get_sha1_hash(path) == sha1:
            return False
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass
    if not url.startswith('http'):
        return False
    request = requests.get(url, stream=True, headers=headers)
    if not request.status_code == 200:
        return False
    with open(path, 'wb') as file:
        request.raw.decode_content = True
        shutil.copyfileobj(request.raw, file)
    return True


if __name__ == '__main__':
    print(get_java_exec())
    