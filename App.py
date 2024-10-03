import customtkinter
from PIL import Image
import os, shutil
import subprocess
from pygame import mixer
import pygame
import json
import random, string

pygame.init()

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("theme/cassettify_theme.json")
if os.path.exists("ffmpeg\\image_output\\cover.jpg"):
    os.remove("ffmpeg\\image_output\\cover.jpg")
if os.path.exists("beat_finder\\output\\beat.txt"):
    os.remove("beat_finder\\output\\beat.txt")
if os.path.exists("ffmpeg\\flac_convert_output\\output.wav"):
    os.remove("ffmpeg\\flac_convert_output\\output.wav")
for temp_file in os.listdir("temp"):
    os.remove("temp\\" + temp_file)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x600")
        self.title("Cassettify")
        self.after(201, lambda :self.iconbitmap("images/icon.ico"))
        customtkinter.FontManager.load_font("font/pixelated/pixelated.ttf")
        self.text_font = customtkinter.CTkFont("Pixelated Regular", 20)
        # self.text_font = customtkinter.CTkFont("Bahnschrift", 16)
        self.resizable = False
        self.sidebar()
        self.current_page = None
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
        self.default_cover = False
        self.full_cassette_cover = None

        self.loop_start = 0
        self.loop_end = 0
        self.num_beats = 0
        self.beatList=[]

        self.viewable_beats = None
        self.beat_list_textbox = None
        self.beat_list_scrollbar = None

        self.entered_start_loop = None
        self.entered_end_loop = None
        self.loop_start_entry = None
        self.loop_end_entry = None


    def sidebar(self):
        sidebar_frame = customtkinter.CTkFrame(self, corner_radius=0, width=150, height=5000)
        sidebar_frame.place(x=0, y=0)

        icon_image = Image.open("images\\icon.png")
        icon_image = icon_image.convert("P", palette=Image.ADAPTIVE, colors=10, dither=Image.FLOYDSTEINBERG)
        sidebar_icon = customtkinter.CTkImage(light_image=icon_image, dark_image=icon_image, size=(100, 100))
        sidebar_icon_label = customtkinter.CTkLabel(sidebar_frame, width=75, height=75, image=sidebar_icon, text="")
        sidebar_icon_label.place(x=25, y=25)

        title_label = customtkinter.CTkLabel(sidebar_frame, width=149.5, text="CASSETTIFY", font=self.text_font)
        title_label.place(x=0, y=10)

        config = customtkinter.CTkButton(sidebar_frame, width=149.5, height=30, text="Config", border_width=0, corner_radius=0, font=self.text_font, command=self.config_page)
        config.place(x=0, y=115)
        visuals = customtkinter.CTkButton(sidebar_frame, width=149.5, height=30, text="Visuals", border_width=0, corner_radius=0, font=self.text_font, command=self.visual_page)
        visuals.place(x=0, y=145)
        track = customtkinter.CTkButton(sidebar_frame, width=149.5, height=30, text="Track", border_width=0, corner_radius=0, font=self.text_font, command=self.track_page)
        track.place(x=0, y=175)
        export = customtkinter.CTkButton(sidebar_frame, width=149.5, height=30, text="Export", border_width=0, corner_radius=0, font=self.text_font, command=self.export_page)
        export.place(x=0, y=205)
        

    def config_page(self):
        config_frame = self.start_new_page()

        self.song_name_entry = customtkinter.CTkEntry(config_frame, font=self.text_font)
        self.song_name_entry.place(x=45, y=50)

        song_name_label = customtkinter.CTkLabel(config_frame, text="Title", font=self.text_font)
        song_name_label.place(x=50, y=20)

        self.song_author_entry = customtkinter.CTkEntry(config_frame, font=self.text_font)
        self.song_author_entry.place(x=45, y=130)

        song_author = customtkinter.CTkLabel(config_frame, text="Author", font=self.text_font)
        song_author.place(x=50, y=100)

        config_track = customtkinter.CTkButton(config_frame, width=100, height=30, text="Select Music File", border_width=0, corner_radius=5, font=self.text_font, command=self.select_music_file)
        config_track.place(x=45, y=195)
        
        self.config_track_filename = customtkinter.CTkLabel(config_frame, text="No File Selected", font=self.text_font)
        self.config_track_filename.place(x=50, y=230)

        self.extracted_title_author_checkbox = customtkinter.CTkCheckBox(config_frame, text="Use Extracted Title & Author", font=self.text_font, border_width=1, corner_radius=0, state="disabled", command=self.on_extracted_data_checkbox_pressed)
        self.extracted_title_author_checkbox.place(x=50, y = 290)
        
        self.config_preview_song_checkbox = customtkinter.CTkCheckBox(config_frame, text="Preview Song", font=self.text_font, border_width=1, corner_radius=0, command=self.preview_song, state="disabled")
        self.config_preview_song_checkbox.place(x=50, y = 350)

        if self.current_music_file:
            self.config_track_filename.configure(text=os.path.basename(self.current_music_file))
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
            

    def select_music_file(self):
        self.current_music_file = customtkinter.filedialog.askopenfilename(filetypes=[("Music Files", "*.mp3 *.ogg *.wav *.flac")], initialdir = os.path.join(os.path.expanduser("~"), "Downloads"))
        if self.current_music_file:
            self.song_name_entry.configure(state="normal")
            self.song_author_entry.configure(state="normal")
            self.extracted_title_author_checkbox.deselect()
            self.config_preview_song_checkbox.configure(state="normal")
            if self.config_preview_song_checkbox.get() == 1:
                self.config_preview_song_checkbox.toggle()
            self.config_track_filename.configure(text=os.path.basename(self.current_music_file))
            if os.path.exists("ffmpeg\\image_output\\cover.jpg") and self.current_music_file:
                os.remove("ffmpeg\\image_output\\cover.jpg")
            self.run_command("ffmpeg\\ffmpeg.exe -i \"" + self.current_music_file + "\" -an -c:v copy ffmpeg\\image_output\\cover.jpg")
            self.song_duration = self.run_command("ffmpeg\\ffprobe.exe -i \"" + self.current_music_file + "\" -show_entries format=duration -v quiet -of csv=\"p=0\"")
            self.extracted_song_title = self.run_command("ffmpeg\\ffprobe.exe -v error -show_entries format_tags=title -of default=nw=1:nk=1 \"" + self.current_music_file + "\"")
            self.extracted_song_author = self.run_command("ffmpeg\\ffprobe.exe -v error -show_entries format_tags=artist -of default=nw=1:nk=1 \"" + self.current_music_file + "\"")
            self.loop_end = self.song_duration

            if self.extracted_song_author and self.extracted_song_title:
                self.extracted_title_author_checkbox.configure(state="normal")
            else: 
                self.extracted_title_author_checkbox.configure(state="disabled")

            if not self.extracted_song_author:
                self.extracted_song_author = "No Author Found"
            
            if not self.extracted_song_title:
                self.extracted_song_title = "No Title Found"

            if self.extracted_song_title_label:
                self.extracted_song_title_label.destroy()
            self.extracted_song_title_label = customtkinter.CTkLabel(self.current_page, text=self.extracted_song_title, font=self.text_font)
            self.extracted_song_title_label.place(x=350, y=50)

            if self.extracted_song_author_label:
                self.extracted_song_author_label.destroy()
            self.extracted_song_author_label = customtkinter.CTkLabel(self.current_page, text=self.extracted_song_author, font=self.text_font)
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

            self.beatList = []

            self.loop_start = 0
            self.loop_end = self.song_duration

    def visual_page(self):
        visual_frame = self.start_new_page()

        image_path_button = customtkinter.CTkButton(visual_frame, width=100, height=30, text="Select Image File", border_width=0, corner_radius=5, font=self.text_font, command=self.select_cover_file)
        image_path_button.place(x=45, y=20)
        
        image_data_button = customtkinter.CTkButton(visual_frame, width=100, height=30, text="Use Album Cover", border_width=0, corner_radius=5, font=self.text_font, state="disabled", command=self.select_album_cover)
        image_data_button.place(x=45, y=60)
        if os.path.exists("ffmpeg\\image_output\\cover.jpg"):
            image_data_button.configure(state="normal")

        cassette_cover_overlay_img = customtkinter.CTkImage(dark_image=self.cassette_cover_overlay, light_image=self.cassette_cover_overlay, size=self.cassette_cover_overlay.size)
        self.cassette_img_label = customtkinter.CTkLabel(visual_frame, width=self.cassette_cover_overlay.width/2, height=self.cassette_cover_overlay.height/2, image=cassette_cover_overlay_img, text="")
        self.cassette_img_label.place(x=350, y=25)

        self.cassette_img_x_entry = customtkinter.CTkEntry(visual_frame, font=self.text_font, width=130, state="disabled")
        self.cassette_img_x_entry.place(x=350, y=250)
        self.cassette_img_y_entry = customtkinter.CTkEntry(visual_frame, font=self.text_font, width=130, state="disabled")
        self.cassette_img_y_entry.place(x=500, y=250)

        cassette_x_label = customtkinter.CTkLabel(visual_frame, font=self.text_font, width=130, text="X")
        cassette_x_label.place(x=350, y=220)
        cassette_y_label = customtkinter.CTkLabel(visual_frame, font=self.text_font, width=130, text="Y")
        cassette_y_label.place(x=500, y=220)

        self.move_cassette_button = customtkinter.CTkButton(visual_frame, width=280, height=30, text="Move", border_width=0, corner_radius=5, font=self.text_font, state="disabled", command=self.move_button_pressed)
        self.move_cassette_button.place(x=350, y=290)

        self.use_default_checkbox = customtkinter.CTkCheckBox(visual_frame, text="Use Default Cover", font=self.text_font, border_width=1, corner_radius=0, command=self.use_default)
        self.use_default_checkbox.place(x=50, y=100)

        cassette_y_label = customtkinter.CTkLabel(visual_frame, font=self.text_font, width=130, text="Use an image with a 1:1 aspect ratio.")
        cassette_y_label.place(x=345, y=350)

        if self.full_cassette_cover:
            self.custom_cassette_cover()
        if self.default_cover:
            self.use_default_checkbox.select()

    def use_default(self):
        if self.use_default_checkbox.get() == 1:
            self.default_cover = True
        else:
            self.default_cover = False

    def select_cover_file(self):
        self.current_cover = customtkinter.filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")], initialdir = os.path.join(os.path.expanduser("~"), "Downloads"))
        if self.current_cover:
            self.custom_cassette_cover()

    def select_album_cover(self):
        self.current_cover = "ffmpeg\\image_output\\cover.jpg"
        self.custom_cassette_cover()

    def custom_cassette_cover(self):
        self.cassette_img_x_entry.configure(state="normal")
        self.cassette_img_y_entry.configure(state="normal")
        self.move_cassette_button.configure(state="normal")
        temp_base = Image.new("RGB", self.cassette_cover_overlay.size, (255, 255, 255))
        temp_img = Image.open(self.current_cover).convert("RGBA").resize((280, 280))
        temp_base.paste(temp_img, (self.cover_pos_x, self.cover_pos_y), temp_img)
        temp_base.paste(self.cassette_cover_overlay, (0, 0), self.cassette_cover_overlay)
        cassette_img = customtkinter.CTkImage(dark_image=temp_base, light_image=temp_base, size=self.cassette_cover_overlay.size)
        self.cassette_img_label.destroy()
        self.cassette_img_label = customtkinter.CTkLabel(self.current_page, width=self.cassette_cover_overlay.width/2, height=self.cassette_cover_overlay.height/2, image=cassette_img, text="")
        self.cassette_img_label.place(x=350, y=25)
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
        
    def move_button_pressed(self):
        if self.cassette_img_x_entry.get() != "":
            self.cover_pos_x = int(self.cassette_img_x_entry.get())
        if self.cassette_img_y_entry.get() != "":
            self.cover_pos_y = int(self.cassette_img_y_entry.get())
        self.custom_cassette_cover()

    def default_checkbox_pressed(self):
        if self.use_default_checkbox.get() == 1:
            self.default_cover = True
        else:
            self.default_cover = False

    def track_page(self):
        track_frame = self.start_new_page()
        self.find_beat_button = customtkinter.CTkButton(track_frame, width=100, height=30, text="Find Beats", border_width=0, corner_radius=5, font=self.text_font, state="disabled", command=self.find_beats)
        self.find_beat_button.place(x=45, y=20)
        if self.current_music_file:
            self.find_beat_button.configure(state="normal")
        
        self.find_beat_label = customtkinter.CTkLabel(track_frame, width=100, height=30, text="Beats Not Found", font=self.text_font)
        self.find_beat_label.place(x=50, y=50)

        looping_label = customtkinter.CTkLabel(track_frame, width=100, height=30, text="Looping (Under Construction, Does Nothing to Final Cassette)", font=self.text_font)
        looping_label.place(x=200, y=20)

        loop_start_label = customtkinter.CTkLabel(track_frame, width=100, height=30, text="Start Beat #", font=self.text_font)
        loop_start_label.place(x=325, y=50)

        loop_end_label = customtkinter.CTkLabel(track_frame, width=100, height=30, text="End Beat #", font=self.text_font)
        loop_end_label.place(x=475, y=50)

        self.loop_start_entry = customtkinter.CTkEntry(track_frame, font=self.text_font, width=50, state="disabled")
        self.loop_start_entry.place(x=350, y=80)

        self.loop_end_entry = customtkinter.CTkEntry(track_frame, font=self.text_font, width=50, state="disabled")
        self.loop_end_entry.place(x=500, y=80)

        self.apply_loop_button = customtkinter.CTkButton(track_frame, width=100, height=30, text="Apply Loop", border_width=0, corner_radius=5, font=self.text_font, state="disabled", command=self.apply_loop)
        self.apply_loop_button.place(x=400, y=140)

        self.preview_loop_button = customtkinter.CTkButton(track_frame, width=100, height=30, text="Preview Loop", font=self.text_font, border_width=0, corner_radius=5, state="disabled", command=self.preview_loop)
        self.preview_loop_button.place(x=390, y=200)

        if self.beatList:
            self.find_beat_label.configure(text="Found  " + str(len(self.beatList)) + "  Beats")
            self.apply_loop_button.configure(state="normal")
            self.loop_end_entry.configure(state="normal")
            self.loop_start_entry.configure(state="normal")
            self.preview_loop_button.configure(state="normal")
            self.loop_start_entry.insert("end", self.entered_start_loop)
            self.loop_end_entry.insert("end", self.entered_end_loop )
            self.beat_list_textbox = customtkinter.CTkTextbox(self.current_page, activate_scrollbars=False, font=self.text_font)
            for i in range(self.num_beats):
                self.viewable_beats += str(i+1) + "                  " + self.beatList[i] + "\n"
            self.beat_list_textbox.insert('end', self.viewable_beats)
            self.beat_list_textbox.configure(state="disable")
            self.beat_list_textbox.place(x=45, y=100)
            
            self.beat_list_scrollbar = customtkinter.CTkScrollbar(self.current_page, command=self.beat_list_textbox.yview)
            self.beat_list_scrollbar.place(x=250, y=100)

            self.beat_list_textbox.configure(yscrollcommand=self.beat_list_scrollbar.set)


    def find_beats(self):
        self.run_command('beat_finder\\essentia_streaming_beattracker_multifeature_mirex2013.exe "' + self.current_music_file + '" beat_finder\\output\\beat.txt')
        with open("beat_finder\\output\\beat.txt", "r") as beats:
            self.beatList = beats.readlines()
        new_beats = ""
        self.viewable_beats = "Beat      Time\n"
        self.num_beats = len(self.beatList)
        for i in range(self.num_beats):
            if i != len(self.beatList)-1:
                new_beats += self.beatList[i].rstrip() + ",\n"
            else:
                new_beats += self.beatList[i].rstrip()
        with open("beat_finder\\output\\beat.txt", "w") as beats:
            beats.write(new_beats)
        self.find_beat_label.configure(text="Found  " + str(len(self.beatList)) + "  Beats")
        self.apply_loop_button.configure(state="normal")
        self.loop_end_entry.configure(state="normal")
        self.loop_start_entry.configure(state="normal")
        if self.beat_list_textbox and self.beat_list_scrollbar:
            self.beat_list_textbox.destroy()
            self.beat_list_scrollbar.destroy()
        self.beat_list_textbox = customtkinter.CTkTextbox(self.current_page, activate_scrollbars=False, font=self.text_font)
        for i in range(self.num_beats):
            self.viewable_beats += str(i+1) + "                  " + self.beatList[i] + "\n"
        self.beat_list_textbox.insert('end', self.viewable_beats)
        self.beat_list_textbox.configure(state="disable")
        self.beat_list_textbox.place(x=45, y=100)
        
        self.beat_list_scrollbar = customtkinter.CTkScrollbar(self.current_page, command=self.beat_list_textbox.yview)
        self.beat_list_scrollbar.place(x=250, y=100)

        self.beat_list_textbox.configure(yscrollcommand=self.beat_list_scrollbar.set)


    def apply_loop(self):
        try:
            self.loop_start = float(self.beatList[int(self.loop_start_entry.get())-1])
            self.loop_end = float(self.beatList[int(self.loop_end_entry.get())-1])
            if self.loop_start < self.loop_end and self.loop_end <= float(self.song_duration):
                self.preview_loop_button.configure(state="normal")
            else:
                self.loop_start = 0
                self.loop_end = self.song_duration
                self.preview_loop_button.configure(state="disabled")
        except:
            self.loop_start = 0
            self.loop_end = self.song_duration
            self.preview_loop_button.configure(state="disabled")
    
    def preview_loop(self):
        if self.current_music_file and not mixer.music.get_busy():
                mixer.music.load(self.current_music_file)
                mixer.music.play(start=self.loop_end-2)
                self.after(2000, self.new_loop)

    def new_loop(self):
        mixer.music.stop()
        mixer.music.play(start=self.loop_start)
        self.after(2000, self.end_loop)

    def end_loop(self):
        mixer.music.stop()

    def export_page(self):
        export_frame = self.start_new_page()
        if self.extracted_title_author_checkbox:
            if self.extracted_title_author_checkbox.get() == 0:
                self.song_title = self.entered_song_title
            
            if self.extracted_title_author_checkbox.get() == 0:
                self.song_author = self.entered_song_author

        export_button = customtkinter.CTkButton(export_frame, width=100, height=30, text="Export .robobeat", border_width=0, corner_radius=5, font=self.text_font, command=self.export_robobeat_file, state="disabled")
        export_button.place(x=300, y=200)
        if self.current_music_file and self.song_duration and self.song_author and self.song_title and (self.full_cassette_cover or self.default_cover) and self.beatList:
            export_button.configure(state="normal")

    def export_robobeat_file(self):
        exported_filename = customtkinter.filedialog.asksaveasfilename(filetypes=[("ROBOBEAT File", "*.robobeat")], initialdir = os.path.join(os.path.expanduser("~"), "Downloads"))
        exported_filename = os.path.splitext(exported_filename)[0] + ".robobeat"
        print(exported_filename)
        if exported_filename:
            if self.current_music_file.endswith(".flac"):
                self.run_command("ffmpeg\\ffmpeg.exe -i \"" + self.current_music_file + "\" ffmpeg\\flac_convert_output\\output.wav")
                self.current_music_file = "ffmpeg\\flac_convert_output\\output.wav"
            letters = string.ascii_lowercase
            internal_name = "cassettify_"
            for i in range(30):
                internal_name += random.choice(letters)
            original_soundfilename = os.path.basename(self.current_music_file)
            soundfilename_extension = "." + original_soundfilename.split(".")[-1]
            exported_soundfilename = internal_name + "_audio" + soundfilename_extension
            shutil.copyfile(self.current_music_file, "temp\\" + exported_soundfilename)

            if self.default_cover:
                config_file_loc = "config_template\\cassetteConfigP2.json"
            else:
                config_file_loc = "config_template\\cassetteConfigP2CustomVisuals.json"
                self.full_cassette_cover.save("temp\\" + internal_name + ".png")
            config_metadata_loc = "config_template\\cassetteConfigP1.json"
            with open(config_file_loc, "r") as j:
                loaded_config = json.load(j)
            loaded_config["InternalName"] = internal_name
            loaded_config["File"]["InternalName"] = internal_name
            loaded_config["File"]["Info"]["PathToAudioClip"] = os.path.expanduser("~") + "/AppData/LocalLow/Inzanity/ROBOBEAT/cassette_audio/" + exported_soundfilename
            loaded_config["File"]["Info"]["FileName"] = exported_soundfilename
            loaded_config["File"]["Info"]["LengthOfClip"] = float(self.song_duration)
            loaded_config["File"]["Info"]["PublicName"] = self.song_title
            loaded_config["File"]["Info"]["ArtistName"] = self.song_author
            loaded_config["File"]["Beat"]["StartTime"] = 0.0 # float(self.loop_start)
            loaded_config["File"]["Beat"]["EndTime"] = float(self.song_duration) # float(self.loop_end)
            loaded_config["File"]["Beat"]["NumberOfBeats"] = self.num_beats
            float_beat_list = self.beatList
            for i in range(len(float_beat_list)):
                try:
                    float_beat_list[i] = float(float_beat_list[i].rstrip())
                except:
                    pass
            """try:
                float_beat_list.remove(float(self.loop_start))
            except:
                pass"""
            loaded_config["File"]["Beat"]["Beats"] = float_beat_list
            if not self.default_cover:
                loaded_config["File"]["Visuals"]["CassetteTextureInternalName"] = internal_name + ".png"
            config_str_part = json.dumps(loaded_config, indent=4)
            with open(config_metadata_loc, "r") as j:
                full_config = j.read() + config_str_part
            final_config_path = "temp\\" + internal_name + ".cassette"
            shutil.copyfile("config_template\\emptyFile.json", final_config_path)
            with open(final_config_path, "a") as j:
                j.write(full_config)
            
            WINDOWS_LINE_ENDING = b'\r\n'
            UNIX_LINE_ENDING = b'\n'

            with open(final_config_path, 'rb') as open_file:
                content = open_file.read()

            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

            with open(final_config_path, 'wb') as open_file:
                open_file.write(content)
            shutil.make_archive(exported_filename, 'zip', "temp\\")
            os.rename(exported_filename + ".zip", exported_filename)
            for temp_file in os.listdir("temp"):
                os.remove(os.path.join("temp/" + temp_file))
            self.finished()
        
    
    def finished(self):
        for child in self.winfo_children():
            child.destroy()
        finish_label = customtkinter.CTkLabel(self, font=self.text_font, width=130, text="Finished!")
        finish_label.place(x=430, y=220)
            

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

    def remove_current_page(self):
        if self.current_page is not None:
            self.current_page.destroy()
        self.current_page = None
        if mixer.music.get_busy():
                mixer.music.stop()
    
    def run_command(self,cmd):
        try:
            result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            return result.strip()
        except subprocess.CalledProcessError as error:
            return error.output.strip()
        
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

    def preview_song(self):
        if self.config_preview_song_checkbox.get() == 1:
            if self.current_music_file:
                mixer.music.load(self.current_music_file)
                mixer.music.play()
        else:
            if mixer.music.get_busy():
                mixer.music.stop()




            


new_app = App()
new_app.mainloop()