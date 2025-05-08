import threading
# pylint: disable=wildcard-import, unused-wildcard-import, protected-access
from dragonfly import Grammar, MappingRule, Function, IntegerRef, Dictation, Choice, Key, Text, get_engine

from castervoice.lib import control, settings, utilities
# from castervoice.lib.actions import Store, Retrieve # Removed problematic import
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R # For Caster's RegisteredAction

# Attempt to import the new OpenAI modules
try:
    from castervoice.lib.openai_utils import OpenAIUtils
    from castervoice.lib.openai_recorder import OpenAIRecordingManager
    OPENAI_MODULES_LOADED = True
except ImportError as e:
    utilities.simple_log(f"Caster: Failed to load OpenAI modules for dictation: {e}")
    OPENAI_MODULES_LOADED = False
    # Define dummy classes if imports fail, so the rule loads without erroring out immediately
    # This allows Caster to start, and the user can be informed that the feature is unavailable.
    class OpenAIUtils:
        def __init__(self, *args, **kwargs): print("Dummy OpenAIUtils: Real version failed to load.")
    class OpenAIRecordingManager:
        def __init__(self, *args, **kwargs): print("Dummy OpenAIRecordingManager: Real version failed to load.")
        def start_continuous_dictation(self): print("OpenAI Dictation: Not available.")
        def process_current_audio(self): print("OpenAI Dictation: Not available.")
        def stop_dictation(self, *args, **kwargs): print("OpenAI Dictation: Not available.")


# Global state for the rule
openai_dictation_is_active = False
openai_recorder_instance = None
openai_utils_instance = None
_the_openai_grammar = None # Stores the engine-managed grammar object for this rule

# Store for original grammar states
original_grammar_states = {}

# Placeholder for Caster's logging, replace with actual if available
log = lambda message: utilities.simple_log(f"[OpenAIDictationRule] {message}")

def _initialize_openai_services_if_needed():
    global openai_utils_instance, openai_recorder_instance
    if not OPENAI_MODULES_LOADED:
        log("OpenAI modules did not load. OpenAI dictation will not be available.")
        return False
    if openai_utils_instance is None:
        openai_utils_instance = OpenAIUtils()
        if not hasattr(openai_utils_instance, 'client') or openai_utils_instance.client is None:
            log("OpenAIUtils client failed to initialize. OpenAI dictation disabled.")
            openai_utils_instance = None
            return False
    if openai_recorder_instance is None and openai_utils_instance:
        openai_recorder_instance = OpenAIRecordingManager(openai_utils_instance)
    return openai_utils_instance is not None and openai_recorder_instance is not None

def _ensure_grammar_reference_is_set():
    global _the_openai_grammar
    if _the_openai_grammar is None:
        engine = get_engine()
        # The name used here MUST match RuleDetails(name=...) in get_rule()
        rule_name_to_find = "open A I dictation rule"
        for gram in engine.grammars:
            for rule in gram.rules:
                if hasattr(rule, 'name') and rule.name == rule_name_to_find:
                    _the_openai_grammar = gram
                    log(f"Found and cached grammar for rule '{rule_name_to_find}': {gram}")
                    return True
                # Fallback: Check by class name if rule.name isn't set as expected by RuleDetails
                elif rule.__class__.__name__ == "OpenAIDictationRule" and not _the_openai_grammar:
                    _the_openai_grammar = gram
                    log(f"Found and cached grammar by class 'OpenAIDictationRule': {gram}")
                    # Don't return yet, prefer named match if available in another grammar
        
        if _the_openai_grammar is not None: # Check if fallback found something
             return True

        if _the_openai_grammar is None:
            log(f"CRITICAL: Could not find the grammar object for rule '{rule_name_to_find}'. Exclusivity will fail.")
            return False
    return True # Already set

