### RunVina - A PyMOL Plugin for One‑Click AutoDock Vina Docking
**RunVina** brings the power of AutoDock Vina directly into the PyMOL interface.  
Define the binding box by simply clicking on active‑site residues, load your receptor and ligand PDBQT files through file dialogs, and start docking with a single menu click.  
All results are automatically saved in the **ligand’s folder** – clean, organised, and ready for analysis.
### Download
https://github.com/JisuanYaowu/RunVina/blob/main/RunVina.py
###  📥 Installation
 Download the latest `run_vina.py` from this repository.
 Open PyMOL->Plugin->(Plugin Manager)->Install (New) Plugin->Find RunVina.py ->Restart PyMOL->Finished. 
Restart PyMOL. You will see a new menu: **Plugin → Vina Docking Plugin**.
It has six submenus: Select Receptor, Select Ligand，Get Box (from selection)，Keep Current Box，Run Vina Docking，Help.
 <img width="3784" height="2515" alt="图片1" src="https://github.com/user-attachments/assets/5c9a4b71-6bd4-4c75-9790-9da120740133" />
<img width="2922" height="2255" alt="图片2" src="https://github.com/user-attachments/assets/ae2d2cbe-71dd-4810-9661-a573e260fe42" />
<img width="2492" height="1388" alt="图片3" src="https://github.com/user-attachments/assets/1069c883-f6cc-422c-ac86-6151075c1713" />
<img width="1098" height="568" alt="图片4" src="https://github.com/user-attachments/assets/b765bbb5-5a6b-47ef-a115-756010e63282" />

### ✨ Features

- 🖱️ **Visual box definition** – click residues in PyMOL and the box is generated instantly (based on the well‑known GetBox plugin).
- 📂 **File‑dialog loading** – select receptor/ligand `.pdbqt` files directly from the menu, no need to drag & drop.
- 🚀 **One‑click docking** – hit “Run Vina Docking” and Vina runs in the background; progress and scores appear in the console.
- 📁 **Smart output** – log, config, docked poses and a readable summary are saved **in the same folder as the ligand**, making multi‑ligand studies painless.
- 🧹 **Zero temporary junk** – no temp directories are left behind.
- 🧩 **Extensible** – all functions are also available as PyMOL commands (`select_receptor()`, `run_vina_docking()`, etc.).
- 📜 **Respects original work** – box drawing code is adapted from GetBox (Mengwu Xiao, GPLv3), with full attribution.

### 📋 Requirements

- **PyMOL** ≥ 2.4 (open‑source or Schrödinger version)
- **AutoDock Vina** (the `vina` executable must be in your system PATH)
- **Python** with `tkinter` (usually included with PyMOL’s Python)
- Pre‑prepared receptor and ligand files in **PDBQT format** (e.g. generated with MGLTools or `prepare_receptor4.py`)

### 🚦 Usage

## Menu workflow (recommended)

1. **Select Receptor**  
   Click `Plugin → Vina Docking Plugin → Select Receptor` and choose your receptor `.pdbqt` file.
2. **Select Ligand**  
   Click `Select Ligand` and choose your ligand `.pdbqt` file.
3. **Define the box**  
   In the PyMOL viewer, **ctrl‑click** a few residues around the binding site, then click `Get Box (from selection)`. A red wireframe box appears.
4. **Run docking**  
   Click `Run Vina Docking`. The console shows progress, scores, and the results are loaded as `docking_results`.
## ⌨️ Command Line Interface

All functions are also accessible via PyMOL console commands:

select_receptor()      # Open file dialog to select the receptor
select_ligand()        # Open file dialog to select the ligand
getbox()               # Create a docking box from the current selection
run_vina_docking()     # Start docking with default parameters

Advanced parameters can be passed directly:

run_vina_docking(exhaustiveness=16, num_modes=20, vina_path="/usr/bin/vina")

## 📁 Output Files

After each docking run, the following files are generated in the **ligand's folder**:

| File | Description |
|------|-------------|
| `vina_config_YYYYMMDD_HHMMSS.txt` | Vina configuration used for this run |
| `vina_log_YYYYMMDD_HHMMSS.log` | Raw output log from Vina |
| `vina_summary_YYYYMMDD_HHMMSS.log` | Human‑readable summary with scores and file paths |
| `docking_out_YYYYMMDD_HHMMSS.pdbqt` | Docked poses (automatically loaded into PyMOL) |

Each run receives a unique timestamp, so previous results are never overwritten.

## ⚙️ Configuration

Default docking parameters are **exhaustiveness = 8** and **num_modes = 9**.  
You can permanently change them by editing the default values in the `run_vina_docking()` function, or override them on the fly:

run_vina_docking(exhaustiveness=16, num_modes=20)

## 🔧 Troubleshooting

**Q: The menu text is invisible in PyMOL.**  
A: Certain GUI themes can cause this. Try running `cmd.set("gui_theme", "classic")` in the PyMOL console and restart. Alternatively, use the command-line functions – they work identically.

**Q: Vina reports "File format not supported".**  
A: Ensure your receptor and ligand files are valid PDBQT files. This plugin does not convert PDB to PDBQT; you must prepare them beforehand (e.g., with MGLTools).

**Q: The system cannot find the `vina` command.**  
A: Provide the full path to the Vina executable when calling the function:  
`run_vina_docking(vina_path="C:/Program Files/vina/vina.exe")`

**Q: I want the output to be saved in the receptor folder instead of the ligand folder.**  
A: Open `rvina.py`, locate the line `ligand_dir = os.path.dirname(vina_ligand_file)` and change `vina_ligand_file` to `vina_receptor_file`.

## 🤝 Credits

- Box drawing and selection logic adapted from the [GetBox Plugin](https://github.com/MengwuXiao/Getbox-PyMOL-Plugin) by **Mengwu Xiao** (Hunan University).
- Original bounding‑box code inspired by **drawBoundingBox.py** by **Jason Vertrees** (PyMOLWiki).
- Vina docking integration, file management, and graphical interface added by **Jisuan Yaowu (Computational Drug)**, 2026.

## 📜 License

This project is licensed under the **GNU General Public License v3.0** – see the [LICENSE](LICENSE) file for details.  
The GetBox portion retains its original GPLv3 license, and all modifications are released under the same terms.

## 📬 Contact

For questions, suggestions, or bug reports, please open an issue on this repository or follow our WeChat official account: **计算药物** (Computational Drug).
