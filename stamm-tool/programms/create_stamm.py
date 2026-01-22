import zipfile
import os
from tkinter import Tk, filedialog

def select_dfiles():
    return filedialog.askopenfilenames(
        title="Select .dfile profile files",
        filetypes=[("DFile profiles", "*.dfile")]
    )

def select_relationships_json():
    return filedialog.askopenfilename(
        title="Select relationships.json",
        filetypes=[("JSON file", "*.json")]
    )

def select_output_stamm():
    return filedialog.asksaveasfilename(
        title="Save .stamm file",
        defaultextension=".stamm",
        filetypes=[("Stamm file", "*.stamm")]
    )

def create_stamm(dfiles, relationships_json, output_stamm):
    with zipfile.ZipFile(output_stamm, "w", zipfile.ZIP_DEFLATED) as stamm:
        # Add profile files
        for dfile in dfiles:
            filename = os.path.basename(dfile)
            stamm.write(dfile, f"profiles/{filename}")

        # Add relationships.json
        stamm.write(relationships_json, "relationships.json")

    print("STAMM file created successfully:")
    print(output_stamm)

def main():
    root = Tk()
    root.withdraw()  # Hide main window

    dfiles = select_dfiles()
    if not dfiles:
        print("No .dfile files selected.")
        return

    relationships_json = select_relationships_json()
    if not relationships_json:
        print("No relationships.json selected.")
        return

    output_stamm = select_output_stamm()
    if not output_stamm:
        print("No output file selected.")
        return

    create_stamm(dfiles, relationships_json, output_stamm)

if __name__ == "__main__":
    main()
