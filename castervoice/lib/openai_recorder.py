import sounddevice as sd
import numpy as np
import soundfile as sf
import io
import threading
import time
import pyperclip # For clipboard operations

# Assuming openai_utils.py is in the same directory or accessible in PYTHONPATH
from .openai_utils import OpenAIUtils

# For Caster specific actions like Key presses
from dragonfly import Key, Function, Pause, Clipboard
from castervoice.lib import control # To access nexus for pause, etc.

class OpenAIRecordingManager:
    def __init__(self, openai_utils_instance: OpenAIUtils):
        self.openai_utils = openai_utils_instance
        self.sample_rate = 16000 # Standard for voice
        self.channels = 1
        self.is_recording = False
        self.frames = []
        self._thread = None
        self.current_original_text = ""
        self.active_processing = False # To prevent concurrent processing attempts

        # Placeholder for Caster's printer or a simple print
        self.log = lambda message: print(f"[OpenAIRecorder] {message}")

    def _get_text_from_focused_field(self):
        self.log("Attempting to get text from focused field...")
        try:
            Key("c-a, c-c").execute() # Select all (Ctrl+A), then copy (Ctrl+C)
            focused_text = Clipboard.get_system_text()
            self.log(f"Retrieved text: {focused_text[:50]}...") # Log what was actually retrieved
            return focused_text
        except Exception as e:
            self.log(f"Error getting text from field: {e}")
            # Consider using castervoice.lib.printer.out for logging within Caster
            return "" # Fallback to empty string

    def _paste_text_into_focused_field(self, text_to_paste):
        self.log("Attempting to paste text...")
        try:
            Clipboard.set_system_text(text_to_paste) # Set clipboard
            Key("c-v").execute() # Ctrl+V for regular paste
            self.log("Pasted text.")
        except Exception as e:
            self.log(f"Error pasting text: {e}")

    def _audio_callback(self, indata, frame_count, time_info, status):
        if status:
            self.log(f"Audio callback status: {status}")
        if self.is_recording:
            self.frames.append(indata.copy())

    def start_continuous_dictation(self):
        if self.is_recording:
            self.log("Already recording.")
            return
        
        self.is_recording = True
        self.active_processing = False
        self.frames = []
        
        self.current_original_text = self._get_text_from_focused_field()
        self.log("Starting continuous dictation stream...")
        
        # For simplicity, this example starts a recording that you'll manually stop
        # and process via `process_current_audio`. VAD would go here.
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._audio_callback,
            dtype='float32' # Standard for many VAD libraries too
        )
        self.stream.start()
        self.log("Audio stream started. Say 'stop dictation recording' or 'dictate off' to process.")

    def process_current_audio(self, mode: str, called_during_shutdown=False):
        if not self.frames or self.active_processing:
            if not self.frames:
                self.log("No audio frames to process.")
            if self.active_processing:
                self.log("Processing already in progress.")
            if not called_during_shutdown and self.is_recording: # Re-arm original text if still active
                 self.current_original_text = self._get_text_from_focused_field()
            return

        self.active_processing = True
        self.log("Processing current audio segment...")

        # Get the most current text from the field to operate on.
        # This is crucial for 'append' and 'edit' to work with the latest state.
        current_field_text = self._get_text_from_focused_field()
        self.current_original_text = current_field_text # Update our state for this processing cycle
        
        audio_data_np = np.concatenate(self.frames, axis=0) if self.frames else np.array([], dtype=np.float32)
        self.frames = [] # Clear frames for next segment or stop

        if audio_data_np.size == 0:
            self.log("No audio data in segment.")
            self.active_processing = False
            # self.current_original_text is already up-to-date from the get_text_from_focused_field() call above.
            return

        # Convert numpy array to a file-like object for OpenAI
        temp_audio_file = io.BytesIO()
        sf.write(temp_audio_file, audio_data_np, self.sample_rate, format='WAV', subtype='PCM_16')
        temp_audio_file.seek(0)
        # Whisper client may need a .name attribute on the file object.
        temp_audio_file.name = "dictation_segment.wav"

        transcribed_text = self.openai_utils.transcribe_audio(temp_audio_file)
        self.log(f"Raw transcribed: {transcribed_text}") # Log raw before filtering

        if transcribed_text:
            original_transcription_for_filtering_log = transcribed_text
            
            # List of command phrases (lowercase) that trigger actions and might be caught in transcription
            command_phrases_lc = ["dictate off", "append", "edit"] 

            for command_lc in command_phrases_lc:
                # Check with trailing period
                # Ensure transcribed_text is long enough before slicing/checking
                if len(transcribed_text) >= len(command_lc) + 1 and transcribed_text.lower().endswith(command_lc + "."):
                    # Verify the segment being removed is indeed the command (case-insensitive)
                    if transcribed_text[-(len(command_lc)+1):-1].lower() == command_lc:
                        self.log(f"Removing trailing command segment '{transcribed_text[-(len(command_lc)+1):]}' from transcription.")
                        transcribed_text = transcribed_text[:-(len(command_lc)+1)].rstrip()
                        continue 

                # Check without trailing period
                # Ensure transcribed_text is long enough
                if len(transcribed_text) >= len(command_lc) and transcribed_text.lower().endswith(command_lc):
                    # Verify the segment
                    if transcribed_text[-len(command_lc):].lower() == command_lc:
                        self.log(f"Removing trailing command segment '{transcribed_text[-len(command_lc):]}' from transcription.")
                        transcribed_text = transcribed_text[:-len(command_lc)].rstrip()
                        continue
            
            if original_transcription_for_filtering_log != transcribed_text:
                self.log(f"Filtered transcription for refinement: '{transcribed_text}'")

        if transcribed_text:
            self.log(f"Transcribed (after potential filtering): {transcribed_text}")
            
            # GPT refines the NEW transcribed segment, using current_original_text (which is fresh from field) as context.
            refined_new_segment = self.openai_utils.refine_text_with_gpt(self.current_original_text, transcribed_text, mode)
            self.log(f"GPT refined segment: \"{refined_new_segment}\"")

            final_text_to_paste = ""
            if mode == "append":
                if not self.current_original_text: # Field was empty
                    final_text_to_paste = refined_new_segment
                elif not refined_new_segment: # Dictation was empty/filtered out
                    final_text_to_paste = self.current_original_text
                else: # Both have content
                    final_text_to_paste = f"{self.current_original_text} {refined_new_segment}"
            elif mode == "edit":
                # For 'edit', assume refine_text_with_gpt IS returning the complete, edited text.
                # This matches the original logic's implicit assumption for 'edit'.
                final_text_to_paste = refined_new_segment
            else: # Default behavior or unknown mode
                self.log(f"Unknown processing mode '{mode}', using refined segment as final text.")
                final_text_to_paste = refined_new_segment
            
            self.log(f"Final text to paste ({mode} mode): \"{final_text_to_paste}\"")
            self._paste_text_into_focused_field(final_text_to_paste)
            
            # After successful processing, update current_original_text for the next potential segment
            # if we are continuing dictation without restarting the mode.
            if self.is_recording and not called_during_shutdown:
                 self.current_original_text = final_text_to_paste # The new baseline IS the refined text
        else:
            self.log("Transcription failed or returned empty.")
            # Original text remains self.current_original_text (which is current_field_text)
        
        self.active_processing = False
        # If VAD was here, it would re-arm recording automatically.
        # For manual `process_current_audio` call, it doesn't re-record unless `start` is called again.
        # If still in dictation mode, prepare for next utterance
        if self.is_recording and not called_during_shutdown:
            self.log("Ready for next audio segment...")
            # self.current_original_text is now the refined text (or original if transcription failed)
            # The stream is still open if we used this manual process command
            # If we want continuous auto-segmenting, VAD logic is needed here to call process & re-capture text.
            pass # Stream remains open


    def stop_dictation(self, process_remaining_audio=True):
        self.log("Stopping dictation...")
        if not self.is_recording and not self.active_processing: # If already stopped and not processing
            if hasattr(self, 'stream') and self.stream and not self.stream.closed:
                 self.stream.stop()
                 self.stream.close()
                 self.log("Stream already stopped but ensured closed.")
            return
            
        self.is_recording = False # Stop new audio from being added to frames
        
        if hasattr(self, 'stream') and self.stream:
            if not self.stream.closed:
                self.stream.stop()
                self.stream.close()
            self.log("Audio stream stopped and closed.")

        if process_remaining_audio and self.frames:
            self.log("Processing remaining audio before full stop...")
            # Call process_current_audio in a blocking way or ensure it completes.
            # Since this is stop_dictation, it's the final processing for this session.
            self.process_current_audio(mode="edit", called_during_shutdown=True) # Default to "edit" mode for final processing
        else:
            self.frames = [] # Discard any unprocessed frames
        
        self.log("Dictation fully stopped.")

