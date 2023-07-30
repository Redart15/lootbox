# Lootbox Datapack

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)\
[![GitHub latest commit](https://badgen.net/github/last-commit/Redart15/lootbox)](https://GitHub.com/Redart15/lootbox/commit/)\
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Redart15/lootbox/graphs/commit-activity)\
[![Windows](https://badgen.net/badge/icon/windows?icon=windows&label)](https://microsoft.com/windows/)\
 [![GitHub release](https://img.shields.io/github/release/Redart15/lootbox)](https://GitHub.com/Redart15/lootbox/releases/)\
<!--[![GitHub all releases](https://img.shields.io/github/downloads/redart15/lootbox/total)](https://GitHub.com/Redart15/lootbox/releases/)-->



# Introduction
Have you ever wanted loot explosions in Minecraft, like in $\color{orange}\texttt{Path of Exile}$?\
Now you can with this datapack. Once in a while a block, entity, structure chest, event or archaeological discovery will erupt into random items.  


# Generate your own
If you used github and have programed in python than you can skip reading this.

For everyone else, click the file readme.pdf or follow the written guide below:

1. Click on green button Code
2. Navigate down to download
3. Click download
4. Unpack the file by right clicking file and select 7-Zip.\
    You should now have a folder called lootbox with files:
    1. [lootbox.zip](./lootbox.zip)\
    This is a finished datapack, if you do not want to generate your own
    2. [readme.pdf](./readme.pdf)\
    Contains a step by step instruction with pictures
    3. [readme.md](./readme.md)\
    In this file you will find the instruction seen on github.
    4. [lootbox.py](./lootbox.py)\
    Lasty this file contains the programm for generating your own lootbox datapack.

If you want to generate your own datapack read on, other wise have fun :grin:

1. google python and download the lates release
2. install python
3. open windows searchbar 
4. type in `%appdata%` and hit enter
5. click `.minecraft`
6. click `versions`
7. navigate to the lates version and opne folder
8. unzip the `.jar` file 
9. click data
10. click minecraft
11. copy loot_tables
12. paste into the folder containing lootbox.py
13. in the same folder click on the adress bar
14. type in `cmd` and hit enter, it should open cmd
15. type `python --version` to confirm pythons installation
16. type `python lootnox.py` it will generate a file [settings.](./settings)
17. open settings
18. modify at will and save
19. back at the command prompt type again `python lootbox.py` followed optionaly by your seed. \
The seed has to be an integer otherwise it will be random.
20. **wait**, it may take 30 seconds for the pack to be generated
21. after it finished there will be a file named `lootbox.zip` This is the datapack file.\

Enjoy!

# About
This repository will be maintained at will. If you want to contibute you can push your own changes or fork the repository. 

The code is mostly commented or self explanetory. 

Setting.json:

`version`: this is the version the datapack is designed for. As of making this guide the current version is 1.20 whice is represented as version 15. Here is just a typo.\
`Type: Integer`

`box count`: this number indicated how many different loottables for the lootboxes will be generated\
`Type: Integer`

`chance`: how common the loot explosions are.\
`Type: Decimal`

`min & max`: how many items are drops when a loot explosion happens\
`Type: Integer`

`IsUnit`: some loot tables consist of many different items, if this is set True that all the items of the same loot tables will be in the same box.\
`Type: Treu/False`


# Changes
## 30.07.2023 - v.1.0
### Added
- readme.pdf, a guide to build one own datapack
- readme.md:
    - added setting documentation
    - added some badges
    
### Changed
- switch to `json` cause `yaml` isn't not out of the box supported on windows

## 30.07.2023 - init

### Upload
- unloaded the repository to github
