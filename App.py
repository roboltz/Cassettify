import customtkinter, CTkColorPicker
from PIL import Image
import os, shutil
import subprocess
from pygame import mixer
import pygame
import json
import random, string
from pydub import AudioSegment
import threading

# Initializes pygame which handles music playback
pygame.init()

# Setting UI Theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("theme/cassettify_theme.json")

# Deletes all temporary files added by user
def clean():
    if os.path.exists("ffmpeg\\image_output\\cover.jpg"):
        os.remove("ffmpeg\\image_output\\cover.jpg")
    if os.path.exists("beat_finder\\output\\beat.txt"):
        os.remove("beat_finder\\output\\beat.txt")
    if os.path.exists("ffmpeg\\flac_convert_output\\output.wav"):
        os.remove("ffmpeg\\flac_convert_output\\output.wav")
    if os.path.exists("beat_previewer\\output\\output.wav"):
        os.remove("beat_previewer\\output\\output.wav")
    if os.path.exists("beat_previewer\\wav_song\\input.wav"):
        os.remove("beat_previewer\\wav_song\\input.wav")
    for temp_file in os.listdir("temp"):
        os.remove("temp\\" + temp_file)
    for audio_file in os.listdir("song"):
        os.remove("song\\" + audio_file)

clean()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # Handles window size, title, and icon
        self.geometry("1000x600")
        self.title("Cassettify")
        self.after(201, lambda :self.iconbitmap("images/icon.ico"))
        
        # Loading custom font
        customtkinter.FontManager.load_font("font/pixelated/pixelated.ttf")
        self.text_font = customtkinter.CTkFont("Pixelated Regular", 20)

        self.VERSION = "V0.1.4-A"

        # runs sidebar() method for options on the left side of the screen
        self.sidebar()

        # Defining variables

        self.current_page = None
        self.selected_music_file = None
        self.current_music_file = None
        self.song_duration = "0.00"
        self.song_author = ""
        self.song_title = ""

        self.extracted_song_author = None
        self.extracted_song_title = None
        self.entered_song_author = ""
        self.entered_song_title = ""

        self.using_extracted_data = False

        self.song_name_entry = None
        self.song_author_entry = None

        self.config_cover_image_label = None
        self.config_duration_label = None
        self.extracted_song_author_label = None
        self.extracted_song_title_label = None
        self.extracted_title_author_checkbox = None

        self.cassette_cover_overlay = Image.open("images\\SmallCustomCassetteTemplate.png")
        self.cassette_cover_overlay = self.cassette_cover_overlay.resize((280, 280))
        self.cassette_cover_overlay = self.cassette_cover_overlay.rotate(90)
        self.cassette_cover_overlay = self.cassette_cover_overlay.resize((280, 178))
        self.cover_pos_x = 0
        self.cover_pos_y = 0
        self.cover_rotation = 0
        self.current_cover = None
        self.default_cover = False
        self.full_cassette_cover = None

        self.cover_red = 255
        self.cover_green = 255
        self.cover_blue = 255
        self.hex_color = "#FFFFFF"

        self.alpha_slider_step = 0

        self.loop_start = None
        self.loop_end = None
        self.num_beats = 0
        self.beatList=[]

        self.viewable_beats = None
        self.beat_list_textbox = None
        self.beat_list_scrollbar = None
        self.progress_bar = None

        self.entered_start_loop = None
        self.entered_end_loop = None
        self.loop_start_entry = None
        self.loop_end_entry = None

        self.child_states = []


    # Creates an interactable sidebar on the left side of the screen
    # which allows you to travel between different screens
    def sidebar(self):
        # Frame
        sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0, width=150, height=5000)
        sidebar_frame.place(x=0, y=0)

        # Icon and title
        icon_image = Image.open("images\\icon.png")
        icon_image = icon_image.convert("P", palette=Image.ADAPTIVE, colors=10, dither=Image.FLOYDSTEINBERG)
        sidebar_icon = customtkinter.CTkImage(light_image=icon_image, dark_image=icon_image, size=(100, 100))
        sidebar_icon_label = customtkinter.CTkLabel(sidebar_frame, width=75, height=75, image=sidebar_icon, text="")
        sidebar_icon_label.place(x=25, y=25)
        title_label = customtkinter.CTkLabel(sidebar_frame, width=149.5, text="CASSETTIFY", font=self.text_font)
        title_label.place(x=0, y=10)
        version_label = customtkinter.CTkLabel(sidebar_frame, width=149.5, text=self.VERSION, font=self.text_font)
        version_label.place(x=0, y=550)

        # Buttons for changing screen
        config = customtkinter.CTkButton(sidebar_frame, width=149.5, height=30, text="Config", border_width=0, corner_radius=0, font=self.text_font, command=self.config_page)
        config.place(x=0, y=115)
        visuals = customtkinter.CTkButton(sidebar_frame, width=149.5, height=30, text="Visuals", border_width=0, corner_radius=0, font=self.text_font, command=self.visual_page)
        visuals.place(x=0, y=145)
        track = customtkinter.CTkButton(sidebar_frame, width=149.5, height=30, text="Track", border_width=0, corner_radius=0, font=self.text_font, command=self.track_page)
        track.place(x=0, y=175)
        export = customtkinter.CTkButton(sidebar_frame, width=149.5, height=30, text="Export", border_width=0, corner_radius=0, font=self.text_font, command=self.export_page)
        export.place(x=0, y=205)
        

    # Page which lets you import your song and change various info
    # about the cassette such as title and author
    def config_page(self):
        # Reset page area
        config_frame = self.start_new_page()

        # Title and author entry
        self.song_name_entry = customtkinter.CTkEntry(config_frame, font=self.text_font)
        self.song_name_entry.place(x=45, y=50)

        song_name_label = customtkinter.CTkLabel(config_frame, text="Title", font=self.text_font)
        song_name_label.place(x=50, y=20)

        self.song_author_entry = customtkinter.CTkEntry(config_frame, font=self.text_font)
        self.song_author_entry.place(x=45, y=130)

        song_author = customtkinter.CTkLabel(config_frame, text="Author", font=self.text_font)
        song_author.place(x=50, y=100)

        # Button to select music file
        config_track = customtkinter.CTkButton(config_frame, width=100, height=30, text="Select Music File", border_width=0, corner_radius=5, font=self.text_font, command=self.select_music_file)
        config_track.place(x=45, y=245)
        
        # Text showing selected file
        self.config_track_filename = customtkinter.CTkLabel(config_frame, text="No File Selected", font=self.text_font)
        self.config_track_filename.place(x=50, y=280)

        # Checkbox for using title and author from metadata in cassette
        self.extracted_title_author_checkbox = customtkinter.CTkCheckBox(config_frame, text="Use Extracted Title & Author", font=self.text_font, border_width=1, corner_radius=0, state="disabled", command=self.on_extracted_data_checkbox_pressed)
        self.extracted_title_author_checkbox.place(x=50, y = 340)
        
        # Checkbox to preview selected song
        self.config_preview_song_checkbox = customtkinter.CTkCheckBox(config_frame, text="Preview Song", font=self.text_font, border_width=1, corner_radius=0, command=self.preview_song, state="disabled")
        self.config_preview_song_checkbox.place(x=50, y = 400)

        # Handles returning screen to previous state after the user clicks off the screen and then returns
        if self.selected_music_file:
            self.config_track_filename.configure(text=os.path.basename(self.selected_music_file))
            self.config_preview_song_checkbox.configure(state="normal")
            if self.extracted_song_title:
                self.extracted_song_title_label = customtkinter.CTkLabel(self.current_page, text=self.extracted_song_title, font=self.text_font)
            else:
                self.extracted_song_title_label = customtkinter.CTkLabel(self.current_page, text="No Title Found", font=self.text_font)
            self.extracted_song_title_label.place(x=350, y=50)
            if self.extracted_song_author:
                self.extracted_song_author_label = customtkinter.CTkLabel(self.current_page, text=self.extracted_song_author, font=self.text_font)
            else:
                self.extracted_song_author_label = customtkinter.CTkLabel(self.current_page, text="No Author Found", font=self.text_font)
            if self.extracted_song_author and self.extracted_song_title:
                self.extracted_title_author_checkbox.configure(state="normal")
            self.extracted_song_author_label.place(x=350, y=20)
            self.config_duration_label = customtkinter.CTkLabel(self.current_page, text=str(round(float(self.song_duration), 3)) + "  Seconds", font=self.text_font)
            self.config_duration_label.place(x=350, y=240)
            try:
                music_image = Image.open("ffmpeg\\image_output\\cover.jpg")
                cover_image = customtkinter.CTkImage(light_image=music_image, dark_image=music_image, size=(150, 150))
                cover_text = ""
            except:
                music_image = None
                cover_image = None
                cover_text = "No Image Found"
            if self.config_cover_image_label:
                self.config_cover_image_label.destroy()
            self.config_cover_image_label = customtkinter.CTkLabel(self.current_page, width=150, height=150, image=cover_image, text=cover_text, font=self.text_font)
            self.config_cover_image_label.place(x=350, y=85)
            self.song_name_entry.insert("end", self.entered_song_title)
            self.song_author_entry.insert("end", self.entered_song_author)
            if self.using_extracted_data:
                self.extracted_title_author_checkbox.select()
                self.song_name_entry.configure(state="disable")
                self.song_author_entry.configure(state="disable")
            

    # Handles the user selecting a music file, and runs when the user clicks the config_track
    # button under the config_page() function
    def select_music_file(self):
        # Opens files select screen, returns as a full file path
        self.selected_music_file = customtkinter.filedialog.askopenfilename(filetypes=[("Music Files", "*.mp3 *.ogg *.wav *.flac")], initialdir = os.path.join(os.path.expanduser("~"), "Downloads"))

        # Continues only if the user selected a file
        if self.selected_music_file:
            self.using_extracted_data = False
            self.current_cover = None
            self.default_cover = False
            self.song_author_entry.delete(0, len(self.song_author_entry.get()))
            self.song_name_entry.delete(0, len(self.song_name_entry.get()))
            # Creates a variable for the new file path of the selected song
            # and changes based on the audio type (ex: audio/song.mp3, audio/song.ogg)
            self.current_music_file = "song\\song" + os.path.splitext(self.selected_music_file)[1]
            # Removes the previous music file in the future position if it exists
            mixer.music.unload()
            if os.path.exists(self.current_music_file):
                os.remove(self.current_music_file)
            # Copies the file to the new destination and renames it
            # This fixes a bug which is caused by the essentia beat tracker
            # not being able to read files with unicode characters in their name
            shutil.copy(self.selected_music_file, self.current_music_file)
            
            mixer.music.load(self.current_music_file)
                
            # Allows user to select checkboxes
            self.song_name_entry.configure(state="normal")
            self.song_author_entry.configure(state="normal")
            self.extracted_title_author_checkbox.deselect()
            self.config_preview_song_checkbox.configure(state="normal")
            # Toggles checkbox to run the preview_song() function and stop the currently playing song
            # Deselect does not run the checkbox's command
            if self.config_preview_song_checkbox.get() == 1:
                self.config_preview_song_checkbox.toggle()
            
            # Gets the file name of the song file from the file path and sets that to the config page text
            self.config_track_filename.configure(text=os.path.basename(self.selected_music_file))

            # Removes old metadata song cover if it exists
            if os.path.exists("ffmpeg\\image_output\\cover.jpg") and self.current_music_file:
                os.remove("ffmpeg\\image_output\\cover.jpg")
            # Attempts to extract song cover, title, and artist from metadata and extracts song duration
            self.run_command("ffmpeg\\ffmpeg.exe -i \"" + self.current_music_file + "\" -an -c:v copy ffmpeg\\image_output\\cover.jpg")
            self.song_duration = self.run_command("ffmpeg\\ffprobe.exe -i \"" + self.current_music_file + "\" -show_entries format=duration -v quiet -of csv=\"p=0\"")

            self.extracted_song_title = self.run_command("ffmpeg\\ffprobe.exe -v error -show_entries format_tags=title -of default=nw=1:nk=1 \"" + self.current_music_file + "\"")
            self.extracted_song_author = self.run_command("ffmpeg\\ffprobe.exe -v error -show_entries format_tags=artist -of default=nw=1:nk=1 \"" + self.current_music_file + "\"")

            self.loop_end = self.song_duration

            # Lets the user press the use extracted title and author button
            # only if both title and author were successfully extracted from the metadata
            if self.extracted_song_author and self.extracted_song_title:
                self.extracted_title_author_checkbox.configure(state="normal")
            else: 
                self.extracted_title_author_checkbox.configure(state="disabled")
            
            # Show found metadata on config screen
            if self.extracted_song_title_label:
                self.extracted_song_title_label.destroy()
            self.extracted_song_title_label = customtkinter.CTkLabel(self.current_page, text=self.extracted_song_title, font=self.text_font)
            if not self.extracted_song_title:
                self.extracted_song_title_label.configure(text="No Title Found")
            self.extracted_song_title_label.place(x=350, y=50)

            if self.extracted_song_author_label:
                self.extracted_song_author_label.destroy()
            self.extracted_song_author_label = customtkinter.CTkLabel(self.current_page, text=self.extracted_song_author, font=self.text_font)
            if not self.extracted_song_author:
                self.extracted_song_author_label.configure(text="No Author Found")
            self.extracted_song_author_label.place(x=350, y=20)

            if self.config_duration_label:
                self.config_duration_label.destroy()
            self.config_duration_label = customtkinter.CTkLabel(self.current_page, text=str(round(float(self.song_duration), 3)) + "  Seconds", font=self.text_font)
            self.config_duration_label.place(x=350, y=240)

            try:
                music_image = Image.open("ffmpeg\\image_output\\cover.jpg")
                cover_image = customtkinter.CTkImage(light_image=music_image, dark_image=music_image, size=(150, 150))
                cover_text = ""
            except:
                music_image = None
                cover_image = None
                cover_text = "No Image Found"
            if self.config_cover_image_label:
                self.config_cover_image_label.destroy()
            self.config_cover_image_label = customtkinter.CTkLabel(self.current_page, width=150, height=150, image=cover_image, text=cover_text, font=self.text_font)
            self.config_cover_image_label.place(x=350, y=85)

            # Reset variables
            self.beatList = []
            self.loop_start = 0
            self.loop_end = self.song_duration
            self.full_cassette_cover = None

    # Use extracted metadata as the main song title and author
    # if the checkbox is checked
    def on_extracted_data_checkbox_pressed(self):
        if self.extracted_title_author_checkbox.get() == 1:
            self.song_title = self.extracted_song_title
            self.song_author = self.extracted_song_author
            self.song_name_entry.configure(state="disabled")
            self.song_author_entry.configure(state="disabled")
            self.using_extracted_data = True
        else:
            self.song_title = self.song_name_entry.get()
            self.song_author = self.song_author_entry.get()
            self.song_name_entry.configure(state="normal")
            self.song_author_entry.configure(state="normal")
            self.using_extracted_data = False

    # Preview the selected song if the preview song checkbox is checked
    def preview_song(self):
        if self.config_preview_song_checkbox.get() == 1:
            mixer.music.unload()
            mixer.music.load(self.current_music_file)
            mixer.music.set_volume(0.8)
            if self.current_music_file:
                mixer.music.play()
        else:
            if mixer.music.get_busy():
                mixer.music.stop()
            mixer.music.set_volume(1)


    # Page that lets you set a custom cassette cover
    def visual_page(self):
        # Reset page area
        visual_frame = self.start_new_page()

        # Buttons for selecting a cassette cover manually or from the metadata
        image_path_button = customtkinter.CTkButton(visual_frame, width=100, height=30, text="Select Image File", border_width=0, corner_radius=5, font=self.text_font, command=self.select_cover_file)
        image_path_button.place(x=45, y=20)
        
        self.image_data_button = customtkinter.CTkButton(visual_frame, width=100, height=30, text="Use Album Cover", border_width=0, corner_radius=5, font=self.text_font, state="disabled", command=self.select_album_cover)
        self.image_data_button.place(x=45, y=60)
        # Only allow the user to use the album cover button if the metadata contained a music file
        if os.path.exists("ffmpeg\\image_output\\cover.jpg") and self.current_cover != "ffmpeg\\image_output\\cover.jpg":
            self.image_data_button.configure(state="normal")

        # Image of the cassette with cover preview
        cassette_cover_overlay_img = customtkinter.CTkImage(dark_image=self.cassette_cover_overlay, light_image=self.cassette_cover_overlay, size=self.cassette_cover_overlay.size)
        self.cassette_img_label = customtkinter.CTkLabel(visual_frame, width=self.cassette_cover_overlay.width/2, height=self.cassette_cover_overlay.height/2, image=cassette_cover_overlay_img, text="")
        self.cassette_img_label.place(x=350, y=25)

        # Entries for the position of the custom image
        self.cassette_img_x_entry = customtkinter.CTkEntry(visual_frame, font=self.text_font, width=130, state="disabled")
        self.cassette_img_x_entry.place(x=350, y=250)
        self.cassette_img_y_entry = customtkinter.CTkEntry(visual_frame, font=self.text_font, width=130, state="disabled")
        self.cassette_img_y_entry.place(x=500, y=250)

        cassette_x_label = customtkinter.CTkLabel(visual_frame, font=self.text_font, width=130, text="X")
        cassette_x_label.place(x=350, y=220)
        cassette_y_label = customtkinter.CTkLabel(visual_frame, font=self.text_font, width=130, text="Y")
        cassette_y_label.place(x=500, y=220)
        
        # UI for coloring cassette color
        change_color_button = customtkinter.CTkButton(visual_frame, width=100, height=30, text="Change Color", border_width=0, corner_radius=5, font=self.text_font, command=self.change_color)
        change_color_button.place(x=45, y=250)

        reset_color_button = customtkinter.CTkButton(visual_frame, width=100, height=30, text="Reset Color", border_width=0, corner_radius=5, font=self.text_font, command=self.reset_color)
        reset_color_button.place(x=45, y=290)

        self.color_display = customtkinter.CTkFrame(visual_frame, width=30, height=30, fg_color=self.hex_color, border_color="#FFFFFF", border_width=2)
        self.color_display.place(x=175, y=250)

        # Button to move custom image based on the entries' values
        self.move_cassette_button = customtkinter.CTkButton(visual_frame, width=280, height=30, text="Move", border_width=0, corner_radius=5, font=self.text_font, state="disabled", command=self.move_button_pressed)
        self.move_cassette_button.place(x=350, y=290)

        # Checkbox to use the default cassette cover, ignoring other changes within the visual menu
        self.use_default_checkbox = customtkinter.CTkCheckBox(visual_frame, text="Use Default Cover", font=self.text_font, border_width=1, corner_radius=0, command=self.use_default)
        self.use_default_checkbox.place(x=50, y=100)

        # Additional info for user
        cassette_image_notif = customtkinter.CTkLabel(visual_frame, font=self.text_font, width=130, text="Use an image with a 1:1 aspect ratio.")
        cassette_image_notif.place(x=210, y=350)
        cassette_color_notif = customtkinter.CTkLabel(visual_frame, font=self.text_font, width=130, text="Add -potato_mode to your game launch\nsettings to make colors more vibrant.\nDespite the name, it may look better to some people.")
        cassette_color_notif.place(x=145, y=390)

        # Handles returning screen to previous state after the user clicks off the screen and then returns
        if self.full_cassette_cover:
            self.custom_cassette_cover()
        if self.default_cover:
            self.use_default_checkbox.select()

    # Handles changing if the user wants to use a default cassette cover
    def use_default(self):
        if self.use_default_checkbox.get() == 1:
            self.default_cover = True
        else:
            self.default_cover = False

    # Handles the user selecting a file for the custom cassette cover
    def select_cover_file(self):
        previous_cover = self.current_cover
        self.current_cover = customtkinter.filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")], initialdir = os.path.join(os.path.expanduser("~"), "Downloads"))
        if self.current_cover:
            self.cover_pos_x = 0
            self.cover_pos_y = 0
            self.cassette_img_x_entry.delete(0, len(self.cassette_img_x_entry.get()))
            self.cassette_img_y_entry.delete(0, len(self.cassette_img_y_entry.get()))
            if os.path.exists("ffmpeg\\image_output\\cover.jpg"):
                self.image_data_button.configure(state="normal")
            self.custom_cassette_cover()
        else:
            self.current_cover = previous_cover
        

    # Handles the user selecting the song metadata for the custom cassette cover
    def select_album_cover(self):
        self.current_cover = "ffmpeg\\image_output\\cover.jpg"
        self.cover_pos_x = 0
        self.cover_pos_y = 0
        self.cassette_img_x_entry.delete(0, len(self.cassette_img_x_entry.get()))
        self.cassette_img_y_entry.delete(0, len(self.cassette_img_y_entry.get()))
        self.image_data_button.configure(state="disabled")
        self.custom_cassette_cover()

    # Handles positioning the custom image within the small custom cassette template
    # and converting it over to a full sized one
    def custom_cassette_cover(self):
        
        # Allows the user to move the image within the cassette
        self.cassette_img_x_entry.configure(state="normal")
        self.cassette_img_y_entry.configure(state="normal")
        self.move_cassette_button.configure(state="normal")
       
        # Creating temporary image objects and converting and resizing them.
        temp_base = Image.new("RGB", self.cassette_cover_overlay.size, (255, 255, 255))
        temp_img = Image.open(self.current_cover).convert("RGBA").resize((280, 280))
        
        # Pasting the custom image under the cassette overlay
        temp_base.paste(temp_img, (self.cover_pos_x, self.cover_pos_y), temp_img)
        temp_base.paste(self.cassette_cover_overlay, (0, 0), self.cassette_cover_overlay)

        # Displays custom cassette cover preview
        cassette_img = customtkinter.CTkImage(dark_image=temp_base, light_image=temp_base, size=self.cassette_cover_overlay.size)
        self.cassette_img_label.destroy()
        self.cassette_img_label = customtkinter.CTkLabel(self.current_page, width=self.cassette_cover_overlay.width/2, height=self.cassette_cover_overlay.height/2, image=cassette_img, text="")
        self.cassette_img_label.place(x=350, y=25)
        
        # Converting the custom cassette cover preview to a full size one
        full_cassette_overlay = Image.open("images\\CustomCassetteTemplate.png")
        full_temp_base = Image.new("RGB", full_cassette_overlay.size, (255, 255, 255))
        left = -self.cover_pos_x 
        right = -self.cover_pos_x + 280
        top = -self.cover_pos_y
        bottom = -self.cover_pos_y + 178
        temp_img = temp_img.crop((left, top, right, bottom))
        temp_img = temp_img.resize((280, 280))
        temp_img = temp_img.rotate(-90)
        temp_img = temp_img.resize((178, 280))
        full_cassette_pos = (314-int(self.cover_pos_y/100), 38+int(self.cover_pos_x/100))
        full_cassette_pos2 = (314-int(self.cover_pos_y/100)-179, 38+int(self.cover_pos_x/100))
        full_temp_base.paste(temp_img, full_cassette_pos, temp_img)
        temp_img = temp_img.rotate(180)
        full_temp_base.paste(temp_img, full_cassette_pos2, temp_img)
        full_temp_base.paste(full_cassette_overlay, (0, 0), full_cassette_overlay)
        self.full_cassette_cover = full_temp_base.copy()
    
    # Resets color back to default white
    def reset_color(self):
        self.hex_color = "#FFFFFF"
        self.cover_red = 255
        self.cover_green = 255
        self.cover_blue = 255
        self.color_display.configure(fg_color=self.hex_color)


    # Handles the changing and displaying of cassette cover color
    def change_color(self):
        # Gets hex code from color picker and converts to RGB
        prev_hex_color = self.hex_color
        self.hex_color = CTkColorPicker.AskColor().get()
        if self.hex_color:
            rgb_value = tuple(int(self.hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            self.cover_red = rgb_value[0]
            self.cover_green = rgb_value[1]
            self.cover_blue = rgb_value[2]
            self.color_display.configure(fg_color=self.hex_color)
        else:
            self.hex_color = prev_hex_color

    # Moves the position of the custom image within the cassette overlay
    def move_button_pressed(self):
        if self.cassette_img_x_entry.get() != "":
            self.cover_pos_x = int(self.cassette_img_x_entry.get())
        if self.cassette_img_y_entry.get() != "":
            self.cover_pos_y = int(self.cassette_img_y_entry.get())
        self.custom_cassette_cover()
    
    # Page that handles a song's beats and looping
    def track_page(self):
        # Reset page area
        track_frame = self.start_new_page()

        # Button to Find a song's beats, only avaliable to press 
        # when the user has selected a song in the config page
        self.find_beat_button = customtkinter.CTkButton(track_frame, width=100, height=30, text="Find Beats", border_width=0, corner_radius=5, font=self.text_font, state="disabled", command=self.start_beats_threading)
        self.find_beat_button.place(x=45, y=20)
        if self.current_music_file:
            self.find_beat_button.configure(state="normal")
        
        # Button to 
        self.preview_beat_checkbox = customtkinter.CTkCheckBox(track_frame, width=100, height=30, text="Preview Beats", font=self.text_font, border_width=1, corner_radius=0, state="disabled", command=self.preview_beats)
        self.preview_beat_checkbox.place(x=160, y=20)

        # Label that tells the user the number of beats it has found if it has found any yet
        self.find_beat_label = customtkinter.CTkLabel(track_frame, width=100, height=30, text="Beats Not Found", font=self.text_font)
        self.find_beat_label.place(x=50, y=50)

        # List of beats with scrolling functionality
        self.beat_list_textbox = customtkinter.CTkTextbox(self.current_page, activate_scrollbars=False, font=self.text_font, state="disabled")
        self.beat_list_textbox.place(x=45, y=80)
        self.beat_list_scrollbar = customtkinter.CTkScrollbar(self.current_page, command=self.beat_list_textbox.yview)
        self.beat_list_scrollbar.place(x=250, y=80)

        # Handles returning screen to previous state after the user clicks off the screen and then returns
        if self.beatList:
            self.find_beat_label.configure(text="Found  " + str(len(self.beatList)) + "  Beats")
            self.preview_beat_checkbox.configure(state="normal")
            self.beat_list_textbox.configure(state="normal")
            self.beat_list_textbox.insert('end', self.viewable_beats)
            self.beat_list_textbox.configure(state="disable")
            self.beat_list_textbox.configure(yscrollcommand=self.beat_list_scrollbar.set)


    def start_beats_threading(self):

        self.progress_bar = customtkinter.CTkProgressBar(self, orientation="horizontal", mode="indeterminate")
        self.progress_bar.place(x=196, y=300)
        self.progress_bar.set(0)
        self.progress_bar.start()

        self.progress_label = customtkinter.CTkLabel(self.current_page, width=self.progress_bar.cget("width"), height=30, text="Finding Beats", font=self.text_font)
        self.progress_label.place(x=45, y=310)

        # Creates a seperate thread for finding beats so the application doesn't freeze
        beats_thread = threading.Thread(target=self.find_beats)
        beats_thread.start()
        

    def find_beats(self):
        self.disable_interactables()
        # Runs the Essentia beat tracker with the current song to automatically find all of the beat positions in the song
        self.run_command('beat_finder\\essentia_streaming_beattracker_multifeature_mirex2013.exe "' + self.current_music_file + '" beat_finder\\output\\beat.txt')

        # Formats the data from the beat tracker to be able to use as a list of integers
        with open("beat_finder\\output\\beat.txt", "r") as beats:
            self.beatList = beats.readlines()
        new_beats = ""
        self.num_beats = len(self.beatList)
        for i in range(self.num_beats):
            if i != len(self.beatList)-1:
                new_beats += self.beatList[i].rstrip() + ",\n"
            else:
                new_beats += self.beatList[i].rstrip()
        with open("beat_finder\\output\\beat.txt", "w") as beats:
            beats.write(new_beats)
        
        # Show the number of beats found on the beat label
        self.find_beat_label.configure(text="Found  " + str(len(self.beatList)) + "  Beats")

        beats_thread = threading.Thread(target=self.show_beat_list)
        beats_thread.start()
        beats_thread.join()
        self.progress_label.destroy()
        self.progress_bar.destroy()

    # Creates list of beats in the scrollable textbox
    def show_beat_list(self):
        self.progress_label.configure(text="Creating List")

        self.viewable_beats = "Beat      Time\n"
        for i in range(self.num_beats):
            self.viewable_beats += str(i+1) + "                  " + self.beatList[i] + "\n"
        self.beat_list_textbox.configure(state="normal")
        self.beat_list_textbox.delete('0.0', 'end')
        self.beat_list_textbox.insert('end', self.viewable_beats)
        self.beat_list_textbox.configure(state="disabled")
        self.beat_list_textbox.configure(yscrollcommand=self.beat_list_scrollbar.set)
        beats_thread = threading.Thread(target=self.create_beat_preview)
        beats_thread.start()
        

    # Creates a song file with beat sounds
    def create_beat_preview(self):
        self.progress_label.configure(text="Creating Beat Preview")

        if os.path.exists("beat_previewer\\wav_song\\input.wav"):
            os.remove("beat_previewer\\wav_song\\input.wav")
        self.run_command("ffmpeg\\ffmpeg.exe -i \"" + self.current_music_file + "\" beat_previewer\\wav_song\\input.wav")
        
        main_song = AudioSegment.from_file("beat_previewer\\wav_song\\input.wav", format="wav")
        beat_sound = AudioSegment.from_file("beat_previewer\\beat_sound\\beat.wav", format="wav")

        overlay_track = AudioSegment.silent(duration=len(main_song))

        for beat_pos in self.beatList:
            overlay_track = overlay_track.overlay(beat_sound, position=float(beat_pos)*1000)
        
        main_song = main_song.overlay(overlay_track, gain_during_overlay=-3)

        mixer.music.unload()
        main_song.export("beat_previewer\\output\\output.wav", format="wav")
        self.preview_beat_checkbox.configure(state="normal")
        self.re_enable_interactables()
        self.progress_bar.stop()

    # Plays song with beat sounds
    def preview_beats(self):
        if self.preview_beat_checkbox.get() == 1:
            mixer.music.unload()
            mixer.music.load("beat_previewer\\output\\output.wav")
            mixer.music.play()
        else:
            mixer.music.stop()



    # Handles applying a loop and cases where the set
    # time for the loop is outside of the possible range
    def apply_loop(self):
        try:
            self.loop_start = float(self.beatList[int(self.loop_start_entry.get())-1])
            self.loop_end = float(self.beatList[int(self.loop_end_entry.get())-1])
            if self.loop_start < self.loop_end and self.loop_end <= float(self.song_duration):
                self.preview_loop_button.configure(state="normal")
            else:
                self.loop_start = None
                self.loop_end = None
                self.preview_loop_button.configure(state="disabled")
        except:
            self.loop_start = None
            self.loop_end = None
            self.preview_loop_button.configure(state="disabled")
    
    # Plays the end and a little of the start of the set loop of the song
    def preview_loop(self):
        if self.current_music_file and not mixer.music.get_busy():
                mixer.music.play(start=self.loop_end-2)
                self.after(2000, self.new_loop)

    # stops and restarts the loop to prevent the 
    # music from overlapping when clicked multiple times in quick sucession
    def new_loop(self):
        mixer.music.stop()
        mixer.music.play(start=self.loop_start)
        self.after(2000, mixer.music.stop)

    # Page for exporting the cassette as a .robobeat file
    def export_page(self):
        # Reset page area
        export_frame = self.start_new_page()
        
        # Handles which title and author to use 
        # if the checkbox for using metadata is checked or not
        if self.extracted_title_author_checkbox:
            if self.extracted_title_author_checkbox.get() == 0:
                self.song_title = self.entered_song_title
            if self.extracted_title_author_checkbox.get() == 0:
                self.song_author = self.entered_song_author

        # Button to export, only avaliable to press if all needed conditions are met
        export_button = customtkinter.CTkButton(export_frame, width=100, height=30, text="Export .robobeat", border_width=0, corner_radius=5, font=self.text_font, command=self.export_robobeat_file, state="disabled")
        export_button.place(x=300, y=200)
        if self.current_music_file and self.song_duration and self.song_author and self.song_title and (self.full_cassette_cover or self.default_cover) and self.beatList:
            export_button.configure(state="normal")

    # Handles combining all nessesary data into a .robobeat file
    def export_robobeat_file(self):
        # Asks user for destination of file
        exported_filename = customtkinter.filedialog.askdirectory(initialdir=os.path.join(os.path.expanduser("~"), "Downloads"))

        if not os.path.exists(os.path.join(exported_filename, self.song_title + ".robobeat")):
            exported_filename = os.path.join(exported_filename, self.song_title + ".robobeat")
        else:
            i = 0
            while os.path.isdir(exported_filename):
                i += 1
                if not os.path.exists(os.path.join(exported_filename, self.song_title + "(" + str(i) + ").robobeat")):
                    exported_filename = os.path.join(exported_filename, self.song_title + "(" + str(i) + ").robobeat")

        # Runs the following only if the user has selected a destination
        if exported_filename:
            # Converts .flac music files into .wav as robobeat does not support .flac
            if self.current_music_file.endswith(".flac"):
                self.run_command("ffmpeg\\ffmpeg.exe -i \"" + self.current_music_file + "\" ffmpeg\\flac_convert_output\\output.wav")
                self.current_music_file = "ffmpeg\\flac_convert_output\\output.wav"

            # Generates a random internal name for the cassette, 
            # similar to robobeat's internal naming system
            letters = string.ascii_lowercase
            internal_name = "cassettify_"
            for i in range(30):
                internal_name += random.choice(letters)

            # Creates a new name for the music file based on the internal name
            # and adds the music file's extension to it, then copies the song into
            # a temporary folder with that name
            original_soundfilename = os.path.basename(self.current_music_file)
            soundfilename_extension = "." + original_soundfilename.split(".")[-1]
            exported_soundfilename = internal_name + "_audio" + soundfilename_extension
            shutil.copyfile(self.current_music_file, "temp\\" + exported_soundfilename)

            # decides on the config file the .robobeat file will use depending on if
            # the user is using a custom cassette cover or not
            if self.default_cover:
                config_file_loc = "config_template\\cassetteConfigP2.json"
            else:
                config_file_loc = "config_template\\cassetteConfigP2CustomVisuals.json"
                # if the user is using a custom cover, copy that into the temp file
                # with the internal name
                self.full_cassette_cover.save("temp\\" + internal_name + ".png")
            
            # location for extra data of the config file that is added on before
            # copying the config file to the temp folder
            config_metadata_loc = "config_template\\cassetteConfigP1.json"
            
            # Loads and changes the data in the config file based on the user's inputs
            with open(config_file_loc, "r") as j:
                loaded_config = json.load(j)
            loaded_config["InternalName"] = internal_name
            loaded_config["File"]["InternalName"] = internal_name
            loaded_config["File"]["Info"]["PathToAudioClip"] = os.path.expanduser("~") + "/AppData/LocalLow/Inzanity/ROBOBEAT/cassette_audio/" + exported_soundfilename
            loaded_config["File"]["Info"]["FileName"] = exported_soundfilename
            loaded_config["File"]["Info"]["LengthOfClip"] = float(self.song_duration)
            loaded_config["File"]["Info"]["PublicName"] = self.song_title
            loaded_config["File"]["Info"]["ArtistName"] = self.song_author
            if not self.loop_start:
                self.loop_start = 0
            if not self.loop_end:
                self.loop_end = self.song_duration
            loaded_config["File"]["Beat"]["StartTime"] = float(self.loop_start)
            loaded_config["File"]["Beat"]["EndTime"] = float(self.loop_end)
            # Handles the looping process and deleting beats outside of the loop
            float_beat_list = self.beatList.copy()
            if not self.loop_start == 0.0 and not self.loop_end == float(self.song_duration):
                start_pos = 0
                end_pos = 0
                rounded_float_beat_list = []
                for i in range(len(self.beatList)):
                    float_beat_list[i] = float(self.beatList[i].rstrip())
                    rounded_float_beat_list.append(round(float_beat_list[i], 2))
                float_beat_list = float_beat_list[rounded_float_beat_list.index(round(loaded_config["File"]["Beat"]["StartTime"], 2)) + 1:rounded_float_beat_list.index(round(loaded_config["File"]["Beat"]["EndTime"], 2)) + 1]
                # Adds to the end time by a small amount to prevent the last beat from being behind the loop end point
                loaded_config["File"]["Beat"]["EndTime"] += 0.001
                self.num_beats = len(float_beat_list)
            else:
                for i in range(len(self.beatList)):
                    float_beat_list[i] = float(self.beatList[i].rstrip())   
            loaded_config["File"]["Beat"]["NumberOfBeats"] = self.num_beats
            loaded_config["File"]["Beat"]["Beats"] = float_beat_list
            if not self.default_cover:
                loaded_config["File"]["Visuals"]["CassetteTextureInternalName"] = internal_name + ".png"
            loaded_config["File"]["Visuals"]["CassetteColor"]["r"] = float(self.cover_red)/255
            loaded_config["File"]["Visuals"]["CassetteColor"]["g"] = float(self.cover_green)/255
            loaded_config["File"]["Visuals"]["CassetteColor"]["b"] = float(self.cover_blue)/255
            # Copies the two parts of the config together, 
            # the main config and extra data and makes the
            # .cassette file containing data about the cassette
            config_str_part = json.dumps(loaded_config, indent=4)
            with open(config_metadata_loc, "r") as j:
                full_config = j.read() + config_str_part
            final_config_path = "temp\\" + internal_name + ".cassette"
            shutil.copyfile("config_template\\emptyFile.json", final_config_path)
            with open(final_config_path, "a") as j:
                j.write(full_config)
            
            # Converts the config file to use Unix 
            # line endings, the same as robobeat does
            WINDOWS_LINE_ENDING = b'\r\n'
            UNIX_LINE_ENDING = b'\n'
            with open(final_config_path, 'rb') as open_file:
                content = open_file.read()
            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
            with open(final_config_path, 'wb') as open_file:
                open_file.write(content)
            
            # Creates a .zip file and packages all data from the temp folder,
            # Then renames the .zip folder into a .robobeat folder and finishes
            shutil.make_archive(exported_filename, 'zip', "temp\\")
            os.rename(exported_filename + ".zip", exported_filename)
            for temp_file in os.listdir("temp"):
                os.remove("temp\\" + temp_file)
            if os.path.exists("ffmpeg\\flac_convert_output\\output.wav"):
                os.remove("ffmpeg\\flac_convert_output\\output.wav")
            self.finished()
        
    # Communicates to the user that exporting has finished
    def finished(self):
        finish_page = self.start_new_page()
        finish_label = customtkinter.CTkLabel(finish_page, font=self.text_font, width=130, text="Finished!")
        finish_label.place(x=300, y=220)
            
    # Returns a new page and removes the old one if any
    def start_new_page(self):
        if self.song_name_entry and self.song_author_entry:
            self.entered_song_title = self.song_name_entry.get()
            self.entered_song_author = self.song_author_entry.get()
            self.song_name_entry = None
            self.song_author_entry = None
        if self.loop_start_entry and self.loop_end_entry:
            self.entered_start_loop = self.loop_start_entry.get()
            self.entered_end_loop = self.loop_end_entry.get()
            self.loop_start_entry = None
            self.loop_end_entry = None
        self.remove_current_page()
        new_frame = customtkinter.CTkFrame(self, corner_radius=0, width=4850, height=5000, fg_color="transparent")
        new_frame.place(x=150, y=0)
        self.current_page = new_frame
        return new_frame
    
    # Removes the current page if there is one
    def remove_current_page(self):
        if self.current_page is not None:
            self.current_page.destroy()
        self.current_page = None
        mixer.music.unload()
        if mixer.music.get_busy():
                mixer.music.stop()
    
    def disable_interactables(self):
        # Disables all interactable widgets
        self.child_states = []
        for frame in self.winfo_children():
            for widget in frame.winfo_children():
                try:
                    if widget.cget("state") == "normal" and type(widget) != customtkinter.CTkLabel:
                        widget.configure(state="disabled")
                        self.child_states.append(widget)
                except ValueError:
                    pass

    def add_disabled_interactables(self, interactables:tuple):
        # Add a list of interactable objects to disable
        # and add to list to be re-enabled later
        for interactable in interactables:
            try:
                interactable.configure(state="disabled")
                self.child_states.append(interactable)
            except ValueError:
                print("Item", str(interactable), "does not have a \"disabled\" state.")

    def re_enable_interactables(self):
        # Re-enable disabled interaactable widgets
        for widget in self.child_states:
            try:
                widget.configure(state="normal")
            except:
                pass
        

    # Handles running and returning console commands
    def run_command(self,cmd):
        # Runs command and returns interactable states to normals
        try:
            result = subprocess.check_output(cmd, shell=True, universal_newlines=True, encoding="utf-8")
            return result.strip()
        except subprocess.CalledProcessError as error:
            return error.output.strip()

new_app = App()
new_app.mainloop()
if mixer.music.get_busy():
    mixer.music.stop()
mixer.music.unload()
clean()