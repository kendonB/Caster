import os
import openai
import io
# soundfile might be needed if Whisper client needs specific format not easily made from raw bytes
# import soundfile 

class OpenAIUtils:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # It's better to let Caster's logging handle this if possible,
            # or print to stderr. Raising an error might stop Caster.
            print("ERROR: OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            # For now, we'll allow it to proceed, but API calls will fail.
            # A more robust solution would be to prevent the rule from loading.
            self.client = None 
            return
        self.client = openai.OpenAI(api_key=self.api_key)

    def transcribe_audio(self, audio_file_obj):
        if not self.client:
            print("OpenAI client not initialized. Cannot transcribe.")
            return None
        try:
            # Whisper API often expects a file-like object with a 'name' attribute.
            if not hasattr(audio_file_obj, 'name'):
                audio_file_obj.name = 'temp_audio.wav'  # Dummy name if not present

            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_obj,
                # language="en" # Optional: specify language
            )
            return transcript.text
        except Exception as e:
            print(f"Error during transcription: {e}")
            # Log the error using Caster's logging if available
            # from castervoice.lib import printer
            # printer.out(f"OpenAI Transcription Error: {e}", level=printer.ERROR)
            return None

    def _call_gpt_with_prompt(self, system_prompt, user_content, fallback_text):
        if not self.client:
            print("OpenAI client not initialized.")
            return fallback_text
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2 # Lower temperature for more deterministic output
            )
            refined_output = response.choices[0].message.content.strip()
            return refined_output
        except Exception as e:
            print(f"Error during GPT call: {e}")
            return fallback_text

    def _get_append_prompt_and_content(self, original_text_context, voice_command_content):
        system_prompt = """You are an intelligent text appending assistant.
You will receive 'Original Text Context' (the text immediately preceding the desired insertion point) and 'Voice Command' (which could be direct dictation to append, or an instruction to compose text to append).

Your primary goal is to process the 'Voice Command' and append the result smoothly to the 'Original Text Context'.

1.  **Process 'Voice Command'**:
    *   If 'Voice Command' is direct dictation: Clean disfluencies (e.g., "um", "ah") and ensure it's well-punctuated and uses correct grammar. Write the text in British English writing style.
    *   If 'Voice Command' is an instruction to compose text (e.g., "summarise the following content", "write a poem about cats"): Generate the requested text. This generated text should then be treated as if it were directly dictated (i.e., it should be clean and well-punctuated).

2.  **Integration**:
    *   Adjust the starting punctuation and capitalization of the processed/generated text from step 1 to flow naturally and grammatically after the 'Original Text Context'.
    *   For example, if 'Original Text Context' ends with a period, the new text should start with a space, then a capital letter. If 'Original Text Context' does not end with sentence-terminating punctuation, the new text might start with a lowercase letter and should be appropriately spaced.

3.  **Output**:
    *   Your output MUST BE ONLY the processed/generated text from the 'Voice Command', adjusted for smooth appending. 
    *   Pay particular attention to whether or not the 'Original Text Context' ends with a space. If it does, do not include a prepended space in your output. If it does not, include a prepended space in your output.
    *   Do NOT include the 'Original Text Context' in your output.
    *   Do NOT include any conversational phrases, explanations, or apologies.
    *   Do NOT include any trailing voice command phrases like 'process dictation', 'dictate off', 'append', or 'edit'.
"""
        user_content = f"Original Text Context:\n'''\n{original_text_context}\n'''\n\nVoice Command:\n'''\n{voice_command_content}\n'''\n\nProcessed Text to Append:"
        return system_prompt, user_content

    def _get_edit_prompt_and_content(self, original_text_to_edit, voice_command_content):
        system_prompt = """You are an expert text editing assistant. Your task is to revise 'Original Text' based on 'Transcribed Voice Commands'.

IMPORTANT RULES:
1.  **Initial Assessment of 'Original Text'**:
    *   If 'Original Text' appears nonsensical, irrelevant (e.g., application logs, system messages, error messages, gibberish), or clearly unintended as a basis for editing (hereafter "Invalid Original Text"):
        *   If 'Transcribed Voice Commands' (TVC) seem to dictate new, self-contained content (e.g., "dictate a new sentence: ...", or is simply prose/code that stands alone): Your output MUST be ONLY this new content, cleaned of disfluencies (e.g., "um", "ah") and appropriately punctuated. The Invalid Original Text is discarded.
        *   Else if TVC seem to be an edit instruction (e.g., "delete that", "change X to Y", "make it blue") or any other command that is NOT new self-contained content: Your output MUST be the Invalid Original Text, reproduced exactly and unaltered. Do not attempt to apply the edit.
    *   If 'Original Text' seems like a valid user document or text intended for editing (hereafter "Valid Original Text"), proceed to Rule 2.

2.  **Processing Valid Original Text with TVC**:
    *   Interpret TVC to modify the Valid Original Text. This can include replacements, deletions, insertions, rephrasing, formatting, etc.
    *   If TVC includes dictation (e.g., for replacement or insertion), ensure this dictated part is cleaned of disfluencies (e.g., "um", "ah") before integrating it into the edit.
    *   If TVC dictates new, self-contained text AND explicitly or implicitly indicates that the Valid Original Text should be entirely replaced (e.g., "clear everything and write: ...", "new document: ..."), then output only the new dictated text, cleaned of disfluencies and appropriately punctuated.

3.  **Output Format**:
    *   Your output MUST be ONLY the final text as determined by the rules above.
    *   Do NOT include any conversational phrases, explanations, apologies, or introductory/concluding remarks like 'Certainly, here is the revised text:'.
    *   Return the entire relevant text block after modification, even if the change was minor.
    *   Do NOT include any trailing voice command phrases like 'process dictation', 'dictate off', 'append', or 'edit'.
"""
        user_content = f"Original Text:\n'''\n{original_text_to_edit}\n'''\n\nTranscribed Voice Commands:\n'''\n{voice_command_content}\n'''\n\nEdited Text:"
        return system_prompt, user_content

    def refine_text_with_gpt(self, original_text, transcribed_audio_text, mode: str):
        if not self.client:
            print("OpenAI client not initialized. Cannot refine text.")
            # Fallback depends on mode; if edit, return original, if append, return transcribed.
            return original_text if mode == "edit" else transcribed_audio_text

        voice_command_content = transcribed_audio_text # Assumed to be cleaned of mode keywords already

        if mode == "append":
            system_prompt, user_content = self._get_append_prompt_and_content(original_text, voice_command_content)
            # Fallback for append is the processed command text itself
            return self._call_gpt_with_prompt(system_prompt, user_content, voice_command_content)
        elif mode == "edit": # Explicitly "edit"
            system_prompt, user_content = self._get_edit_prompt_and_content(original_text, voice_command_content)
            # Fallback for edit mode is the original_text, as we want to preserve it if LLM call fails
            return self._call_gpt_with_prompt(system_prompt, user_content, original_text)
        else: # Should not happen if mode is always "append" or "edit"
            print(f"Warning: Unknown mode '{mode}' in refine_text_with_gpt. Defaulting to edit behavior.")
            system_prompt, user_content = self._get_edit_prompt_and_content(original_text, voice_command_content)
            return self._call_gpt_with_prompt(system_prompt, user_content, original_text)


