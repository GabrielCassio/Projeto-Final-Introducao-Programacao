from pathlib import Path

class FinderPaths():
    absoluteRootPath = Path.cwd()
    curFilePath = Path(__file__).resolve()

    def RelativeToAbsPath(self, fullName: str, path: str = None, target: str = None) -> Path:
        # Separando caminho relativo
        sepNames = fullName.split("/")

        finalPath = self.absoluteRootPath / Path(fullName)
        return finalPath

__all__ = ["FinderPaths"]