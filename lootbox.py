import json
import os
import random
import sys
import zipfile
import io
import math
# import yaml does not work with windows



"""
TODO:
    write some function to aid people ingame
    write some help, for not programmers
        write --help for python script
        write a popup in chat for help
        write something to disable popup
    write some helping inbetween steps
        2 output streams
            to log file of some sort
            to screen

comments are always pointing down
structure:
loot_table:pool
    pools:list -> pools
    pools -> pool
        pool:dict -> entries
        entries -> entry
            entry:dict
"""

# need "path" multiple times to keep the code readable
def get_paths2file(path):
    print("Getting filepaths...")
    file_list = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [dirname for dirname in dirnames if dirname not in excluded_dir] # for testing it excludes 'combined'
        for filename in filenames:
            file = os.path.join(dirpath, filename)
            file_list.append(file)
    return file_list    

def generate_loottables(filepath_list, box_count, isUnit):
    print("Generating lootboxes...")
    list_loot = collect_unitEntries(filepath_list)
    list_lootboxes = dist_into_boxes(list_loot,box_count,isUnit) 
    return list_lootboxes


def adjust_weight(list_entries):
    #for lootbox in list_lootbox:
        # new table has different total weight
    total = get_total_weights(list_entries,"weight")
    for entry in list_entries:
        frequency = entry["frequency"]
        # common item in origina table are now also common items in new table
        entry["weight"] = int(math.ceil(frequency * total)) # maybe this is the issue
        del entry["frequency"]

# set weight as percent of total, save old_weight for later
def add_freq_origin(list_entries):
    # for unitEntries in list_unitEntries:
    total = get_total_weights(list_entries,"weight")
    for entry in list_entries:
        if not "weight" in entry:
            entry["weight"] = 1
        weight = entry["weight"]
        entry["frequency"] = round(weight/total, 2)

# get total weight, for modification
def get_total_weights(list_entries, sum_over):
    total = 0
    for entry in list_entries:  
        if sum_over in entry:
            total = total + entry[sum_over]
        else:
            total = total + 1
            entry[sum_over] = 1
    return total

# naming somewhat bad, but in short it collect all the drops of a given table to a unit
def collect_unitEntries(filepath_list):
    list_unitEntries = []
    for file in filepath_list:
        list_unitEntries.append(collect_entries(file))
    return list_unitEntries

# there is definetly a better way to write this
def collect_entries(file):
    list_comp_entries = []
    sub_files = [file]
    # table can contain multiple tables themself
    while(sub_files):
        list_entries = []
        data = load_json(sub_files.pop(0))
        if not "pools" in data:
            continue
        pools = data["pools"]
        # tables have multiple pools
        for pool in pools:
            toadd_entries = list(pool["entries"])
            # and each pool can have multiple entries
            while(toadd_entries):
                entry = toadd_entries.pop(0)
                if "loot_table" in entry["type"]:
                    local_path = entry["name"]
                    local_path = local_path.removeprefix("minecraft:")
                    next_subfile = os.path.join('loot_tables',local_path + '.json')
                    sub_files.append(next_subfile)
                    # skip looking at other options, maybe there are cases where 
                    # such tables aso have children, where this may not be a good idea
                    continue
                # children can have also entries themself, and as such have to piped loop as well
                if "children" in entry:
                    list_children = entry["children"]
                    # extend the list untill there is no more entries
                    toadd_entries.extend(list_children)
                    continue
                # most functions are to specific and as such have to be removed
                remove_functions(entry)
                # no conditions in universal, as such has to be removed
                remove_conditions(entry)
                list_entries.append(entry)
        # weight have to be adjusted as ther result list can be comprised of multiple files
        add_freq_origin(list_entries)
        list_comp_entries.extend(list_entries)
    # new weights now represent how frequent these items are normaly dropped
    adjust_weight(list_comp_entries)
    # table is bound to be divid, frequency is proportional to origin, weight are as such adjusted
    add_freq_origin(list_comp_entries)
    return list_comp_entries

