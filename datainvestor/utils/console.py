BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def string_colour(text, colour=WHITE):
    """
    Crea una stringa di testo in un colore particolare sul terminale.
    """
    seq = "\x1b[1;%dm" % (30 + colour) + text + "\x1b[0m"
    return seq
