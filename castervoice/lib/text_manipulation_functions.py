from dragonfly import Key, Pause
import pyperclip
import re 


character_list = [".", ",", "'", "(", ")", "[", "]", "<", ">", "{", "}", "?", "-", ";", "=", "/", 
"\\", "$", "_", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", 
    "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"] 

def get_start_end_position(text, phrase, left_right):
    if left_right == "left":
        if phrase in character_list:
            pattern = re.escape(phrase)
        else:
            # avoid e.g. matching 'and' in 'land' but allow e.g. matching 'and' in 'hello.and'
            # for matching purposes use lowercase
            # PROBLEM: this will not match words in class names like "Class" in "ClassName"
            pattern = '(?:[^A-Za-z]|\A)({})(?:[^A-Za-z]|\Z)'.format(phrase.lower()) # must get group 1

        if not re.search(pattern, text.lower()):
            # replaced phase not found
            print("'{}' not found".format(phrase))
            return
        
        match_iter = re.finditer(pattern, text.lower())
        if phrase in character_list: # consider changing this to if len(phrase) == 1 or something
            match_list = [(m.start(), m.end()) for m in match_iter] 
        else:
            match_list = [(m.start(1), m.end(1)) for m in match_iter] # first group
        last_match = match_list[-1] # Todo: allow user to pick which match they want e.g. the second to last one
        left_index, right_index = last_match


    if left_right == "right":
        # if replaced phrase is punctuation, don't require a word boundary for match
        if phrase in character_list:
            pattern = re.escape(phrase.lower())
        # phrase contains a word
        else:
            pattern = '(?:[^A-Za-z]|\A)({})(?:[^A-Za-z]|\Z)'.format(phrase.lower()) # must get group 1

        match = re.search(pattern, text.lower())
        if not match:
            print("'{}' not found".format(phrase))
            return
        else:
            if phrase in character_list:
                left_index, right_index = match.span()
            else:
                left_index, right_index = match.span(1) # Group 1
    return (left_index, right_index)


def select_text_and_return_it(left_right, number_of_lines_to_search):
    # temporarily store previous clipboard item
    temp_for_previous_clipboard_item = pyperclip.paste()
    Pause("30").execute()
    if left_right == "left":
        Key("s-home, s-up:%d, s-home, c-c" %number_of_lines_to_search).execute()
    if left_right == "right":
        Key("s-end, s-down:%d, s-end, c-c" %number_of_lines_to_search).execute()
    Pause("70").execute()
    selected_text = pyperclip.paste()
    return (selected_text, temp_for_previous_clipboard_item)

def deal_with_phrase_not_found(selected_text, temp_for_previous_clipboard_item, cursor_behavior, left_right):
        # Approach 1: unselect text by using the arrow keys, a little faster but does not work in texstudio
        if cursor_behavior == "standard":
            if left_right == "left":
                Key("right").execute()
            if left_right == "right":
                Key("left").execute()
        # Approach 2: paste selected text over itself, sometimes a little slower but works in texstudio
        if cursor_behavior == "texstudio":
            # move cursor to the right side of selection by pasting, 
            # another way to do this in tex studio is to press left then right or vice versa
            # depending on whether you're selecting from left to right or right to left
            Key("c-v").execute() # move cursor to the right side of selection by pasting, 
            if left_right == "right":
                Key("left:%d" %len(selected_text)).execute()
    
        # put previous clipboard item back in the clipboard
        Pause("20").execute()
        pyperclip.copy(temp_for_previous_clipboard_item)


def replace_phrase_with_phrase(text, replaced_phrase, replacement_phrase, left_right):
    match = get_start_end_position(text, replaced_phrase, left_right)
    if match:
        left_index, right_index = match
    else:
        return
    return text[: left_index] + replacement_phrase + text[right_index:] 
    


