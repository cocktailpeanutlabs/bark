import gradio as gr
from share_btn import community_icon_html, loading_icon_html, share_js
import os 
import shutil
import torch

#from huggingface_hub import snapshot_download
import numpy as np
from scipy.io import wavfile
from scipy.io.wavfile import write, read
from pydub import AudioSegment

file_upload_available = os.environ.get("ALLOW_FILE_UPLOAD")

print(f"file_upload_available = {file_upload_available}")

import json
with open("characters.json", "r") as file:
    data = json.load(file)
    characters = [
        {
            "image": item["image"],
            "title": item["title"],
            "speaker": item["speaker"]
        }
        for item in data
    ]
    
from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/bark", gpu=torch.cuda.is_available())

def cut_wav(input_path, max_duration):
    # Load the WAV file
    audio = AudioSegment.from_wav(input_path)
    
    # Calculate the duration of the audio
    audio_duration = len(audio) / 1000  # Convert milliseconds to seconds
    
    # Determine the duration to cut (maximum of max_duration and actual audio duration)
    cut_duration = min(max_duration, audio_duration)
    
    # Cut the audio
    cut_audio = audio[:int(cut_duration * 1000)]  # Convert seconds to milliseconds
    
    # Get the input file name without extension
    file_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # Construct the output file path with the original file name and "_cut" suffix
    output_path = f"{file_name}_cut.wav"
    
    # Save the cut audio as a new WAV file
    cut_audio.export(output_path, format="wav")

    return output_path

def load_hidden(audio_in):
    return audio_in

def load_hidden_mic(audio_in):
    print("MICRO IN HAS CHANGED")
    
    library_path = 'bark_voices'  
    folder_name = 'audio-0-100'  
    second_folder_name = 'audio-0-100_cleaned' 
    
    folder_path = os.path.join(library_path, folder_name)
    second_folder_path = os.path.join(library_path, second_folder_name)

    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"Successfully deleted the folder: {folder_path}")
        except OSError as e:
            print(f"Error: {folder_path} - {e.strerror}")
    else:
        print(f"The folder does not exist: {folder_path}")

    if os.path.exists(second_folder_path):
        try:
            shutil.rmtree(second_folder_path)
            print(f"Successfully deleted the folder: {second_folder_path}")
        except OSError as e:
            print(f"Error: {second_folder_path} - {e.strerror}")
    else:
        print(f"The folder does not exist: {second_folder_path}")
    
    return audio_in

def clear_clean_ckeck():
    return False

def wipe_npz_file(folder_path):
    if os.path.exists(folder_path):
        #shutil.rmtree(folder_path)
        print(folder_path)
    else :
        print("path does not exists yet")
    print("YO")
    
def split_process(audio, chosen_out_track):
    os.makedirs("out", exist_ok=True)
    write('test.wav', audio[0], audio[1])
    os.system("python3 -m demucs.separate -n mdx_extra_q -j 4 test.wav -o out")
    #return "./out/mdx_extra_q/test/vocals.wav","./out/mdx_extra_q/test/bass.wav","./out/mdx_extra_q/test/drums.wav","./out/mdx_extra_q/test/other.wav"
    if chosen_out_track == "vocals":
        return "./out/mdx_extra_q/test/vocals.wav"
    elif chosen_out_track == "bass":
        return "./out/mdx_extra_q/test/bass.wav"
    elif chosen_out_track == "drums":
        return "./out/mdx_extra_q/test/drums.wav"
    elif chosen_out_track == "other":
        return "./out/mdx_extra_q/test/other.wav"
    elif chosen_out_track == "all-in":
        return "test.wav"
        
def update_selection(selected_state: gr.SelectData):
    c_image = characters[selected_state.index]["image"]
    c_title = characters[selected_state.index]["title"]
    c_speaker = characters[selected_state.index]["speaker"]

    return c_title, selected_state

    