# just to shorten code
def load_json(source):
    if not os.path.exists(source):
        return {}   
    with open(source,'r') as source:
        data = json.load(source)
    return data

def remove_functions(entry):
    if not "functions" in entry:
        return
    functions = entry["functions"]
    # cant modify a collections while iterating through it
    for function in functions[:]:
        # most conditions are universily applicable, they are very specific, and as such can be put on any type
        if "conditions" in function:
            functions.remove(function)
            continue
        # blocks, chest, gameplay and arch can not be killed
        if "minecraft:looting_enchant" in function["function"]:
            functions.remove(function)
            continue
        # entities, chest, gameplay and arch do not stop nbt data
        if "minecraft:copy_name" in function["function"]:
            functions.remove(function)
            continue
        # same aplies from above
        if "minecraft:copy_nbt" in function["function"]:
            functions.remove(function)
            continue
        # same aplies from above
        if "minecraft:copy_state" in function["function"]:
            functions.remove(function)
            continue
        if "minecraft:apply_bonus" in function["function"]:
            functions.remove(function)
            continue
    if len(functions) == 0:
        del entry["functions"]

def remove_conditions(entry):
    if "conditions" in entry:
        del entry["conditions"]


def dist_into_boxes(list_loot, box_count,isUnit):
    count = len(list_loot)

    # option between unit or individual entries
    if isUnit:
        func = dist_unitEntries
    else:
        list_loot = unbox_2list_entries(list_loot)
        func = dist_entries

    # lootboxes need to be filled with at least one element
    # this is also the reason files cannot be read and written at the same time
    if(box_count > count):
        box_count = count
    list_lootboxes = [[] for _ in range(box_count)]

    index = 0
    while(list_loot):
        # rotates through all boxes
        index = (index + 1) % len(list_lootboxes)
        lootbox = list_lootboxes[index]
        random_index = randomInt(0,len(list_loot))
        loot = list_loot[random_index]
        func(loot,lootbox)
        del list_loot[random_index]
    for lootbox in list_lootboxes:
        adjust_weight(lootbox)
    return list_lootboxes

def dist_unitEntries(list_entries,lootbox):
    for entry in list_entries:
        lootbox.append(entry)

def dist_entries(entry,lootbox):
    lootbox.append(entry)

def unbox_2list_entries(list_unitEntries):
    unboxed_entries = []
    for entries in list_unitEntries:
        for entry in entries:
            unboxed_entries.append(entry)
    return unboxed_entries

# cause rand includes the stop element in the range
def randomInt(start,stop):
    random_index = 0
    if stop > 0:
        random_index = random.randint(start, stop-1)
    return random_index

def write_2zipstream(version, datapack_name, datapack_description, filepath_list, loottables, min_value, max_value, seed, box_count, chance, isUnit, zipbytes):
    print("Beginning writting...")
    prefix_name = "lootbox_{}.json"
    prefix_path = 'data/minecraft/'
    combined_table_path = prefix_path + 'loot_tables/lootboxes'
    zipstream = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)
    zipstream_lootboxes(min_value, max_value, combined_table_path, prefix_name, loottables, zipstream)
    zipstream_editedItems(filepath_list, prefix_path, len(loottables), chance, zipstream)
    # writes functions and additional information into zipfile
    zipstream_metadata(version, datapack_name, datapack_description, seed, box_count, chance, isUnit, zipstream)
    zipstream.close()

def zipstream_lootboxes(min_value, max_value, combined_table_path, prefix_name, loottables, zip):
    print("Writting lootboxes...")
    for x in range(0,len(loottables)):
        name = prefix_name.format(x)
        output_data = {'pools': [{'rolls' : {"min": min_value, "max": max_value},'entries': loottables[x]}]}
        source = os.path.join(combined_table_path,name)
        zip.writestr(source, json.dumps(output_data, indent=4))

