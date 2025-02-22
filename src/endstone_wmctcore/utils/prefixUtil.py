from endstone import ColorFormat

def debugLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.MATERIAL_REDSTONE}DEBUG{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"


def infoLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.YELLOW}>{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"


def modLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.RED}ML{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"


def griefLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.GOLD}GL{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"

def errorLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.RED}ERROR LOG{ColorFormat.DARK_GRAY}] {ColorFormat.RED}"