def copypaste_replace_phrase_with_phrase(replaced_phrase, replacement_phrase, left_right, number_of_lines_to_search, cursor_behavior):
    clip = select_text_and_return_it(left_right, number_of_lines_to_search)
    selected_text = clip[0]
    temp_for_previous_clipboard_item = clip[1]
    replaced_phrase = str(replaced_phrase)
    replacement_phrase = str(replacement_phrase) 
    new_text = replace_phrase_with_phrase(selected_text, replaced_phrase, replacement_phrase, left_right)
    if not new_text:
        # replaced_phrase not found
        deal_with_phrase_not_found(selected_text, temp_for_previous_clipboard_item, cursor_behavior, left_right)
        return
    
    pyperclip.copy(new_text)
    Key("c-v").execute()
    if number_of_lines_to_search < 20: 
        # only put the cursor back in the right spot if the number of lines to search is fairly small
        if left_right == "right":
            offset = len(new_text)
            Key("left:%d" %offset).execute()
    # put previous clipboard item back in the clipboard
    Pause("20").execute()
    pyperclip.copy(temp_for_previous_clipboard_item)

def remove_phrase_from_text(text, phrase, left_right):
    match = get_start_end_position(text, phrase, left_right)
    if match:
        left_index, right_index = match
    else:
        return
        
    # if the "phrase" is punctuation, just remove it, but otherwise remove an extra space adjacent to the phrase
    if phrase in character_list:
        return text[: left_index] + text[right_index:] 
    else:
        return text[: left_index - 1] + text[right_index:] 


def copypaste_remove_phrase_from_text(phrase, left_right, number_of_lines_to_search, cursor_behavior):
    clip = select_text_and_return_it(left_right, number_of_lines_to_search)
    selected_text = clip[0]
    temp_for_previous_clipboard_item = clip[1]
    phrase = str(phrase)
    new_text = remove_phrase_from_text(selected_text, phrase, left_right)
    if not new_text:
        # phrase not found
        deal_with_phrase_not_found(selected_text, temp_for_previous_clipboard_item, cursor_behavior, left_right)
        return 
    pyperclip.copy(new_text)
    Key("c-v").execute()

    if left_right == "right":
        offset = len(new_text)
        Key("left:%d" %offset).execute()
    # put previous clipboard item back in the clipboard
    Pause("20").execute()
    pyperclip.copy(temp_for_previous_clipboard_item)


def move_until_phrase(left_right, before_after, phrase, number_of_lines_to_search, cursor_behavior):
    # set default for before_after
    if before_after == None:
        if left_right  == "left":
            before_after = "after"
        if left_right == "right":
            before_after = "before"

    clip = select_text_and_return_it(left_right, number_of_lines_to_search)
    selected_text = clip[0]
    temp_for_previous_clipboard_item = clip[1]
    phrase = str(phrase)
    match = get_start_end_position(selected_text, phrase, left_right)
    if match:
        left_index, right_index = match
    else:
        # phrase not found
        deal_with_phrase_not_found(selected_text, temp_for_previous_clipboard_item, cursor_behavior, left_right)
        return
    left_index, right_index = get_start_end_position(selected_text, phrase, left_right)

    
    if cursor_behavior == "standard":
        # Approach 1: unselect using arrow keys rather than pasting over the existing text. (a little faster) does not work texstudio
        if right_index < round(len(selected_text))/2:
            # it's faster to approach phrase from the left
            Key("left").execute() # unselect text and place cursor on the left side of selection 
            if before_after  == "before":
                offset_correction = selected_text[: left_index].count("\r\n")
                offset = left_index - offset_correction
            if before_after  == "after":
                offset_correction = selected_text[: right_index].count("\r\n")
                offset = right_index - offset_correction
            Key("right:%d" %offset).execute()
        else:
            # it's faster to approach phrase from the right
            Key("right").execute() # unselect text and place cursor on the right side of selection
            if before_after  == "before":
                offset_correction = selected_text[left_index :].count("\r\n")
                offset = len(selected_text) - left_index - offset_correction
            if before_after  == "after":
                offset_correction = selected_text[right_index :].count("\r\n")
                offset = len(selected_text) - right_index - offset_correction
            Key("left:%d" %offset).execute()
            
    if cursor_behavior == "texstudio":
    # Approach 2: paste the selected text over itself rather than simply unselecting. A little slower but works Texstudio
    # comments below indicate the other approach
        Key("c-v").execute()
        if before_after == "before":
            selected_text_to_the_right_of_phrase = selected_text[left_index :]    
        if before_after == "after":
            selected_text_to_the_right_of_phrase = selected_text[right_index :]
        multiline_offset_correction = selected_text_to_the_right_of_phrase.count("\r\n")
        if before_after  == "before":
            offset = len(selected_text) - left_index - multiline_offset_correction
        if before_after == "after":
            offset = len(selected_text) - right_index - multiline_offset_correction
        Key("left:%d" %offset).execute()

    # put previous clipboard item back in the clipboard (Todo: consider factoring this out)
    Pause("20").execute()
    pyperclip.copy(temp_for_previous_clipboard_item)