def infer(prompt, input_wav_file, clean_audio, hidden_numpy_audio):

    if clean_audio is True :
        # Extract the file name without the extension
        new_name = os.path.splitext(os.path.basename(input_wav_file))[0]
        check_name = os.path.join("bark_voices", f"{new_name}_cleaned")
        if os.path.exists(check_name):
            source_path = os.path.join(check_name, f"{new_name}_cleaned.wav")
        else:
            source_path = split_process(hidden_numpy_audio, "vocals")
        
            # Rename the file
            new_path = os.path.join(os.path.dirname(source_path), f"{new_name}_cleaned.wav")
            os.rename(source_path, new_path)
            source_path = new_path
    else :
        # Path to your WAV file
        source_path = input_wav_file

    # Destination directory
    destination_directory = "bark_voices"

    # Extract the file name without the extension
    file_name = os.path.splitext(os.path.basename(source_path))[0]

    # Construct the full destination directory path
    destination_path = os.path.join(destination_directory, file_name)

    # Create the new directory
    os.makedirs(destination_path, exist_ok=True)

    # Move the WAV file to the new directory
    shutil.move(source_path, os.path.join(destination_path, f"{file_name}.wav"))
    
    tts.tts_to_file(text=prompt,
                file_path="output.wav",
                voice_dir="bark_voices/",
                speaker=f"{file_name}")

    # List all the files and subdirectories in the given directory
    contents = os.listdir(f"bark_voices/{file_name}")

    # Print the contents
    for item in contents:
        print(item)  

    tts_video = gr.make_waveform(audio="output.wav")
    
    return "output.wav", tts_video, gr.update(value=f"bark_voices/{file_name}/{contents[1]}", visible=True), gr.Group.update(visible=True), destination_path

def infer_from_c(prompt, c_name):
    
    tts.tts_to_file(text=prompt,
                file_path="output.wav",
                voice_dir="examples/library/",
                speaker=f"{c_name}")

    tts_video = gr.make_waveform(audio="output.wav")
    
    return "output.wav", tts_video, gr.update(value=f"examples/library/{c_name}/{c_name}.npz", visible=True), gr.Group.update(visible=True)


css = """
#col-container {max-width: 780px; margin-left: auto; margin-right: auto;}
a {text-decoration-line: underline; font-weight: 600;}
.mic-wrap > button {
    width: 100%;
    height: 60px;
    font-size: 1.4em!important;
}
.record-icon.svelte-1thnwz {
    display: flex;
    position: relative;
    margin-right: var(--size-2);
    width: unset;
    height: unset;
}
span.record-icon > span.dot.svelte-1thnwz {
    width: 20px!important;
    height: 20px!important;
}
.animate-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from {
      transform: rotate(0deg);
  }
  to {
      transform: rotate(360deg);
  }
}
#share-btn-container {
  display: flex; 
  padding-left: 0.5rem !important; 
  padding-right: 0.5rem !important; 
  background-color: #000000; 
  justify-content: center; 
  align-items: center; 
  border-radius: 9999px !important; 
  max-width: 15rem;
  height: 36px;
}
div#share-btn-container > div {
    flex-direction: row;
    background: black;
    align-items: center;
}
#share-btn-container:hover {
  background-color: #060606;
}
#share-btn {
  all: initial; 
  color: #ffffff;
  font-weight: 600; 
  cursor:pointer; 
  font-family: 'IBM Plex Sans', sans-serif; 
  margin-left: 0.5rem !important; 
  padding-top: 0.5rem !important; 
  padding-bottom: 0.5rem !important;
  right:0;
}
#share-btn * {
  all: unset;
}
#share-btn-container div:nth-child(-n+2){
  width: auto !important;
  min-height: 0px !important;
}
#share-btn-container .wrap {
  display: none !important;
}
#share-btn-container.hidden {
  display: none!important;
}
img[src*='#center'] { 
    display: block;
    margin: auto;
}
.footer {
        margin-bottom: 45px;
        margin-top: 10px;
        text-align: center;
        border-bottom: 1px solid #e5e5e5;
    }
    .footer>p {
        font-size: .8rem;
        display: inline-block;
        padding: 0 10px;
        transform: translateY(10px);
        background: white;
    }
    .dark .footer {
        border-color: #303030;
    }
    .dark .footer>p {
        background: #0b0f19;
    }

.disclaimer {
    text-align: left;
}
.disclaimer > p {
    font-size: .8rem;
}
"""

