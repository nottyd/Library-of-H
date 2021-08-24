# Requirements
- Windows: Works on Windows 10, not tested with other versions.  
- Linux: Should work on Linux, not tested.
- Python:
```
python          3.x  
colorama        0.3.9  
mechanize       0.4.5  
beautifulsoup4  4.9.3  
Pillow          8.3.1  
PyQt5           5.15.4  
lxml            4.6.3  
```

# nhentaiDownloader  
Script created using Python to download individual galleries or all artist/group galleries from nhentai.
## menu
- **Download by Galleries**: Will prompt to input gallery codes separated by spaces.
- **Download by Artists**: Will prompt to input artist names separated by commas.
- **Download by Groups**: Will prompt to input group names separated by commas.
## nhentaiConfig.ini
 - **[Network]**
    - **useragent**: input user agent. _(Already has one by default.)_
    - **retry**: How many times should the script retry when met with a temporary http error.
    - **retrywait**: How long the script should wait after each retry.
  - **[Filters]**
    - **collection**: `True` if you want comic, anthologies, etc to be filtered _out_, `False` if you want to download them too.
    - **duplicate**: `True` if you want duplicates to be filtered _out_, `False` if you want to download duplicates too. _(Should work for the most part.)_
  - **[GeneralSettings]**
    - **gallerydownloadlocation**: location for script to download individual galleries into.
    - **artistdownloadlocation**: location for script to download artist galleries into.
    - **groupdownloadlocation**: location for script to download group galleries into.
    - **databaselocation**: location for script to create nhentaiDatabase.db in.
  - **[Filenames]**
    - **gallerydownloadnameformat**: format for individual gallery download location.
    - **artistdownloadnameformat**: format for artist gallery download location.
    - **groupdownloadnameformat**: format for group gallery download location.
  - **[DownloadSettings]**
    - **overwrite**: `True` if you want to overwrite if/when the script encounters already downloaded files, else `False`.

## [Filenames] formats
  ###### Using `%(gallery_code)s` in every gallery directory name is recommended as gallery codes (gallery id) will always be unique, unlike the other parameters (namely the title).
  **For gallerydownloadnameformat**
  ```
    - %(gallery_before)s:
        nhentai term for the grey text that comes before the gallery title.
    - %(gallery_title)s:
        The main gallery title.
    - %(original_title)s:
        Untranslated gallery title.
    - %(translated_title)s:
        Translated gallery title.
    - %(gallery_after)s:
        nhentai term for the grey text that comes after the gallery title.
    - %(gallery_code)s:
        nhentai assigned id for the gallery.
  ```
  **For artistdownloadnameformat**
  ```
   - %(artist_name)s:
      Name of the artist.
   - %(gallery_before)s:
      nhentai term for the grey text that comes before the gallery title.
   - %(gallery_title)s:
      The main gallery title.
    - %(original_title)s:
        Untranslated gallery title.
    - %(translated_title)s:
        Translated gallery title.
   - %(gallery_after)s:
      nhentai term for the grey text that comes after the gallery title.
   - %(gallery_code)s:
      nhentai assigned id for the gallery.
  ```
  **For groupdownloadnameformat**
  ```
    - %(group_name)s:
        Name of the group.
    - %(gallery_before)s:
        nhentai term for the grey text that comes before the gallery title.
    - %(gallery_title)s:
        The main gallery title.
    - %(original_title)s:
        Untranslated gallery title.
    - %(translated_title)s:
        Translated gallery title.
    - %(gallery_after)s:
        nhentai term for the grey text that comes after the gallery title.
    - %(gallery_code)s:
        nhentai assigned id for the gallery.
  ```
## usage
Run the python file.
```
$ python3 nhentaiDownloader.py
Choose a download method:  
1. Download by Galleries
2. Download by Artists
3. Download by Groups
Enter x to exit.
>>
```
# nhentaiExplorer  
An image explorer that uses the database file created by the downloader to view galleries. Basically create an (tiny) offline nhentai.net. _(WIP)_
## Import
Import the `nhentaiDatabase.db` file created by the nhentaiDownloader script.
## Search
- **artists**: filter database by artist name.
- **characters**: filter database by character name.
- **ids**: filter database by id (gallery code).
- **groups**: filter database by group name.
- **parodies**: filter database by parody name.
- **tags**: filter database by tag.
- **titles**: filter database by title.
- **collections**: filter database by collection type. _(Not implemented yet.)_
- **custom...**: filter database by custom filter. _(Not implemented yet.)_

## usage
Run the python file.
# nhentaiLibraryToDatabase
A script to create a database file with already existing nhentai library.  
_Library must contain metadata.csv files for this to work._

## usage:
```python
python3 nhentaiLibraryToDatabase.py "location/to/library"
```
