# -*- coding: utf-8 -*-
from pymol.cgo import *
from pymol import cmd
from random import randint
from pymol.vfont import plain
import sys
import os
import subprocess
import time
from datetime import datetime

# -*- coding: utf-8 -*-
##############################################################################
# Vina Docking Plugin for PyMOL
# This script provides a graphical interface for AutoDock Vina docking
# within PyMOL. It allows users to select receptor/ligand PDBQT files,
# define the docking box by clicking residues, and run Vina docking.
# Results are saved directly in the ligand's folder.
#
# Original GetBox plugin (box drawing & selection logic) was written by
# Mengwu Xiao (Hunan University) and is available at:
# https://github.com/MengwuXiao/Getbox-PyMOL-Plugin
#
# Copyright (C) 2014 Mengwu Xiao (box code), modifications for Vina docking
# by Jisuan Yaowu, 2026.
#
# USAGES: See function show_help() or click Help in the menu.
# REFERENCE: drawBoundingBox.py written by Jason Vertrees
#            GetBox Plugin by Mengwu Xiao
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
##############################################################################

# 文件对话框支持
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    import Tkinter as tk
    import tkFileDialog as filedialog

# Global variables
vina_receptor = None
vina_ligand = None
vina_receptor_file = None    # 受体原始文件路径
vina_ligand_file = None      # 配体原始文件路径
vina_box_info = None
vina_box_object = None

def __init__(self):
    self.menuBar.addcascademenu('Plugin', 'Vina Docking Plugin', label='Vina Docking Plugin')
    self.menuBar.addmenuitem('Vina Docking Plugin', 'command', 'SelectReceptor', label='Select Receptor',
                             command=lambda s=self: select_receptor())
    self.menuBar.addmenuitem('Vina Docking Plugin', 'command', 'SelectLigand', label='Select Ligand',
                             command=lambda s=self: select_ligand())
    self.menuBar.addmenuitem('Vina Docking Plugin', 'separator')
    self.menuBar.addmenuitem('Vina Docking Plugin', 'command', 'GetBox', label='Get Box (from selection)',
                             command=lambda s=self: getbox())
    self.menuBar.addmenuitem('Vina Docking Plugin', 'command', 'KeepBox', label='Keep Current Box',
                             command=lambda s=self: keep_box())
    self.menuBar.addmenuitem('Vina Docking Plugin', 'separator', 'sep2')
    self.menuBar.addmenuitem('Vina Docking Plugin', 'command', 'RunVina', label='Run Vina Docking',
                             command=lambda s=self: run_vina_docking())
    self.menuBar.addmenuitem('Vina Docking Plugin', 'command', 'VinaHelp', label='Help',
                             command=lambda s=self: show_help())

def printf(str):
    if sys.version < '3':
        exec ("print str")
    else:
        exec ("print(str)")

def show_help():
    help_text = '''
============================================================
VINA DOCKING PLUGIN - HELP
============================================================

MENU: Plugin -> Vina Docking Plugin

WORKFLOW:
1. Select Receptor (choose a PDBQT file)
2. Select Ligand (choose a PDBQT file)
3. Select active site residues, then Get Box
4. Run Vina Docking

All results will be saved in the same folder as the ligand file.
This makes it easy to handle multiple ligands against one receptor.

COMMANDS:
  select_receptor()   - Load receptor from file
  select_ligand()     - Load ligand from file
  getbox()            - Box from selection (or ligand)
  run_vina_docking()  - Start docking
============================================================
'''
    printf(help_text)

def show_selection():
    global vina_receptor, vina_ligand
    printf("\n" + "="*60)
    printf("CURRENT SELECTIONS:")
    printf("="*60)
    printf("Receptor: %s" % (vina_receptor if vina_receptor else "None"))
    printf("Ligand: %s" % (vina_ligand if vina_ligand else "None"))
    if vina_box_info:
        printf("Box: center=(%.3f, %.3f, %.3f), size=(%.3f, %.3f, %.3f)" %
               (vina_box_info['center_x'], vina_box_info['center_y'], vina_box_info['center_z'],
                vina_box_info['size_x'], vina_box_info['size_y'], vina_box_info['size_z']))
    else:
        printf("Box: None")
    printf("="*60 + "\n")