def zipstream_editedItems(filepath_list, prefix_path, size_loottable, chance, zip):
    index = randomInt(0,size_loottable-1)
    print("Writting and adjusting loottables...")
    for file in filepath_list:
        index = (index + 1) % size_loottable
        data = add_lootbox_2items(file, index, chance)
        zip.writestr(os.path.join(prefix_path, file), json.dumps(data,indent=4))

def add_lootbox_2items(file, index, chance): # does not use loottable
    data = load_json(file)
    if not "pools" in data:
        return data
    list_entries = data["pools"]          
    list_entries.append(make_lootboxPool(index, len(list_entries), chance))
    return data

# leaves and chest have multiple pools, modifing the pools results in more loot than expected
# comprimise: the original block is not consumed 
def make_lootboxPool(index, size, chance):
    loot_weight = convert_toInt(chance)
    factor = 100.0/chance
    total = int(round(loot_weight * factor,0))
    empty_weight = total - loot_weight
    lootbox_path = "minecraft:lootboxes/lootbox_{}".format(index)
    lootbox_entry = {"type":'minecraft:loot_table',"name":lootbox_path,"weight":loot_weight}
    empty_entry = {"type":'minecraft:empty',"weight": size * empty_weight}
    # its rolls not rools u fucking idiot, and its a float not an int !
    new_pool = {"rolls":1.0,"bonus_rolls":0.0,"entries":[lootbox_entry,empty_entry]}
    return new_pool

# originaly number was given as float, and as such needed to be converted into int
def convert_toInt(chance):
    string = str(chance)
    if '.' in string:
        index = string.index('.')
        digits_after_dot = len(string) - index - 1
    else:
        digits_after_dot = 0
    return int(chance * math.pow(10,digits_after_dot))

def zipstream_metadata(version, datapack_name, datapack_description, seed, box_count, chance, isUnit, zipstream):
    print("Writting metadata....")
    write_pack_mcmeta(version, datapack_description, zipstream)
    write_functrions(datapack_name, seed, box_count, chance, isUnit, zipstream)
    # in the original insperation these file were written, however no idea why
    # tags_path = 'data/minecraft/tags/functions/load.json'
    # tags_content = {'values':['{}:seed'.format(datapack_name)]}
    # zipstream.writestr(tags_path, json.dumps(tags_content))

def write_functrions(datapack_name, seed, box_count, chance, isUnit, zipstream):
    mcfunction_path = 'data/{}/functions/{}.mcfunction'
    # writed all the nessery functions to file
    seed_path =  mcfunction_path.format(datapack_name,"seed")
    seed_content =  'tellraw @a {"text":"Seed %d"}' % seed
    zipstream.writestr(seed_path, seed_content)

    box_count_path = mcfunction_path.format(datapack_name,"boxcount")
    box_count_content = 'tellraw @a {"text":"Number of Boxes %d"}' % box_count
    zipstream.writestr(box_count_path, box_count_content)

    chance_path = mcfunction_path.format(datapack_name,"chance")
    chance_content = 'tellraw @a {"text":"Chance to roll a lootbox is %.2f%%"}' % chance
    zipstream.writestr(chance_path, chance_content)

    unit_path = mcfunction_path.format(datapack_name,"unit")
    unit_text = "Loottables are found together:{}".format(isUnit)
    unit_content = 'tellraw @a {"text":\"%s\"}' % unit_text
    zipstream.writestr(unit_path, unit_content)

    credit_path = mcfunction_path.format(datapack_name,"credit")
    credit_content = 'tellraw @a {"text":"Lootbox Datapack by Redart15","color":"green"}'
    zipstream.writestr(credit_path, credit_content)

    # reload_path = mcfunction_path.format(datapack_name,"reset")
    # reload_content = ''# reset the datapack,

    info_path = mcfunction_path.format(datapack_name,"info")
    info_content = "function lootbox:seed\nfunction lootbox:boxcount\nfunction lootbox:chance\nfunction lootbox:unit\nfunction lootbox:credit"
    zipstream.writestr(info_path, info_content)