def select_phrase(phrase, left_right, number_of_lines_to_search, cursor_behavior):
    clip = select_text_and_return_it(left_right, number_of_lines_to_search)
    selected_text = clip[0]
    temp_for_previous_clipboard_item = clip[1]
    phrase = str(phrase)
    match = get_start_end_position(selected_text, phrase, left_right)
    if match:
        left_index, right_index = match
    else:
        # phrase not found
        deal_with_phrase_not_found(selected_text, temp_for_previous_clipboard_item, cursor_behavior, left_right)
        return
    left_index, right_index = get_start_end_position(selected_text, phrase, left_right)
    


    # Approach 1: unselect using arrow keys rather than pasting over the existing text. (a little faster) does not work texstudio
    if cursor_behavior == "standard":
        if right_index < round(len(selected_text))/2:
            # it's faster to approach phrase from the left
            Key("left").execute() # unselect text and place cursor on the left side of selection 
            multiline_movement_offset_correction = selected_text[: left_index].count("\r\n")
            movement_offset = left_index - multiline_movement_offset_correction
            # move to the left side of the phrase
            Key("right:%d" %movement_offset).execute()
            # select phrase
            multiline_selection_offset_correction = selected_text[left_index : right_index].count("\r\n")
            selection_offset = len(phrase) - multiline_selection_offset_correction
            Key("s-right:%d" %selection_offset).execute()
        else:
            # it's faster to approach phrase from the right
            Key("right").execute() # unselect text and place cursor on the right side of selection
            multiline_movement_offset_correction = selected_text[left_index :].count("\r\n")
            movement_offset = len(selected_text) -  left_index - multiline_movement_offset_correction
            # move to the left side of the phrase
            Key("left:%d" %movement_offset).execute()
            # select phrase
            multiline_selection_offset_correction = selected_text[left_index : right_index].count("\r\n")
            selection_offset = len(phrase) - multiline_selection_offset_correction
            Key("s-right:%d" %selection_offset).execute()
        
    # Approach 2: paste the selected text over itself rather than simply unselecting. A little slower but works Texstudio
    # comments below indicate the other approach
    if cursor_behavior == "texstudio":
        Key("c-v").execute()
        multiline_movement_correction = selected_text[right_index :].count("\r\n")
        movement_offset = len(selected_text) - right_index - multiline_movement_correction
        Key("left:%d" %movement_offset).execute()
        multiline_selection_correction = selected_text[left_index : right_index].count("\r\n")
        selection_offset = len(selected_text[left_index : right_index]) - multiline_selection_correction
        Key("s-left:%d" %selection_offset).execute()


    # put previous clipboard item back in the clipboard
    Pause("20").execute()
    pyperclip.copy(temp_for_previous_clipboard_item)