def select_receptor():
    """弹出文件对话框，加载 PDBQT 受体并记录文件路径"""
    global vina_receptor, vina_receptor_file
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title='Select Receptor (PDBQT)',
        filetypes=[('PDBQT files', '*.pdbqt'), ('PDB files', '*.pdb'), ('All files', '*.*')]
    )
    root.destroy()
    if not file_path:
        printf("Receptor selection cancelled.")
        return
    before = set(cmd.get_names())
    cmd.load(file_path)
    after = set(cmd.get_names())
    new_objs = after - before
    if not new_objs:
        printf("Error: Failed to load receptor file.")
        return
    vina_receptor = list(new_objs)[0]
    vina_receptor_file = file_path
    printf("\n" + "="*60)
    printf("RECEPTOR LOADED: %s" % vina_receptor)
    printf("="*60 + "\n")
    cmd.show_as("cartoon", vina_receptor)
    cmd.color("cyan", vina_receptor)
    show_selection()

def select_ligand():
    """弹出文件对话框，加载 PDBQT 配体并记录文件路径"""
    global vina_ligand, vina_ligand_file
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title='Select Ligand (PDBQT)',
        filetypes=[('PDBQT files', '*.pdbqt'), ('PDB files', '*.pdb'), ('Mol2 files', '*.mol2'), ('All files', '*.*')]
    )
    root.destroy()
    if not file_path:
        printf("Ligand selection cancelled.")
        return
    before = set(cmd.get_names())
    cmd.load(file_path)
    after = set(cmd.get_names())
    new_objs = after - before
    if not new_objs:
        printf("Error: Failed to load ligand file.")
        return
    vina_ligand = list(new_objs)[0]
    vina_ligand_file = file_path
    printf("\n" + "="*60)
    printf("LIGAND LOADED: %s" % vina_ligand)
    printf("="*60 + "\n")
    cmd.show_as("sticks", vina_ligand)
    cmd.color("green", vina_ligand)
    show_selection()

def keep_box():
    global vina_box_info
    if vina_box_info is not None:
        printf("\n" + "="*60)
        printf("KEEPING CURRENT BOX")
        printf("="*60)
        printf("  Center: (%.3f, %.3f, %.3f)" % (vina_box_info['center_x'], vina_box_info['center_y'], vina_box_info['center_z']))
        printf("  Size:   (%.3f, %.3f, %.3f)" % (vina_box_info['size_x'], vina_box_info['size_y'], vina_box_info['size_z']))
        printf("="*60 + "\n")
    else:
        printf("\nWarning: No box defined yet.")
        if vina_ligand is not None:
            printf("  Creating box from ligand...")
            getbox(vina_ligand)
        else:
            printf("  Error: Please select a ligand first!\n")

def getbox(selection="(sele)", extending=5.0):
    """基于选中的残基或配体创建对接盒子"""
    global vina_box_info, vina_box_object
    if selection == "(sele)":
        sel_names = cmd.get_names(selection='(sele)')
        if sel_names:
            selection = "(sele)"
        elif vina_ligand is not None:
            selection = vina_ligand
        else:
            printf("\nError: No selection found!")
            printf("  Hint: Select residues or set a ligand first.\n")
            return
    printf("\nCreating box from: %s" % selection)
    # cmd.hide("spheres")
    # cmd.show("spheres", selection)
    ([minX, minY, minZ], [maxX, maxY, maxZ]) = cmd.get_extent(selection)
    minX -= float(extending)
    minY -= float(extending)
    minZ -= float(extending)
    maxX += float(extending)
    maxY += float(extending)
    maxZ += float(extending)
    box_name = showbox(minX, maxX, minY, maxY, minZ, maxZ)
    vina_box_object = box_name
    printf("\n" + "="*60)
    printf("BOX CREATED SUCCESSFULLY")
    printf("="*60)
    printf("  Center: (%.3f, %.3f, %.3f)" % (vina_box_info['center_x'], vina_box_info['center_y'], vina_box_info['center_z']))
    printf("  Size:   (%.3f, %.3f, %.3f)" % (vina_box_info['size_x'], vina_box_info['size_y'], vina_box_info['size_z']))
    printf("="*60 + "\n")
    return