def write_pack_mcmeta(version, datapack_description, zipstream):
    pack_mcmeta_path = 'pack.mcmeta'
    pack_mcmeta_content = {'pack':{'pack_format':version, 'description':datapack_description}}
    zipstream.writestr(pack_mcmeta_path, json.dumps(pack_mcmeta_content, indent=4))
    

def read_config(config, tupel, default, type):
    value = config.get(tupel, default)
    if isinstance(value, type):
        return value
    else:
        print("The {} is not an {}".format(tupel,type.__name__))
        print("Using default value {} for {}".format(default,tupel))
        return default

def read_config(config_data, key, default, data_type):
    return data_type(config_data.get(key, default))

def main():
    current_directory = os.getcwd()
    path = os.path.join(current_directory, "setting.json")

    if not os.path.exists(path):
        config_data = {
            "version": 16,
            "box_count": 50,
            "chance": 25.0,
            "min_value": 1,
            "max_value": 5,
            "isUnit": True
        }

        with open(path, 'w') as config_file:
            json.dump(config_data, config_file)

        print("Before generating the loottable, you might want to adjust settings in settings.json")
        print("After that just start the script a new.")
        # ends the program early to allow the player to set their own settings.
        exit()
    else:
        print('Reading in settings...')
        with open(path, 'r') as config_file:
            config_data = json.load(config_file)

        # probably better to set defaults somewhere central and allow players to modify them instead of a file, but not sure
        version = read_config(config_data, "version", 16, int)
        box_count = read_config(config_data, "box_count", 50, int)
        chance = read_config(config_data, "chance", 25.0, float)
        min_value = read_config(config_data, "min_value", 1, int)
        max_value = read_config(config_data, "max_value", 5, int)
        isUnit = read_config(config_data, "isUnit", True, bool)

    # cause of the conversion numbers need to be a set size long
    if chance > 1_000 or chance < 1:
        chance = 25.0
        print("Using default value {} for {}".format(25.0, "chance"))

    # decided to round up
    chance = round(chance, 3)


    if len(sys.argv) >= 2:
        try:
            seed = int(sys.argv[1])
        except:
            print('The seed "{}" is not an integer.'.format(sys.argv[1]))
            exit()
    else:
        print('If you want to use a specific seed use: "python randomize.py <seed>"')
        random_data = os.urandom(8)
        seed = int.from_bytes(random_data, byteorder="big")  

    random.seed(seed)
    datapack_name = 'lootbox'.format(seed)
    

    print('Generating datapack...')
    filepath_list = get_paths2file("loot_tables")
    loottables = generate_loottables(filepath_list, box_count, isUnit)

    print('Preparing data...')
    zipbytes = io.BytesIO()
    datapack_filename = '{}.zip'.format(datapack_name)
    datapack_description = 'Lootboxes, Seed:{}, Box Count:{}, Chance:{}, isUnit:{}'.format(seed,box_count,chance,isUnit)
    write_2zipstream(version, datapack_name, datapack_description, filepath_list, loottables, min_value, max_value, seed, box_count, chance, isUnit, zipbytes)

    print('Zipping files...')
    with open(datapack_filename, 'wb') as file:
        file.write(zipbytes.getvalue())
            
    print('Created datapack {}'.format(datapack_filename))


config_context = """
# 1.20 is Version 16, every major release add 1 to version
# be warned this script may not be compatable with older versions
# type integer
version: 16 

# determins how many different lootboxes there will be (1-100 recommended)
# type integer
box_count: 50 

# sets how many rolls are made on the lootbox tables itself
# type integer
min_value: 1
max_value: 5

# odd of rolling the table, 50 means 50%
# type dezimal
chance: 25.0

# some table are made up of a lot of subtables, keep all these table together when distrubitung into lootboxes
# type boolean
isUnit: True
"""

if __name__ == '__main__':
    excluded_dir = []
    # exclude_dir = ["archaeology", "chests", "entities", "gameplay"]
    main()


# using same number generate the same table, remove # to uncomment this value
# seed: 1