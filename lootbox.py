import json
import os
import random
import sys
import zipfile
import io
import math

"""
comments are always pointing down
structure:
loot_table:pool
    pools:list -> pools
    pools -> pool
        pool:dict -> entries
        entries -> entry
            entry:dict
"""

# need paths multiple times to keep the code readable
def get_paths2file(path):
    print("Getting filepaths...")
    file_list = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [dirname for dirname in dirnames if dirname not in excluded_dir] # for testing it excludes 'combined'
        for filename in filenames:
            if filename == "fishing.json":
                continue
            file = os.path.join(dirpath, filename)
            print(file)
            file_list.append(file)
    return file_list    

def generate_loottables(filepath_list, box_count, isUnit):
    print("Generating lootboxes")
    list_loot = collect_unitEntries(filepath_list)
    #add_identifier(list_loot)
    list_lootboxes = distLoot_boxes(list_loot,box_count,isUnit)
    #adjust_weight(list_lootboxes)
    return list_lootboxes


def adjust_weight(list_lootbox):
    for lootbox in list_lootbox:
        # new table has different total weight
        total = get_total(lootbox,"old_weight")
        for entry in lootbox:
            weight = entry["weight"]
           # common item in origina table are now also common items in new table
            # entry["weight"] = int(math.ceil(weight * total)) # maybe this is the issue
            entry["weight"] = int(weight * total)
            del entry["old_weight"]

# set weight as percent of total, save old_weight for later
def add_identifier(list_unitEntries):
    for unitEntries in list_unitEntries:
        total = get_total(unitEntries,"weight")
        for entry in unitEntries:
            if not "weight" in entry:
                entry["weight"] = 1
            weight = entry["weight"]
            entry["weight"] = round(weight/total, 2)
            entry["old_weight"] = weight

# get total weight, for modification
def get_total(unitEntries, sum_over):
    total = 0
    for entry in unitEntries:  
        if sum_over in entry:
            total = total + entry[sum_over]
        else:
            total = total + 1
            entry[sum_over] = 1
    return total
        


def collect_unitEntries(filepath_list):
    # unitEntries is a collection of entries of a given table
    list_unitEntries = []
    for file in filepath_list:
        data = load_json(file) # load json
        if not "pools" in data:
            continue
        pools = data["pools"]
        # collect all entries to a list to keep then as one pools
        list_entries = collect_entries(pools)
        list_unitEntries.append(list_entries)
    # for later need to unbox the element of each list_entries back to entries
    return list_unitEntries      

def collect_entries(pools):
    list_entries = []
    for pool in pools: 
        entries = pool["entries"]
        for entry in entries:
            entry = remove_conditions(entry)
            list_entries.append(entry)
    return list_entries

# just to shorten code
def load_json(source):
    with open(source,'r') as source:
        data = json.load(source)
    return data

# removes a bunch of edge cases, less complexity
def remove_conditions(toadd):
    # need to extract the entry out of the subentry
    toadd = remove_enchantmentReq(toadd)
    remove_2ndConditions(toadd)
    remove_functions(toadd)
    return toadd 

def remove_functions(toadd):
    if "functions" in toadd:
        # del toadd["functions"]
        function_list = toadd["functions"]
        for func in function_list:
            if "minecraft:looting_enchant" in func["function"]:
                function_list.remove(func)

def remove_2ndConditions(toadd):
    if "conditions" in toadd:
        del toadd["conditions"]

def remove_enchantmentReq(toadd):
    if "children" in toadd:
        for child in toadd["children"]:
            if "conditions" in child:
                del child["conditions"]
                toadd = child 
                break
    return toadd

def distLoot_boxes(list_loot, box_count,isUnit):
    count = len(list_loot)

    # option between unit or individual entries
    if isUnit:
        func = dist_unitEntries
    else:
        list_loot = unbox_2list_entries(list_loot)
        func = dist_entries

    # lootboxes need to be filled with at least one element
    if(box_count > count):
        box_count = count
    list_lootboxes = [[] for _ in range(box_count)]

    index = 0
    while(list_loot):
        index = shiftIndex_bounded(index,len(list_lootboxes))
        lootbox = list_lootboxes[index]
        random_index = randomInt(0,len(list_loot))
        loot = list_loot[random_index]
        func(loot,lootbox)
        del list_loot[random_index]
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

# just to shorten code, shift index in circle
# needed to cicle through list_unitEntries
def shiftIndex_bounded(init, size):
    return (init + 1) % size

