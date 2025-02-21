from endstone._internal.endstone_python import ColorFormat
class Prefix:

    def infoLog(self):
        return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.YELLOW}>{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"

    def modLog(self):
        return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.RED}ML{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"

    def griefLog(self):
        return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.GOLD}GL{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"

    def debugLog(self):
        return f"{ColorFormat.BOLD}{ColorFormat.DARK_GRAY}[{ColorFormat.MATERIAL_REDSTONE}DEBUG{ColorFormat.DARK_GRAY}] {ColorFormat.RESET}"