from endstone import ColorFormat

def debugLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.MATERIAL_REDSTONE}DEBUG{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"

def infoLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.YELLOW}>{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"

def trailLog():
    return f"{ColorFormat.BOLD}{ColorFormat.YELLOW}--> {ColorFormat.RESET}"

def modLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.RED}ML{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}{ColorFormat.GOLD}"

def griefLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.GOLD}GL{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"

def noticeLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.RED}!{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}{ColorFormat.RED}"

def errorLog():
    return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.RED}X{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}{ColorFormat.RED}"