if __name__ == '__main__':
    utils = OpenAIUtils()
    if utils.client:
        try:
            import soundfile as sf
            import numpy as np
            
            dummy_audio_file = io.BytesIO()
            samplerate = 16000
            dummy_audio_data = np.zeros(samplerate) 
            sf.write(dummy_audio_file, dummy_audio_data, samplerate, format='WAV')
            dummy_audio_file.seek(0)
            dummy_audio_file.name = "test_silence.wav"

            print("Testing transcription (with dummy silence)...")
            transcribed_silence = utils.transcribe_audio(dummy_audio_file)
            print(f"Transcription of silence: '{transcribed_silence}' (expected empty or minimal)")

            print("\n--- Testing 'append' functionality ---")
            context_append1 = "This is the first sentence."
            append_command1 = "add this new phrase ah" # Keyword 'append' removed
            refined_append1 = utils.refine_text_with_gpt(context_append1, append_command1, "append")
            print(f"Context: '{context_append1}', Command: '{append_command1}', Mode: 'append'")
            print(f"Refined (append1): '{refined_append1}' (Expected: 'Add this new phrase.')")
            
            context_append2 = "This is an ongoing sentence"
            append_command2 = "and um continue it nicely" # Keyword 'append' removed
            refined_append2 = utils.refine_text_with_gpt(context_append2, append_command2, "append")
            print(f"Context: '{context_append2}', Command: '{append_command2}', Mode: 'append'")
            print(f"Refined (append2): '{refined_append2}' (Expected: ' and continue it nicely.')")

            context_append3 = "Existing text."
            append_command3 = "write a short thank you note then" # Keyword 'append' removed
            refined_append3 = utils.refine_text_with_gpt(context_append3, append_command3, "append")
            print(f"Context: '{context_append3}', Command: '{append_command3}', Mode: 'append'")
            print(f"Refined (append3): '{refined_append3}' (Expected: ' Thank you so much!' or similar composed text)")


            print("\n--- Testing 'edit' functionality (default mode) ---")
            edit_original1 = "This is the old text to change."
            edit_command1 = "replace old with brand new" # Keyword 'edit' removed
            refined_edit1 = utils.refine_text_with_gpt(edit_original1, edit_command1, "edit")
            print(f"Original: '{edit_original1}', Command: '{edit_command1}', Mode: 'edit'")
            print(f"Refined (edit1): '{refined_edit1}' (Expected: 'This is the brand new text to change.')")

            edit_original2 = "hello world this is a test"
            edit_command2_no_keyword = "make all of it uppercase" # No keyword was fine for edit before
            refined_edit2 = utils.refine_text_with_gpt(edit_original2, edit_command2_no_keyword, "edit")
            print(f"Original: '{edit_original2}', Command: '{edit_command2_no_keyword}', Mode: 'edit'")
            print(f"Refined (edit2): '{refined_edit2}' (Expected: 'HELLO WORLD THIS IS A TEST')")

            # Test for 'Invalid Original Text' with dictation in 'edit' mode
            edit_original_invalid = "LOG: System_Error_XyZ123" 
            edit_command_dictate = "dictate a new document: The quick brown fox jumps over the lazy dog."
            refined_edit_invalid_dictate = utils.refine_text_with_gpt(edit_original_invalid, edit_command_dictate, "edit")
            print(f"Original (Invalid): '{edit_original_invalid}', Command: '{edit_command_dictate}', Mode: 'edit'")
            print(f"Refined (edit_invalid_dictate): '{refined_edit_invalid_dictate}' (Expected: 'The quick brown fox jumps over the lazy dog.')")

            # Test for 'Invalid Original Text' with an edit instruction in 'edit' mode
            edit_command_instruction = "delete the log part"
            refined_edit_invalid_instruction = utils.refine_text_with_gpt(edit_original_invalid, edit_command_instruction, "edit")
            print(f"Original (Invalid): '{edit_original_invalid}', Command: '{edit_command_instruction}', Mode: 'edit'")
            print(f"Refined (edit_invalid_instruction): '{refined_edit_invalid_instruction}' (Expected: '{edit_original_invalid}')")
            
            # Test for 'edit' keyword being optional for edit mode - now mode is explicit
            edit_original3 = "This text needs a correction."
            edit_command3_no_keyword = "Correct the typo in nedds to needs"
            refined_edit3 = utils.refine_text_with_gpt(edit_original3, edit_command3_no_keyword, "edit")
            print(f"Original: '{edit_original3}', Command: '{edit_command3_no_keyword}', Mode: 'edit'")
            print(f"Refined (edit3 no keyword): '{refined_edit3}' (Expected: 'This text needs a correction.' or similar if LLM is smart)")


        except ImportError:
            print("Skipping audio tests: soundfile or numpy not installed.")
        except Exception as e:
            print(f"Test error: {e}")
    else:
        print("Client not initialized. Skipping refinement tests.") 