# Example of how this might be used by the rule (conceptual)
if __name__ == '__main__':
    # This test requires OPENAI_API_KEY to be set
    # And Caster's control.nexus() mock or equivalent for Key presses
    class MockOpenAIUtils:
        def transcribe_audio(self, audio_file_obj): return "This is a test transcription."
        def refine_text_with_gpt(self, original, transcribed): return f"{original} ... {transcribed} ... refined!"

    mock_openai_utils = MockOpenAIUtils()
    recorder = OpenAIRecordingManager(mock_openai_utils)
    
    # Simulate Caster's control.nexus() for Key presses
    # In real Caster, control.nexus() is available.
    class MockComm:
        def get_com(self, name): return self
        def pause(self, duration_str): time.sleep(float(duration_str) / 1000.0)
    class MockNexus:
        def __init__(self): self.comm = MockComm()
    control.nexus = MockNexus() # Monkey-patch for testing Key actions

    if not os.getenv("OPENAI_API_KEY"):
        print("WARN: OPENAI_API_KEY not set, using mock OpenAI utils for this test.")
        recorder.openai_utils = MockOpenAIUtils() # Ensure it uses mock if key is missing
    else:
        print("INFO: OPENAI_API_KEY is set, will use actual OpenAIUtils if not overridden by mock.")
        # For a full test, initialize with the real OpenAIUtils
        # from openai_utils import OpenAIUtils as RealOpenAIUtils
        # recorder.openai_utils = RealOpenAIUtils() # This would make actual API calls

    print("Simulating 'dictate' command...")
    # In a real rule, pyperclip.copy would set the initial clipboard for _get_text_from_focused_field
    pyperclip.copy("Initial text in the field.") 
    recorder.start_continuous_dictation()
    
    print("Simulating speech for 2 seconds...")
    time.sleep(2) # Simulate speaking time, audio frames would be captured
    
    # Manually trigger processing (in a real VAD setup, this would be automatic on silence)
    print("Simulating 'append' or 'edit' command or end of speech segment...")
    recorder.process_current_audio(mode="edit") # Example mode for test
    # At this point, the clipboard would have the refined text from mock_openai_utils
    print(f"Clipboard content after processing: {pyperclip.paste()}")

    print("\nSimulating 'dictate off' command...")
    recorder.stop_dictation(process_remaining_audio=False) # Don't re-process if already done

    print("\nTest with another segment after first processing (if start_continuous_dictation was re-armed)")
    # This part of test needs recorder to re-arm original_text and be ready for more frames.
    # The current `process_current_audio` doesn't automatically re-open stream for manual trigger.
    # A VAD loop would be: record -> silence -> process -> record -> silence -> process ...
    # For now, let's test stopping with remaining audio:
    pyperclip.copy("Text before second segment.")
    recorder.start_continuous_dictation() # Start a new session
    print("Simulating more speech for 1 second...")
    time.sleep(1) # More frames captured
    print("Simulating 'dictate off' but with processing remaining audio...")
    recorder.stop_dictation(process_remaining_audio=True) # stop_dictation now handles passing the mode internally
    print(f"Clipboard content after final processing: {pyperclip.paste()}") 