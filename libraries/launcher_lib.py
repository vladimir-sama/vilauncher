import os
import sys
import json
import shutil
import platform
import requests
import subprocess
import minecraft_launcher_lib as mc_lib
from github import Github

launcher_name = 'VILauncher'
launcher_version = '0.04'

CODE_VANILLA = 0
CODE_FORGE   = 1
CODE_FABRIC  = 2
FILTER_INSTALLED = 0
FILTER_VANILLA   = 1
FILTER_FABRIC    = 2
FILTER_IMPALER   = 3

# GET FUNCTIONS

def get_java_exec():
    return shutil.which('java')

def get_versions_legacy():
    return os.listdir(os.path.join(mc_lib.utils.get_minecraft_directory(), 'versions'))

def get_versions_online(show_snapshots:bool, show_old:bool):
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

def get_versions_installed(mc_dir:str):
    return mc_lib.utils.get_installed_versions(mc_dir)

def get_versions_impaler():
    online_versions : list = [version.get('id') for version in get_versions_online(False, False)]
    try:
        return online_versions[:online_versions.index('1.16.5') + 1]
    except:
        pass
    return online_versions

def get_filters():
    return [
        'Installed',
        'Vanilla',
        'Fabric',
        'Impaler'
    ]

def get_account_types():
    return ['mojang', 'tlauncher']

# FILTERS

def is_valid_version(version:str, mc_dir:str):
    return mc_lib.utils.is_version_valid(version, mc_dir)

def filter_snapshots(version_list:list):
    ls = []
    for version in version_list:
        if not 'rc' in version.get('id') and '.' in version.get('id') and not 'pre' in version.get('id').lower():
            ls.append(version)
    return ls
    
def filter_old(version_list:list):
    ls = []
    for version in version_list:
        if not version.get('id').startswith('a') and not version.get('id').startswith('b') and not version.get('id').startswith('c'):
            ls.append(version)
    return ls

def ls_fabric_version(version_list:list):
    fabric_list = []
    for version in version_list:
        if mc_lib.fabric.is_minecraft_version_supported(version):
            fabric_list.append(version)
    return fabric_list

def ls_forge_version(version_list:list):
    forge_list = []
    for version in version_list:
        if mc_lib.forge.find_forge_version(version):
            forge_list.append(version)
    return forge_list

# MINECRAFT LAUNCH

def get_natives_string(lib:dict):
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

def should_use_library(lib:dict):
    if not 'rules' in lib:
        return True
    for rule in lib['rules']:
        if rule_says_yes(rule):
            return True
    return False

def get_classpath(lib:dict, mc_dir:str, callback:dict, user_type:str):
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

def install_version(version:str, mc_dir:str, callback:dict, version_type:int, launcher_dir:str):
    installed = [version_.get('id') for version_ in get_versions_installed(mc_dir)]
    version_formated : str = version
    if 'fabric' in version.lower():
        version_type = CODE_FABRIC
        version_formated = version.lstrip('Fabric ').split('-')[-1]
    elif 'forge' in version.lower():
        version_type = CODE_FORGE
        version_formated = version.lstrip('Forge ').split('-')[0]
    launch_version : str = version
    tl_skin_path : str = install_tl_skin(version_formated, mc_dir, version_type, launcher_dir)

    modified_string = ''
    if not version_formated in installed:
        mc_lib.install.install_minecraft_version(version_formated, mc_dir, callback)
    if version_type == CODE_FABRIC:
        if mc_lib.fabric.is_minecraft_version_supported(version_formated):
            latest_loader = mc_lib.fabric.get_latest_loader_version()
            launch_version = 'fabric-loader-' + latest_loader + '-' + version_formated
            modified_string = ' + Fabric (' + latest_loader + ')'
            if not launch_version in installed:
                mc_lib.fabric.install_fabric(version_formated, mc_dir, latest_loader, callback)
        else:
            return ['Fabric', 'This Fabric version (' + version_formated + ') is not supported']
    elif version_type == CODE_FORGE:
        forge_version = mc_lib.forge.find_forge_version(version_formated)
        launch_version = version_formated + '-forge-' + forge_version.split('-')[1]
        modified_string = ' + Forge (' + forge_version + ')'
        if mc_lib.forge.supports_automatic_install(forge_version):
            if not launch_version in installed:
                mc_lib.forge.install_forge_version(forge_version, mc_dir, callback)
        else:
            return ['Forge', 'This Forge version (' + forge_version + ') does not support automatic install']
    if not launch_version in installed:
        return [[launch_version, tl_skin_path], 'Install', 'Minecraft version (' + version + ')' + modified_string + ' installed']
    return [[launch_version, tl_skin_path]]

def get_game_args(version_json:dict):
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
    