def write_2zipstream(version, datapack_name, datapack_description, filepath_list, loottables, zipbytes):
    print("Beginning writting...")
    prefix_name = "lootbox_{}.json"
    prefix_path = 'data/minecraft/'
    combined_table_path = prefix_path + 'loot_tables/loot_boxes'
    zipstream = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)
    zipstream_lootboxes(combined_table_path, prefix_name, loottables, zipstream)
    zipstream_editedItems(filepath_list, prefix_path, loottables, zipstream)
    zipstream_metadata(version, datapack_name, datapack_description, zipstream)
    zipstream.close()

def zipstream_lootboxes(combined_table_path, prefix_name, loottables, zip):
    print("Writting lootboxes...")
    min_value = 1
    max_value = 5
    for x in range(0,len(loottables)):
        name = prefix_name.format(x)
        output_data = {'pools': [{'rolls' : {"min": min_value, "max": max_value},'entries': loottables[x]}]}
        source = os.path.join(combined_table_path,name)
        zip.writestr(source, json.dumps(output_data, indent=4))

def zipstream_editedItems(filepath_list, prefix_path, loottables, zip):
    index = randomInt(0,len(loottables)-1)
    print("Writting and adjusting loottables...")
    for file in filepath_list:
        index = shiftIndex_bounded(index, len(loottables))
        data = add_lootbox_2items(file, loottables, index)
        zip.writestr(os.path.join(prefix_path, file), json.dumps(data,indent=4))

def add_lootbox_2items(file, loottables, index):
    data = load_json(file)
    if not "pools" in data:
        return data
    list_entries = data["pools"]          
    list_entries.append(make_lootboxPool(index, len(list_entries)))
    return data

# leaves and chest have multiple pools, modifing the pools results in more loot than expected
# comprimise: the original block is not consumed 
def make_lootboxPool(index, size):
    lootbox_path = "minecraft:lootboxes/lootbox_{}".format(index)
    lootbox_entry = {"type":'minecraft:loot_table',"name":lootbox_path,"weight":1}
    empty_entry = {"type":'minecraft:empty',"weight": size * 3}
    # its rolls not rools u fucking idiot, and its a float not an int !
    new_pool = {"rolls":1.0,"bonus_rolls":0.0,"entries":[lootbox_entry,empty_entry]}
    return new_pool

def zipstream_metadata(version, datapack_name, datapack_description, zipstream):
    print("Writting metadata....")
    pack_mcmeta_path = 'pack.mcmeta'
    pack_mcmeta_content = {'pack':{'pack_format':version, 'description':datapack_description}}
    tags_path = 'data/minecraft/tags/functions/load.json'
    tags_content = {'values':['{}:reset'.format(datapack_name)]}
    mcfunction_path = 'data/{}/functions/reset.mcfunction'.format(datapack_name)
    mcfunction_content = 'tellraw @a ["",{"text":"Tables Lootbox Datapack by Redart15","color":"cyan"}]'
    zipstream.writestr(pack_mcmeta_path, json.dumps(pack_mcmeta_content, indent=4))
    zipstream.writestr(tags_path, json.dumps(tags_content))
    zipstream.writestr(mcfunction_path, mcfunction_content)


def main():
    """
    TODO:
        fatal
            no git so idk how to return to working state without massakering alot
        error
            only works as command not as actual minable blocks
        bug
            item -> loottable -> colored sheep -> sheep => can not be killed by player cause it a drop of a loottable
            need to somehow prevent tables leaving loottable. idee, dont allow table references to be included.
        add a way to set settings for:
            seed
            box count
            version
            isUnit  
        write some help, for not programmers
            write --help for python script
            write a popup in chat for help
            write something to disable popup
        write some helping inbetween steps
            2 output streams
                to log file of some sort
                to screen
    """

    print('Reading in settings...')
    box_count = 4
    version = 16
    isUnit = True

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
    datapack_name = 'lootbox'
    

    print('Generating datapack...')
    filepath_list = get_paths2file("loot_tables")
    loottables = generate_loottables(filepath_list, box_count, isUnit)

    print('Preparing data...')
    datapack_filename = '{}.zip'.format(datapack_name)
    datapack_description = 'Lootboxes, Box Count:{}, Seed:{}'.format(box_count,seed)
    zipbytes = io.BytesIO()
    write_2zipstream(version, datapack_name, datapack_description, filepath_list, loottables, zipbytes)

    print('Zipping files...')
    with open(datapack_filename, 'wb') as file:
        file.write(zipbytes.getvalue())
            
    print('Created datapack {}'.format(datapack_filename))



if __name__ == '__main__':
    excluded_dir = ['combined',"combiined","sheep"]
    main()