def _perform_dictation_activation():
    global openai_dictation_is_active
    if not _initialize_openai_services_if_needed():
        log("Cannot activate OpenAI dictation mode due to initialization failure.")
        Text("Open AI dictation not available, check configuration.").execute()
        return

    if openai_dictation_is_active:
        log("OpenAI dictation mode is already active.")
        return

    if not _the_openai_grammar: # Should have been set by the wrapper
        log("ERROR: Grammar reference not set before activation logic.")
        Text("Dictation mode activation error: grammar not found.").execute()
        return

    log("Activating OpenAI dictation mode...")
    _the_openai_grammar.set_exclusive(True)
    log(f"Grammar '{_the_openai_grammar.name if hasattr(_the_openai_grammar, 'name') else _the_openai_grammar}' set to exclusive.")
            
    openai_dictation_is_active = True
    if openai_recorder_instance:
        threading.Thread(target=openai_recorder_instance.start_continuous_dictation, daemon=True).start()

def _perform_dictation_deactivation():
    global openai_dictation_is_active
    if not openai_dictation_is_active:
        log("OpenAI dictation mode is not active.")
        return

    if not _the_openai_grammar: # Should have been set by the wrapper
        log("ERROR: Grammar reference not set before deactivation logic. Cannot make non-exclusive.")
        # Proceed to stop recording etc., but log the grammar issue.
    else:
        log("Deactivating OpenAI dictation mode...")
        _the_openai_grammar.set_exclusive(False)
        log(f"Grammar '{_the_openai_grammar.name if hasattr(_the_openai_grammar, 'name') else _the_openai_grammar}' set to non-exclusive.")

    if openai_recorder_instance:
        threading.Thread(target=openai_recorder_instance.stop_dictation, args=(True,), daemon=True).start()
    
    openai_dictation_is_active = False

# These are the functions called by Dragonfly actions
def activate_openai_dictate_mode_command(): 
    if not _ensure_grammar_reference_is_set():
        log("OpenAI Dictation grammar link error on activation.")
        return    
    _perform_dictation_activation()

def deactivate_openai_dictate_mode_command():
    if not _ensure_grammar_reference_is_set():
        # Log error but proceed with deactivation attempt if already active
        log("OpenAI Dictation grammar link error on deactivation attempt.")
    _perform_dictation_deactivation()

# New helper function
def _handle_process_request(mode: str):
    if not openai_dictation_is_active or not openai_recorder_instance:
        log(f"Cannot process audio ({mode}): OpenAI dictation not active or recorder not initialized.")
        return
    if not _initialize_openai_services_if_needed(): # Ensure services are up
        log(f"OpenAI services not ready to process current audio segment ({mode}).")
        return
    log(f"Processing current dictation segment as '{mode}'...")
    threading.Thread(target=openai_recorder_instance.process_current_audio, args=(mode,), daemon=True).start()

def process_append_command():
    _handle_process_request("append")

def process_edit_command():
    _handle_process_request("edit")

class OpenAIDictationRule(MappingRule):
    mapping = {
        "dictate": Function(activate_openai_dictate_mode_command),
        "dictate off": Function(deactivate_openai_dictate_mode_command),
        "append": Function(process_append_command),
        "edit": Function(process_edit_command),
    }
    extras = []
    defaults = {}

# Initialize services once Caster loads this rule file if modules are available.
# This is a bit eager; initialization could be deferred to first command use.
if OPENAI_MODULES_LOADED:
    # Running initialize_openai_services() here might be too early, 
    # especially if Caster loads rules in a context where env vars or full nexus isn't ready.
    # It's safer to call it on first use in activate_openai_dictate_mode.
    # For now, let's log its potential success or failure here based on module load.
    log("OpenAI dictation rule loaded. Services will initialize on first 'dictate' command.")
else:
    log("OpenAI dictation rule loaded, but dependent modules failed. Feature unavailable.")

def get_rule():
    # Name here must match `rule_name_to_find` in `_ensure_grammar_reference_is_set`
    return OpenAIDictationRule, RuleDetails(name="open A I dictation rule")

# It's good practice to have a cleanup function if threads or resources are managed
# Caster might call this on shutdown or rule unload, but this is not standard in basic rules.
# def unload():
#    log("Unloading OpenAI Dictation Rule...")
#    if openai_dictation_is_active:
#        deactivate_openai_dictate_mode() # Try to clean up 