def launch(version:str, username:str, uuid:str, access_token:str, user_type:str, java_args:list, callback:dict):
    minecraft_dir : str = mc_lib.utils.get_minecraft_directory()
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
    game_args : list = []
    jvm_args : list = []
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
    if 'arguments' in client_json.keys():
        if 'jvm' in client_json['arguments'].keys():
            jvm_args = [arg for arg in client_json['arguments']['jvm'] if isinstance(arg, str)]
            jvm_args = [arg for arg in jvm_args if not any(arg.startswith(default) for default in default_jvm)]
            if jvm_args.count('-cp'):
                class_path_index : int = jvm_args.index('-cp')
                del jvm_args[class_path_index + 1]
                del jvm_args[class_path_index]
        if 'game' in client_json['arguments'].keys():
            game_args = get_game_args(client_json)
    class_path : str = get_classpath(client_json, minecraft_dir, callback, user_type)
    main_class : str = client_json['mainClass']
    version_type : str = client_json['type']
    if not user_type == get_account_types()[0]:
        user_type == get_account_types()[0]
        

    process = subprocess.Popen([java_executable] + java_args + additional_args + [default_jvm[0] + natives_dir, default_jvm[1] + launcher_name, default_jvm[2] + launcher_version, '-cp', class_path, main_class, '--username', username, '--version', version, '--gameDir', minecraft_dir, '--assetsDir', os.path.join(minecraft_dir, 'assets'), '--assetIndex', asset_index, '--uuid', uuid, '--accessToken', access_token, '--userType', user_type, '--versionType', version_type] + jvm_args + game_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    return process

# TLAUNCHER

def install_tl_skin(version:str, mc_dir:str, version_type:int, launcher_dir:str):
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
    search : list = [version]
    exclude : str = 'optifine'
    if version_type == CODE_FABRIC:
        search.append('fabric')
    elif version_type == CODE_FORGE:
        search.append('forge')
    else:
        return ''
    supported : bool = True
    for lib in libraries:
        if 'supports' in lib.keys():
            found : bool = False
            for version_ in lib['supports']:
                for term in search:
                    if not term in version_.lower():
                        continue
                if exclude in version_.lower():
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
    found_version : str = ''
    for mod in check_versions:
        for term in search:
            if not term in mod.lower():
                continue
        if exclude in mod.lower():
            continue
        found_version = mod
        break
    if not found_version:
        return ''
    search.append('tlskincape')
    for mod in check_mods:
        for term in search:
            if not term in mod['name']:
                continue
        if exclude in mod['name']:
            continue
        if not found_version in mod['supports']:
            return ''
        full_path : str = os.path.join(mc_dir, 'libraries', mod['artifact']['path'])
        try:
            mc_lib.helper.download_file(mod['artifact']['url'], full_path, {}, mod['artifact']['sha1'])
        except:
            pass
        return full_path
    return ''

# MODPACKS

def apply_modpack(mc_dir:str, modpack_dir:str, modpack:str, remove:bool):
    if remove:
        if os.path.isdir(os.path.join(mc_dir, 'mods')):
            os.rename(os.path.join(mc_dir, 'mods'), os.path.join(mc_dir, modpack))
            shutil.move(os.path.join(mc_dir, modpack), modpack_dir)

        if os.path.isdir(os.path.join(mc_dir, 'temp_mods')):
            os.rename(os.path.join(mc_dir, 'temp_mods'), os.path.join(mc_dir, 'mods'))
    else:
        if os.path.isdir(os.path.join(mc_dir, 'mods')):
            os.rename(os.path.join(mc_dir, 'mods'), os.path.join(mc_dir, 'temp_mods'))

        if os.path.isdir(os.path.join(modpack_dir, modpack)):
            shutil.move(os.path.join(modpack_dir, modpack), mc_dir)
            os.rename(os.path.join(mc_dir, modpack), os.path.join(mc_dir, 'mods'))

def get_impaler_mod_list():
    return {
        'modrinth': [
            'AZomiSrC', # Hydrogen
            'YL57xq9U', # Iris
            'gvQqBUqZ', # Lithium
            'P7dR8mSH', # Fabric API
            'mOgUt4GM', # Modmenu
            'Orvt0mRa', # Indium
            'yBW8D80W', # Dynamic Lights
            'H8CaAYZC>hEOCdOgW',
            # Starlight > Phosphor
            'fQEb0iXm', # Krypton
            '2Uev7LdA', # Better Grass
            'PtjYWJkn', # Sodium Extra
            'aXf2OSFU', # Zoomer
            'LQ3K71Q1', # Dynamic FPS
            'GNxdLCoP'  # Cull Leaves
        ],
        'github': []
    }

def download_modpack(modlist:dict, download_dir:str, version_formated:str, callback:dict, github_token:str):
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)
    if len(os.listdir(download_dir)) >= len():
        return True
    modrinth_list : list = modlist['modrinth']
    github_list : list = modlist['github']
    callback.get('setMax', mc_lib.helper.empty)(len(modrinth_list + github_list))
    previous_index : int = 0
    for index, mod_id in enumerate(modrinth_list):
        final : dict = find_modrinth(mod_id)
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

def find_github(repo:str, token:str, strings:list):
    git = Github(token)
    repo = git.get_repo(repo) # PaperMC/Starlight
    for release in repo.get_releases():
        for asset in release.get_assets():
            asset_name = asset.name
            if all(string in asset_name for string in strings):
                return (asset.url, asset_name, asset.raw_headers)
    return ()

def download_github(url:str, destination:str, headers:dict):
    return download_file(url, destination, '', headers)

# MODRINTH

def find_modrinth(mod_id_unformated:str):
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

def download_modrinth_mod(version_json:dict, download_dir:str):
    destination : str = os.path.join(download_dir, version_json['files'][0]['filename'])
    if os.path.isfile(destination):
        return destination
    try:
        mc_lib.helper.download_file(version_json['files'][0]['url'], destination, {}, version_json['files'][0]['hashes']['sha1'])
    except:
        return ''
    return destination

# Utils

def set_ram(minimum_ram:int, maximum_ram:int, scale:str):
    return ['-Xms' + str(minimum_ram) + scale, '-Xmx' + str(maximum_ram) + scale]

def download_file(url:str, path:str, sha1:str, headers:dict):
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
    pass
    