def showbox(minX, maxX, minY, maxY, minZ, maxZ):
    global vina_box_info
    linewidth = 3.0
    minX, maxX = float(minX), float(maxX)
    minY, maxY = float(minY), float(maxY)
    minZ, maxZ = float(minZ), float(maxZ)
    cmd.delete('axes')
    w, l = 0.5, 5.0
    obj = [
        CYLINDER, minX, minY, minZ, minX + l, minY, minZ, w, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        CYLINDER, minX, minY, minZ, minX, minY + l, minZ, w, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0,
        CYLINDER, minX, minY, minZ, minX, minY, minZ + l, w, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
    ]
    cyl_text(obj, plain, [minX + l, minY, minZ - w], 'X', 0.20, axes=[[3,0,0],[0,3,0],[0,0,3]])
    cyl_text(obj, plain, [minX - w, minY + l, minZ], 'Y', 0.20, axes=[[3,0,0],[0,3,0],[0,0,3]])
    cyl_text(obj, plain, [minX - w, minY, minZ + l], 'Z', 0.20, axes=[[3,0,0],[0,3,0],[0,0,3]])
    cmd.load_cgo(obj, 'axes')
    boundingBox = [
        LINEWIDTH, float(linewidth),
        BEGIN, LINES,
        COLOR, 1.0, 0.0, 0.0,
        VERTEX, minX, minY, minZ, VERTEX, maxX, minY, minZ,
        VERTEX, minX, maxY, minZ, VERTEX, maxX, maxY, minZ,
        VERTEX, minX, maxY, maxZ, VERTEX, maxX, maxY, maxZ,
        VERTEX, minX, minY, maxZ, VERTEX, maxX, minY, maxZ,
        COLOR, 0.0, 1.0, 0.0,
        VERTEX, minX, minY, minZ, VERTEX, minX, maxY, minZ,
        VERTEX, maxX, minY, minZ, VERTEX, maxX, maxY, minZ,
        VERTEX, minX, minY, maxZ, VERTEX, minX, maxY, maxZ,
        VERTEX, maxX, minY, maxZ, VERTEX, maxX, maxY, maxZ,
        COLOR, 0.0, 0.0, 1.0,
        VERTEX, minX, minY, minZ, VERTEX, minX, minY, maxZ,
        VERTEX, minX, maxY, minZ, VERTEX, minX, maxY, maxZ,
        VERTEX, maxX, minY, minZ, VERTEX, maxX, minY, maxZ,
        VERTEX, maxX, maxY, minZ, VERTEX, maxX, maxY, maxZ,
        END
    ]
    boxName = "box_" + str(randint(0, 10000))
    while boxName in cmd.get_names():
        boxName = "box_" + str(randint(0, 10000))
    cmd.load_cgo(boundingBox, boxName)
    SizeX, SizeY, SizeZ = maxX - minX, maxY - minY, maxZ - minZ
    CenterX, CenterY, CenterZ = (maxX + minX)/2, (maxY + minY)/2, (maxZ + minZ)/2
    VinaBox = "--center_x %.1f --center_y %.1f --center_z %.1f --size_x %.1f --size_y %.1f --size_z %.1f" % (
        CenterX, CenterY, CenterZ, SizeX, SizeY, SizeZ)
    printf("\nVina box command: %s" % VinaBox)
    cmd.zoom(boxName)
    vina_box_info = {
        'center_x': CenterX, 'center_y': CenterY, 'center_z': CenterZ,
        'size_x': SizeX, 'size_y': SizeY, 'size_z': SizeZ
    }
    return boxName

