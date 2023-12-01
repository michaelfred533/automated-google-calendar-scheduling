# --- get_time() ---

class TooMuchStudyTimeError(Exception):
    """
    The study time entered by the user
    is much for 1 day.
    """

# --- get_topics() ---

class MissingCommaError(Exception):
    """
    The topic list is missing ", "
    """

class TooManyTopicsError(Exception):
    """
    Too many topics to study in 1 day
    """

class DuplicateTopicsError(Exception):
    """
    The topic list has duplicates
    """

# --- get_study_type_list() ---

class LengthMismatchError(Exception):
    """
    The input for study types does not match the length of the topics list.
    """

class IncorrectTypeError(Exception):
    """
    The input does not match the existing types
    """

# --- get_proportions() ---

class ProportionsDontAddToOneError(Exception):
    """
    The proportions entered by the user do not add to 1.
    """

# --- Event class data validation ---

class StartEndDurationMismatchError(Exception):
    """
    The start and end times of the event are not consistent with the duration
    """ 

    