with gr.Blocks(css=css) as demo:
    with gr.Column(elem_id="col-container"):
        
        gr.Markdown("""
        <h1 style="text-align: center;">Coqui + Bark Voice Cloning</h1>
        <p style="text-align: center;">
        Mimic any voice character in less than 2 minutes with this <a href="https://tts.readthedocs.io/en/dev/models/bark.html" target="_blank">Coqui TTS + Bark</a> demo ! <br />
        Upload a clean 20 seconds WAV file of the vocal persona you want to mimic, <br />
        type your text-to-speech prompt and hit submit ! <br />
        </p>

        [![Duplicate this Space](https://huggingface.co/datasets/huggingface/badges/raw/main/duplicate-this-space-sm.svg#center)](https://huggingface.co/spaces/fffiloni/instant-TTS-Bark-cloning?duplicate=true)
            
        """)
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(
                    label="Text to speech prompt",
                    elem_id = "tts-prompt"
                )

                with gr.Tab("File upload"):
                    
                    with gr.Column():

                        if file_upload_available == "True": 
                            audio_in = gr.Audio(
                                label="WAV voice to clone", 
                                type="filepath",
                                source="upload"
                            )
                        else:
                            audio_in = gr.Audio(
                                label="WAV voice to clone", 
                                type="filepath",
                                source="upload",
                                interactive = False
                            )
                        clean_sample = gr.Checkbox(label="Clean sample ?", value=False)
                        hidden_audio_numpy = gr.Audio(type="numpy", visible=False)
                        submit_btn = gr.Button("Submit")
                
                with gr.Tab("Microphone"):
                    texts_samples = gr.Textbox(label = "Helpers", 
                                               info = "You can read out loud one of these sentences if you do not know what to record :)",
                                               value = """"Jazz, a quirky mix of groovy saxophones and wailing trumpets, echoes through the vibrant city streets."
———
"A majestic orchestra plays enchanting melodies, filling the air with harmony."
———
"The exquisite aroma of freshly baked bread wafts from a cozy bakery, enticing passersby."
———
"A thunderous roar shakes the ground as a massive jet takes off into the sky, leaving trails of white behind."
———
"Laughter erupts from a park where children play, their innocent voices rising like tinkling bells."
———
"Waves crash on the beach, and seagulls caw as they soar overhead, a symphony of nature's sounds."
———
"In the distance, a blacksmith hammers red-hot metal, the rhythmic clang punctuating the day."
———
"As evening falls, a soft hush blankets the world, crickets chirping in a soothing rhythm."
                                               """,
                                               interactive = False,
                                               lines = 5
                                              )
                    micro_in = gr.Audio(
                                label="Record voice to clone", 
                                type="filepath",
                                source="microphone",
                                interactive = True
                            )
                    clean_micro = gr.Checkbox(label="Clean sample ?", value=False)
                    micro_submit_btn = gr.Button("Submit")
                
                audio_in.upload(fn=load_hidden, inputs=[audio_in], outputs=[hidden_audio_numpy])
                micro_in.stop_recording(fn=load_hidden_mic, inputs=[micro_in], outputs=[hidden_audio_numpy])
                
                
                with gr.Tab("Voices Characters"):
                    selected_state = gr.State()
                    gallery_in = gr.Gallery(
                                label="Character Gallery", 
                                value=[(item["image"], item["title"]) for item in characters],
                                interactive = True,
                                allow_preview=False,
                                columns=2,
                                elem_id="gallery",
                                show_share_button=False
                            )
                    c_submit_btn = gr.Button("Submit")


            with gr.Column():
        
                cloned_out = gr.Audio(
                    label="Text to speech output",
                    visible = False
                )
        
                video_out = gr.Video(
                    label = "Waveform video",
                    elem_id = "voice-video-out"
                )
                
                npz_file = gr.File(
                    label = ".npz file",
                    visible = False
                )

                folder_path = gr.Textbox(visible=False)

                
                
                character_name = gr.Textbox(
                    label="Character Name", 
                    placeholder="Name that voice character",
                    elem_id = "character-name"
                )
                
                voice_description = gr.Textbox(
                    label="description", 
                    placeholder="How would you describe that voice ? ",
                    elem_id = "voice-description"
                )

                with gr.Group(elem_id="share-btn-container", visible=False) as share_group:
                    community_icon = gr.HTML(community_icon_html)
                    loading_icon = gr.HTML(loading_icon_html)
                    share_button = gr.Button("Share with Community", elem_id="share-btn")
        
        share_button.click(None, [], [], _js=share_js)
        
        gallery_in.select(
            update_selection,
            outputs=[character_name, selected_state],
            queue=False,
            show_progress=False,
        )
    
        audio_in.change(fn=wipe_npz_file, inputs=[folder_path])
        micro_in.clear(fn=wipe_npz_file, inputs=[folder_path])
    
        gr.Examples(
            examples = [
                [
                    "Once upon a time, in a cozy little shell, lived a friendly crab named Crabby. Crabby loved his cozy home, but he always felt like something was missing.",
                    "./examples/en_speaker_6.wav",
                    False,
                    None
                ],
                [ 
                    "It was a typical afternoon in the bustling city, the sun shining brightly through the windows of the packed courtroom. Three people sat at the bar, their faces etched with worry and anxiety. ",
                    "./examples/en_speaker_9.wav",
                    False,
                    None
                ],
            ],
            fn = infer,
            inputs = [
                prompt,
                audio_in,
                clean_sample,
                hidden_audio_numpy
            ],
            outputs = [
                cloned_out, 
                video_out,
                npz_file,
                share_group,
                folder_path
            ],
            cache_examples = False
        )
    
        gr.HTML("""
                <div class="footer">
                    <p>
                    Coqui + Bark Voice Cloning Demo by 🤗 <a href="https://twitter.com/fffiloni" target="_blank">Sylvain Filoni</a>
                    </p>
                </div>
                <div class="disclaimer">
                    <h3> * DISCLAIMER </h3>
                    <p>
                        I hold no responsibility for the utilization or outcomes of audio content produced using the semantic constructs generated by this model. <br />
                        Please ensure that any application of this technology remains within legal and ethical boundaries. <br />
                        It is important to utilize this technology for ethical and legal purposes, upholding the standards of creativity and innovation.
                    </p>
                </div>
            """)
    
    submit_btn.click(
        fn = infer,
        inputs = [
            prompt,
            audio_in,
            clean_sample,
            hidden_audio_numpy
        ],
        outputs = [
            cloned_out, 
            video_out,
            npz_file,
            share_group,
            folder_path
        ]
    )

    micro_submit_btn.click(
        fn = infer,
        inputs = [
            prompt,
            micro_in,
            clean_micro,
            hidden_audio_numpy
        ],
        outputs = [
            cloned_out, 
            video_out,
            npz_file,
            share_group,
            folder_path
        ]
    )

    c_submit_btn.click(
        fn = infer_from_c,
        inputs = [
            prompt,
            character_name
        ],
        outputs = [
            cloned_out, 
            video_out,
            npz_file,
            share_group
        ]
    )

demo.queue(api_open=False, max_size=10).launch()
