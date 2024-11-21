# Cassettify

Cassettify is an improvement over my old [EasyCassetteImages](https://github.com/roboltz/EasyCassetteImages) app
which was able to create custom cassette covers for the rhythm shooter game [ROBOBEAT](https://store.steampowered.com/app/1456760/ROBOBEAT/).
Cassettify improves on this app by featuring not only cassette cover creation, but full cassette creation.

Full cassette creation means you can import a music file, give it a title and author, create a custom cassette cover, and define the beat positions, and then export as a .robobeat file that can be directly imported within the game.
With the help of ffmpeg, the song file's metadata can also be extracted (if it has any) to get the songs title, author and cover image (which can be used within the cassette cover editor).
the .flac file type is also supported while it is not in the game, as the app will simply convert the .flac into a .wav before archiving the final data into the .robobeat file. The Most important feature in this app is the
automatic beat detection, which uses part of the [Essentia](https://essentia.upf.edu) audio library to find the positions of beats in a song. This is superior to the base game's beat detection, and on certain songs with clear beats, can be even better than cassettes made by people.
The beat detection is great at finding the beats to old songs with inconsistent BPM, but can sometimes get confused, and often thinks that the offbeat of the song is the main beat. If this happens you can select all beats in ROBOBEAT's cassette editor with Ctrl+A, and then adjust the timings to the main beat. An extra alternate beat detection method may be added to counteract this as well.

## Credits
Font: [Pixelated by Greenma20](http://fontstruct.com/fontstructions/show/426637)

Beat detector: [Essentia Beat Tracker](https://essentia.upf.edu), found at Download > Precompiled extractor binaries > Current builds > essentia-extractors-v2.1_beta5-356-g673b6a14-win-i686 > essentia_streaming_beattracker_multifeature_mirex2013.exe

Other audio related tasks: [ffmpeg](https://ffmpeg.org), found at Download > Get packages & executable files > Windows > Windows builds from gyan.dev > ffmpeg-git-essentials.7z

Color Wheel: [CTkColorPicker](https://github.com/Akascape/CTkColorPicker)

## Screenshots
Note: Screenshots are from version v0.1.1-alpha, There are some differences in the UI in later versions.

Config:
![Cassettify 03_10_2024 22_48_26](https://github.com/user-attachments/assets/0cf7a9b4-856c-4525-abb3-2d08d28acad1)
Image of metadata pulled from one of [Pascal Michael Stiefel's](https://open.spotify.com/artist/3FU61shb6MdX8NLBnBauTI?si=Gke0s4uCSs6xX_mEjH4yIQ) songs from the [A Hat In Time OST](https://store.steampowered.com/app/356831/A_Hat_in_Time__Soundtrack/), Train Rush.

Visual:
![New File at _ · roboltz_Cassettify — Mozilla Firefox 03_10_2024 22_56_11](https://github.com/user-attachments/assets/ad58092a-5d14-4334-8622-4fa8d95a5186)
Image for cassette cover pulled from pulled metadata on config page. (see above)

Track:
![Captures - File Explorer 03_10_2024 23_00_00](https://github.com/user-attachments/assets/803ebd32-8764-4449-b2d5-9e450f16ef04)
After clicking the "Finds Beats" button the application will freeze for several seconds and show you the list of beats it found.

![Captures - File Explorer 03_10_2024 23_01_51](https://github.com/user-attachments/assets/9c5ad79b-a310-4165-a0ef-8b7e9cbe7315)
If you have a song selected, set a title and author (or selected the extracted title and author checkbox), added a cover (you can select the default checkbox as well), and found the beat positions, you will be able to export your cassette.

After you import the robobeat file, you can play it like any other cassette!
![ROBOBEAT 03_10_2024 23_33_43](https://github.com/user-attachments/assets/bed4ca83-4159-4a6b-9044-412b2b4907d4)

## Known Issues
* App freezes when finding beats. (Not really a bug, but can be confusing for people who think that their app might have crashed.)

Please report any issues you experience to the issues tab, but check to see if the issue you are experiencing hasn't already been discussed.

## Planned Additions
* Constant BPM mode. (for better support for most newer digital music)
* BPM Range for the automatic beat finder (set the range you want the bpm to be set to for higher or lower bpm limits)
* Button in track menu to listen to the song with beat ticks
* Visual Beat editor (similar to the base game's, but with some extra features like beat snapping, this will take a while and wont be added until much later)

## Build Instructions
These instructions are designed for people contributing to the repository and are testing, or if I update the app and forget to make a precompiled release for it. For an already compiled version, check under Releases on the right side of the tab.

1. Download source code, either manually or with this git command:
```console
git clone https://github.com/roboltz/Cassettify.git
```
2. Open your command prompt if you haven't already and change your directory into the downloaded folder. If you installed the source code manually you will need to unzip it first.

3. download the latest version of [Python 3.12](https://www.python.org/downloads) and run this command to create an enviornment in the folder to store the libraries:
```console
py -3.12 -m venv .venv
```
4. Activate the created enviornment:
```console
.venv\Scripts\activate
```
You should now see (.venv) to the far right of the console prefixing the path.

5. Make sure pip is updated:
```console
py -m pip install --upgrade pip
```
6. Install all required libraries from the requirements.txt file:
```console
py -m pip install -r requirements.txt
```
7. You can either:
Run python through the Run.py file:
```console
py Run.py
```
Make sure the enviornment is activated before doing this! the enviornment will deactivate every time you close the command prompt.

Or compile the app:
```console
py -m nuitka --standalone --enable-plugin=tk-inter --mingw64 --windows-icon-from-ico=images/icon.ico App.py
```
If you have not run the Nuitka compiler before, it will take a while.
After compiling, delete the App.build folder that is created in the source code. There is also a App.dist folder that is created as well. This is what holds the compiled executable, and is named "App.exe".
The executable should still NOT work properly yet. Copy every other folder from the main source code folder into App.dist EXCEPT .venv, App.py, and requirements.txt. Now you can remove the App.dist folder from the source code and rename it and the executable to whatever you want (as long as the executable keeps the .exe suffix)
