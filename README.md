# Cassettify

Cassettify is an improvement over my old [EasyCassetteImages](https://github.com/roboltz/EasyCassetteImages) app
which was able to create custom cassette covers for the rhythm shooter game [ROBOBEAT](https://store.steampowered.com/app/1456760/ROBOBEAT/).
Cassettify improves on this app by featuring not only cassette cover creation, but full cassette creation.

Full cassette creation means you can import a music file, give it a title and author, create a custom cassette cover, and define the beat positions, and then export as a .robobeat file that can be directly imported within the game.
With the help of ffmpeg, the song file's metadata can also be extracted (if it has any) to get the songs title, author and cover image (which can be used within the cassette cover editor).
the .flac file type is also supported while it is not in the game, as the app will simply convert the .flac into a .wav before archiving the final data into the .robobeat file. The Most important feature in this app is the
automatic beat detection, which uses part of the [Essentia](https://essentia.upf.edu) audio library to find the positions of beats in a song. This is superior to the base game's beat detection, and on certain songs with clear beats, can be even better than cassettes made by people.
The beat detection is great at finding the beats to old songs with inconsistent BPM, but can sometimes get confused, and often thinks that the offbeat of the song is the main beat. If this happens you can select all beats in ROBOBEAT's cassette editor with Ctrl+A, and then adjust the timings to the main beat. An extra alternate beat detection method may be added to counteract this as well.

Looping is currently disabled because of a bug when importing the .robobeat file with already defined start and end times, but you can still test out the looping system on the Track page, it will just not be exported. It has already been fixed and will be added in the next update.

## Credits
Font: [Pixelated by Greenma20](http://fontstruct.com/fontstructions/show/426637)
Beat detector: [Essentia Beat Tracker](https://essentia.upf.edu), go to Download > Precompiled extractor binaries > Current builds > essentia-extractors-v2.1_beta5-356-g673b6a14-win-i686 > essentia_streaming_rhythmextractor_multifeature.exe
Other audio related tasks: [ffmpeg](https://ffmpeg.org), go to Download > Get packages & executable files > Windows > Windows builds from gyan.dev > ffmpeg-git-essentials.7z


## Screenshots
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
* File names that contain special characters, for example text in another language, will not be able to be imported properly. Same goes for the metadata. Until a patch is released, if your filename has special characters, simply rename it. If your metadata has special characters, use an online metadata remover.

## Planned Additions

* Constant BPM mode. (for better support for most newer digital music)
* RGBA selector for custom cassette color.
* Fixing and reimplementing looping. (done, will be added in next update)
* Visual Beat editor (similar to the base game's, but with some extra features like beat snapping)