def select_until_phrase(left_right, phrase, before_after, number_of_lines_to_search, cursor_behavior):
    # set default for before_after
    if not before_after:
        if left_right  == "left":
            before_after = "after"
        if left_right == "right":
            before_after = "before"

    
    clip = select_text_and_return_it(left_right, number_of_lines_to_search)
    selected_text = clip[0]
    temp_for_previous_clipboard_item = clip[1]
    phrase = str(phrase)
    match = get_start_end_position(selected_text, phrase, left_right)
    if match:
        left_index, right_index = match
    else:
        # phrase not found
        deal_with_phrase_not_found(selected_text, temp_for_previous_clipboard_item, cursor_behavior, left_right)
        return
    left_index, right_index = get_start_end_position(selected_text, phrase, left_right)
    
    # Approach 1: unselect using arrow keys rather than pasting over the existing text. (a little faster) does not work texstudio
    if cursor_behavior == "standard":
        if left_right == "left":
            Key("right").execute() # unselect text and move to left side of selection
            if before_after == "before":
                multiline_correction = selected_text[left_index :].count("\r\n")
                offset = len(selected_text) - left_index - multiline_correction
            if before_after == "after":
                multiline_correction = selected_text[right_index :].count("\r\n")
                offset = len(selected_text) - right_index - multiline_correction
            Key("s-left:%d" %offset).execute()
        if left_right == "right": 
            Key("left").execute() # unselect text and move to the right side of selection
            if before_after == "before":
                multiline_correction = selected_text[: left_index].count("\r\n")
                offset = left_index - multiline_correction
            if before_after == "after":
                multiline_correction = selected_text[: right_index].count("\r\n")
                offset = right_index - multiline_correction
            Key("s-right:%d" %offset).execute()


    # Approach 2: paste the selected text over itself rather than simply unselecting. A little slower but works Texstudio
    if cursor_behavior == "texstudio":
        Key("c-v").execute()  
        if left_right == "left":
            if before_after == "before": 
                selected_text_to_the_right_of_phrase = selected_text[left_index :]    
                multiline_offset_correction = selected_text_to_the_right_of_phrase.count("\r\n")
                offset = len(selected_text) - left_index - multiline_offset_correction
                
            if before_after == "after":
                selected_text_to_the_right_of_phrase = selected_text[right_index :]
                multiline_offset_correction = selected_text_to_the_right_of_phrase.count("\r\n")
                offset = len(selected_text) - right_index - multiline_offset_correction
            
            Key("s-left:%d" %offset).execute()
        if left_right == "right":
            multiline_movement_correction = selected_text.count("\r\n")
            movement_offset = len(selected_text) - multiline_movement_correction
            
            if before_after == "before":
                multiline_selection_correction = selected_text[: left_index].count("\r\n")
                selection_offset = left_index - multiline_movement_correction
            if before_after == "after":
                multiline_selection_correction = selected_text[: right_index].count("\r\n")
                selection_offset = right_index

            # move cursor to original position
            Key("left:%d" %movement_offset).execute()
            # select text
            Key("s-right:%d" %selection_offset).execute()
        
    
    # put previous clipboard item back in the clipboard (consider factoring this out)
    Pause("20").execute()
    pyperclip.copy(temp_for_previous_clipboard_item)


# seems a little inconsistent
def delete_until_phrase(text, phrase, left_right, before_after):
    match = get_start_end_position(text, phrase, left_right)
    if match:
        left_index, right_index = match
    else:
        return
    # the spacing below may need to be tweaked
    if left_right == "left":
        if before_after == "before":
            # if text[-1] == " ":
            #     return text[: left_index] + " "
                return text[: left_index]

        else: # todo: handle before-and-after defaults better
            if text[-1] == " ":
                return text[: right_index] + " "
            else:
                return text[: right_index]
    if left_right == "right":
        if before_after == "after":
            return text[right_index :]
        else:
            if text[0] == " ":
                return " " + text[left_index :]
            else:
                return text[left_index :]

def copypaste_delete_until_phrase(left_right, phrase, number_of_lines_to_search, before_after, cursor_behavior):
    clip = select_text_and_return_it(left_right, number_of_lines_to_search)
    selected_text = clip[0]
    temp_for_previous_clipboard_item = clip[1]
    
    phrase = str(phrase)
    new_text = delete_until_phrase(selected_text, phrase, left_right, before_after)
    if not new_text:
        # phrase not found
        deal_with_phrase_not_found(selected_text, temp_for_previous_clipboard_item, cursor_behavior, left_right)
        return

    # put modified text on the clipboard
    pyperclip.copy(new_text)
    Key("c-v").execute()

    if left_right == "right":
        offset = len(new_text)
        Key("left:%d" %offset).execute()
    # put previous clipboard item back in the clipboard
    Pause("20").execute()
    pyperclip.copy(temp_for_previous_clipboard_item)