def run_vina_docking(exhaustiveness=8, num_modes=9, vina_path="vina"):
    global vina_receptor, vina_ligand, vina_receptor_file, vina_ligand_file, vina_box_info
    printf("\n" + "="*60)
    printf("AUTODOCK VINA DOCKING")
    printf("="*60)
    if vina_receptor is None:
        printf("Error: No receptor selected!")
        return
    if vina_ligand is None:
        printf("Error: No ligand selected!")
        return
    if vina_box_info is None:
        printf("Warning: No box defined, creating from ligand...")
        getbox(vina_ligand, 5.0)
        if vina_box_info is None:
            printf("Error: Failed to create box!")
            return

    printf("\nSettings:")
    printf("  Receptor: %s" % vina_receptor)
    printf("  Ligand: %s" % vina_ligand)
    printf("  Exhaustiveness: %d" % exhaustiveness)
    printf("  Number of modes: %d" % num_modes)
    box = vina_box_info
    printf("  Box center: (%.3f, %.3f, %.3f)" % (box['center_x'], box['center_y'], box['center_z']))
    printf("  Box size: (%.3f, %.3f, %.3f)" % (box['size_x'], box['size_y'], box['size_z']))
    printf("-"*60)

    # 将输出文件保存到配体所在目录
    ligand_dir = os.path.dirname(vina_ligand_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    config_file = os.path.join(ligand_dir, "vina_config_%s.txt" % timestamp)
    log_file = os.path.join(ligand_dir, "vina_log_%s.log" % timestamp)
    out_file = os.path.join(ligand_dir, "docking_out_%s.pdbqt" % timestamp)

    # 写入 Vina 配置文件，直接引用原始文件（路径用双引号包裹防空格）
    with open(config_file, 'w') as f:
        f.write('receptor = "%s"\n' % vina_receptor_file)
        f.write('ligand = "%s"\n' % vina_ligand_file)
        f.write("center_x = %.3f\n" % box['center_x'])
        f.write("center_y = %.3f\n" % box['center_y'])
        f.write("center_z = %.3f\n" % box['center_z'])
        f.write("size_x = %.3f\n" % box['size_x'])
        f.write("size_y = %.3f\n" % box['size_y'])
        f.write("size_z = %.3f\n" % box['size_z'])
        f.write("exhaustiveness = %d\n" % exhaustiveness)
        f.write("num_modes = %d\n" % num_modes)
        f.write('out = "%s"\n' % out_file)
        f.write('log = "%s"\n' % log_file)

    printf("\nRunning Vina docking directly in ligand folder...")
    cmd_str = '%s --config "%s"' % (vina_path, config_file)
    printf("Command: %s" % cmd_str)

    start_time = time.time()
    process = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    end_time = time.time()

    if process.returncode != 0:
        printf("\nERROR: Vina docking failed!")
        if stderr:
            printf("Error message: %s" % stderr.decode('utf-8'))
        return

    printf("\n" + "="*60)
    printf("DOCKING COMPLETED SUCCESSFULLY!")
    printf("="*60)
    printf("Time elapsed: %.2f seconds" % (end_time - start_time))

    # 解析对接结果
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log_content = f.read()

        scores = []
        in_table = False
        skip_headers = 0
        for line in log_content.split('\n'):
            if '-----+------------+----------+----------' in line:
                in_table = True
                skip_headers = 2
                continue
            if in_table and skip_headers > 0:
                skip_headers -= 1
                continue
            if in_table:
                if not line.strip() or line.startswith('Writing'):
                    break
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    try:
                        scores.append(float(parts[1]))
                    except:
                        pass

        # 生成友好的摘要文件（同样保存在配体目录）
        summary_file = os.path.join(ligand_dir, "vina_summary_%s.log" % timestamp)
        with open(summary_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("AutoDock Vina Docking Results\n")
            f.write("=" * 70 + "\n")
            f.write("Date: %s\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            f.write("Receptor: %s\n" % vina_receptor)
            f.write("Ligand: %s\n" % vina_ligand)
            f.write("Exhaustiveness: %d\n" % exhaustiveness)
            f.write("Number of modes: %d\n" % num_modes)
            f.write("Box center: (%.3f, %.3f, %.3f)\n" % (box['center_x'], box['center_y'], box['center_z']))
            f.write("Box size: (%.3f, %.3f, %.3f)\n" % (box['size_x'], box['size_y'], box['size_z']))
            f.write("Time elapsed: %.2f seconds\n" % (end_time - start_time))
            f.write("-" * 70 + "\n")
            f.write("DOCKING SCORES:\n")
            for i, score in enumerate(scores[:num_modes], 1):
                f.write("Mode %2d: %.2f kcal/mol\n" % (i, score))
            f.write("\nBest score: %.2f kcal/mol (Mode 1)\n" % (scores[0] if scores else 0))
            f.write("Full log: %s\n" % log_file)
            f.write("Output PDBQT: %s\n" % out_file)

        printf("\n" + "-"*60)
        printf("DOCKING SCORES:")
        printf("-"*60)
        for i, score in enumerate(scores[:num_modes], 1):
            printf("Mode %2d: %.2f kcal/mol" % (i, score))
        if scores:
            printf("\nBest score: %.2f kcal/mol (Mode 1)" % scores[0])
        printf("\n" + "-"*60)
        printf("Summary saved to: %s" % summary_file)
        printf("Log file saved to: %s" % log_file)

        # 加载对接结果到 PyMOL
        if os.path.exists(out_file):
            cmd.load(out_file, "docking_results")
            cmd.show_as("sticks", "docking_results")
            cmd.color("orange", "docking_results")
            printf("Docking results loaded as 'docking_results'")
        printf("="*60 + "\n")
    else:
        printf("Warning: Vina log file not found.")

def rmhet():
    cmd.select("rmhet", "hetatm")
    cmd.remove("rmhet")

def autobox(extending=5.0):
    cmd.remove('solvent')
    cmd.select("Ions", "((resn PO4) | (resn SO4) | (resn ZN) | (resn CA) | (resn MG) | (resn CL)) & hetatm")
    cmd.remove("Ions")
    cmd.delete("Ions")
    cmd.select("ChainAHet", "hetatm & chain A")
    getbox("ChainAHet", extending)

cmd.extend("select_receptor", select_receptor)
cmd.extend("select_ligand", select_ligand)
cmd.extend("show_selection", show_selection)
cmd.extend("getbox", getbox)
cmd.extend("keep_box", keep_box)
cmd.extend("showbox", showbox)
cmd.extend("autobox", autobox)
cmd.extend("rmhet", rmhet)
cmd.extend("run_vina_docking", run_vina_docking)
cmd.extend("show_help", show_help)

printf("\n" + "="*60)
printf("VINA DOCKING PLUGIN LOADED!")
printf("="*60)
printf("")
printf("MENU: Plugin -> Vina Docking Plugin")
printf("")
printf("WORKFLOW:")
printf("  1. Select Receptor (choose .pdbqt file)")
printf("  2. Select Ligand (choose .pdbqt file)")
printf("  3. Select active-site residues, then Get Box")
printf("  4. Run Vina Docking")
printf("")
printf("  All output files are saved in the LIGAND's folder.")
printf("  Perfect for docking multiple ligands against one receptor.")
printf("")
printf("OR use commands:")
printf("  select_receptor()  - Load receptor")
printf("  select_ligand()    - Load ligand")
printf("  getbox()           - Create box")
printf("  run_vina_docking() - Run docking")
printf("="*60 + "\n")