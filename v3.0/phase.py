import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
from pathlib import Path

# Helpers

def polar_to_complex(mag, ang_deg):
    ang_rad = math.radians(ang_deg)
    return mag * (math.cos(ang_rad) + 1j * math.sin(ang_rad))

def complex_to_polar(z):
    mag = abs(z)
    ang = math.degrees(math.atan2(z.imag, z.real))
    if ang > 180:
        ang -= 360
    if ang <= -180:
        ang += 360
    return mag, ang

# pyinstaller --onefile --noconsole --icon=icon.ico --name "PhasorCalc App" --add-data "icon.ico;." phase.py

def resource_path(relative_path: str) -> str:
    try:
        #Quando empacotado com PyInstaller
        base_path = Path(sys._MEIPASS)  # pasta temporária criada pelo PyInstaller
    except Exception:
        #Quando executado como um script normal
        base_path = Path(__file__).resolve().parent
    return str((base_path / relative_path).resolve())

class ToolTip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", "9")
        )
        label.pack(ipadx=6, ipady=4)

    def hide(self, event=None):
        self.unschedule()
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

class PhasorCalcApp:
    def __init__(self, root):
        self.setup_styles()

        self.root = root
        root.title('Calculadora de Fasores de Corrente - v2.0')
        self.loads = [] # List to store load data
        self.create_ui()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')  # You can choose other themes like 'clam', 'alt', 'default', 'classic', etc.

        self.style.configure(
            'TEntry',
            padding=6,
            relief='flat'
        )

        self.style.configure(
            'Primary.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=(10, 6)
        )

        self.style.configure(
            'Secondary.TButton',
            padding=(8, 5)
        )

        self.style.configure(
            'Treeview.Heading',
            font=('Segoe UI', 9, 'bold')
        )

        self.style.configure(
            'Treeview',
            rowheight=26,
            font=('Segoe UI', 9)
        )

        self.style.configure(
            'Text',
            font=('Consolas', 10),
            background='#f9f9f9',
            relief='flat',
            padx=8,
            pady=8
        )

        self.style.configure(
            'TLabelframe.Label',
            font=('Segoe UI', 10, 'bold')
        )

    def create_ui(self):
        icon_path = resource_path('icon.ico')  # Path to your icon file

        root.iconbitmap(icon_path)
 
        self.root.geometry('1000x700+0+0')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=2)
        self.root.rowconfigure(1, weight=0)

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky='nsew')

        main_frame.columnconfigure(0, weight=1)  # painel esquerdo
        main_frame.columnconfigure(1, weight=3)  # resultados / gráfico
        main_frame.rowconfigure(2, weight=1)

        # Grid Frame Configuration
        grid_frame = ttk.Labelframe(main_frame, text='Configuração da Rede')
        grid_frame.grid(row=0, column=0, sticky='ew', pady=8, padx=5)

        grid_frame.columnconfigure(1, weight=1)

        ttk.Label(grid_frame, text='Tensão de Linha (V):').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.line_voltage_entry = ttk.Entry(grid_frame, width=10)
        self.line_voltage_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.line_voltage_entry.insert(0, '220') # Default value
        self.line_voltage_entry.bind('<KeyRelease>', self.on_voltage_change)
        ToolTip(self.line_voltage_entry, '🔌 Tensão de linha: Tensão entre duas fases (Vab, Vbc, Vca) da rede. Exemplo: 220V, 380V.')

        # Input Frame for new loads
        input_frame = ttk.Labelframe(main_frame, text='Adicionar Nova Carga')
        input_frame.grid(row=1, column=0, sticky='ew', pady=8, padx=5)

        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text='Nome da Carga:').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.load_name_entry = ttk.Entry(input_frame, width=20)
        self.load_name_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(input_frame, text='Potência (W):').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.power_entry = ttk.Entry(input_frame, width=10)
        self.power_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        ToolTip(self.power_entry, '⚡ Potência Ativa (W): Potência real consumida ou gerada pela carga. \nUse valores positivos para cargas consumidoras e negativos para geradores.')

        ttk.Label(input_frame, text='Fator de Potência (FP):').grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.pf_entry = ttk.Entry(input_frame, width=5)
        self.pf_entry.grid(row=1, column=3, sticky='ew', padx=5, pady=2)
        self.pf_entry.insert(0, '1.0') # Default value
        ToolTip(self.pf_entry, '🔋 Fator de Potência (FP)\nFP = cos(φ).\n Relação entre potência ativa e aparente. \nValor entre 0 e 1. Exemplo: 0.8, 0.95, 1.0.')

        # Radiobuttons for Power Factor Type (Inductive/Capacitive)
        self.pf_type_var = tk.StringVar(value='Indutivo') # Default to Indutivo
        
        pf_type_frame = ttk.Frame(input_frame)
        pf_type_frame.grid(row=2, column=2, columnspan=2, sticky='w', padx=5, pady=2)
        ToolTip(pf_type_frame, 'Tipo de Fator de Potência:\nIndutivo: Carga que consome potência reativa (motor, transformador).\nCapacitivo: Carga que fornece potência reativa (banco de capacitores).')
        
        ttk.Label(pf_type_frame, text='Tipo FP:').pack(side='left')
        ttk.Radiobutton(pf_type_frame, text='Indutivo', variable=self.pf_type_var, value='Indutivo').pack(side='left')
        ttk.Radiobutton(pf_type_frame, text='Capacitivo', variable=self.pf_type_var, value='Capacitivo').pack(side='left')

        ttk.Label(input_frame, text='Fase(s):').grid(row=3, column=0, sticky='w', padx=5, pady=2)
        
        self.phase_a_var = tk.BooleanVar()
        self.phase_b_var = tk.BooleanVar()
        self.phase_c_var = tk.BooleanVar()
        self.neutral_var = tk.BooleanVar()

        cb_a = ttk.Checkbutton(input_frame, text='A', variable=self.phase_a_var)
        cb_a.grid(row=4, column=1, sticky='w', padx=5, pady=2)
        cb_b = ttk.Checkbutton(input_frame, text='B', variable=self.phase_b_var)
        cb_b.grid(row=4, column=2, sticky='w', padx=5, pady=2)
        cb_c = ttk.Checkbutton(input_frame, text='C', variable=self.phase_c_var)
        cb_c.grid(row=4, column=3, sticky='w', padx=5, pady=2)
        cb_n = ttk.Checkbutton(input_frame, text='Neutro', variable=self.neutral_var)
        cb_n.grid(row=4, column=4, sticky='w', padx=5, pady=2)

        ToolTip(cb_a, 'Selecione os condutores às quais a carga está conectada.\nPode ser uma ou mais fases (A, B, C) e/ou Neutro (N).')
        ToolTip(cb_b, 'Selecione os condutores às quais a carga está conectada.\nPode ser uma ou mais fases (A, B, C) e/ou Neutro (N).')
        ToolTip(cb_c, 'Selecione os condutores às quais a carga está conectada.\nPode ser uma ou mais fases (A, B, C) e/ou Neutro (N).')
        ToolTip(cb_n, 'Selecione os condutores às quais a carga está conectada.\nPode ser uma ou mais fases (A, B, C) e/ou Neutro (N).')

        add_load_btn = ttk.Button(input_frame, text='➕ Adicionar Carga', style='Primary.TButton', command=self.add_load)
        add_load_btn.grid(row=5, column=0, columnspan=5, pady=10)

        # Loads List Frame
        loads_list_frame = ttk.Labelframe(main_frame, text='Cargas Adicionadas')
        loads_list_frame.grid(row=2, column=0, sticky='nsew', pady=8, padx=5)

        self.loads_tree = ttk.Treeview(loads_list_frame, columns=('Nome', 'Potência', 'FP', 'Tipo FP', 'Fases', 'Corrente'), show='headings')
        self.loads_tree.heading('Nome', text='Nome')
        self.loads_tree.heading('Potência', text='Potência (W)')
        self.loads_tree.heading('FP', text='FP')
        self.loads_tree.heading('Tipo FP', text='Tipo FP')
        self.loads_tree.heading('Fases', text='Fases')
        self.loads_tree.heading('Corrente', text='Corrente (A)')
        self.loads_tree.column('Nome', width=100)
        self.loads_tree.column('Potência', width=80)
        self.loads_tree.column('FP', width=40)
        self.loads_tree.column('Tipo FP', width=60)
        self.loads_tree.column('Fases', width=80)
        self.loads_tree.column('Corrente', width=80)
        self.loads_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Buttons for Modify and Delete
        btn_frame = ttk.Frame(loads_list_frame)
        btn_frame.grid(row=1, column=0, sticky='ew', pady=5)

        modify_load_btn = ttk.Button(btn_frame, text='✏️ Modificar Carga', style="Secondary.TButton", command=self.modify_load)
        modify_load_btn.pack(side='left', padx=5)

        delete_load_btn = ttk.Button(btn_frame, text='🗑️ Deletar Carga', style="Secondary.TButton", command=self.delete_load)
        delete_load_btn.pack(side='left', padx=5)

        loads_list_frame.columnconfigure(0, weight=1)
        loads_list_frame.rowconfigure(0, weight=1)

        # Results and Plot Frame
        results_plot_frame = ttk.Labelframe(main_frame, text='Resultados e Diagrama Fasorial')
        results_plot_frame.grid(row=0, column=1, rowspan=3, sticky='nsew', pady=8, padx=5)
        results_plot_frame.rowconfigure(1, weight=1)
        results_plot_frame.columnconfigure(0, weight=1)

        self.result_text = tk.Text(results_plot_frame, height=10, width=40)
        self.result_text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.fig = Figure(figsize=(5,4), tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=results_plot_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        footer_frame = ttk.Frame(root, padding=(10, 8, 10, 12))
        footer_frame.grid(row=2, column=0, sticky='ew')

        rodape = ttk.Label(footer_frame, text="Desenvolvido por Pedro Akio Sakuma - Engenharia de Desenvolvimento © 2025", anchor='e', font=("Segoe UI", 9)) # Label fixo no rodapé
        rodape.pack(fill='x')

    def on_voltage_change(self, event):
        self.calculate_and_plot()

    def add_load(self):
        name = self.load_name_entry.get().strip()
        power_str = self.power_entry.get().strip()
        pf_str = self.pf_entry.get().strip()
        pf_type = self.pf_type_var.get()
        phases = []
        if self.phase_a_var.get():
            phases.append('A')
        if self.phase_b_var.get():
            phases.append('B')
        if self.phase_c_var.get():
            phases.append('C')
        if self.neutral_var.get():
            phases.append('N')

        if not name or not power_str or not phases or not pf_str:
            messagebox.showerror('Erro', 'Por favor, preencha todos os campos e selecione pelo menos uma fase.')
            return

        try:
            power = float(power_str)
            pf = float(pf_str)
            if not (0 <= pf <= 1):
                messagebox.showerror('Erro', 'O Fator de Potência deve estar entre 0 e 1.')
                return
            line_voltage = float(self.line_voltage_entry.get().strip())
            if line_voltage <= 0:
                messagebox.showerror('Erro', 'A tensão de linha deve ser um valor positivo.')
                return
        except ValueError:
            messagebox.showerror('Erro', 'Potência, Fator de Potência ou Tensão de Linha inválida. Por favor, insira um número.')
            return

        if pf == 0 and power != 0:
            messagebox.showerror('Erro', 'Fator de Potência não pode ser zero se a Potência Ativa não for zero.')
            return

        num_phases_selected = len([p for p in phases if p in ["A", "B", "C"]])

        if num_phases_selected == 1 and "N" in phases:
            # Single-phase load (e.g., R-N)
            # OK
            pass
        elif num_phases_selected == 1 and "N" not in phases:
            # If only one phase selected without Neutral, assume it's a single-phase load to Neutral
            # Not OK             
            messagebox.showwarning("Aviso", "Selecione pelo menos mais um condutor (Neutro ou outra fase).")
            return
        elif num_phases_selected == 2 and "N" not in phases:
            # Two-phase load (e.g., A-B for an inverter)
            # For a load connected between two phases, the voltage across it is the line-to-line voltage.
            # OK
            pass
        elif num_phases_selected == 2 and "N" in phases:
            # Two phases selected along with Neutral is not a standard configuration
            # It indicates a unbalanced load but is not typically used for simplified calculations.
            # Not OK
            messagebox.showwarning("Aviso", "Tipo de Carga inválida para cálculo simplificado com duas fases e Neutro.")
            return       
        elif num_phases_selected == 3 and "N" not in phases:
            # Three-phase load (e.g., A-B-C)
            # OK
            pass
        elif num_phases_selected == 3 and "N" in phases:
            # Three phases along with Neutral is not a standard configuration for load connection.
            # Not OK
            messagebox.showwarning("Aviso", "Tipo de Carga inválida para cálculo simplificado com três fases e Neutro.")
            return
        else:
            messagebox.showerror("Erro", "Combinação de fases não suportada para cálculo de corrente simplificado. Por favor, selecione uma fase e Neutro, duas fases (sem Neutro), ou A, B e C (sem Neutro) para trifásico.")
            return

        load_data = {
            "name": name, 
            "power": power, 
            "pf": pf, 
            "pf_type": pf_type, 
            "phases": phases, 
            "current": 0, # Será calculado em calculate_and_plot
            "line_voltage": line_voltage
        }
        self.loads.append(load_data)
        self.update_loads_display()
        self.calculate_and_plot()

        self.load_name_entry.delete(0, tk.END)
        self.power_entry.delete(0, tk.END)
        self.pf_entry.delete(0, tk.END)
        self.pf_entry.insert(0, '1.0')
        self.phase_a_var.set(False)
        self.phase_b_var.set(False)
        self.phase_c_var.set(False)
        self.neutral_var.set(False)

    def delete_load(self):
        selected_item = self.loads_tree.selection()
        if not selected_item:
            messagebox.showwarning('Aviso', 'Por favor, selecione uma carga para deletar.')
            return

        item_index = self.loads_tree.index(selected_item[0])

        if 0 <= item_index < len(self.loads):
            del self.loads[item_index]
            self.update_loads_display()
            self.calculate_and_plot()

    def modify_load(self):
        selected_item = self.loads_tree.selection()
        if not selected_item:
            messagebox.showwarning('Aviso', 'Por favor, selecione uma carga para modificar.')
            return

        item_index = self.loads_tree.index(selected_item[0])
        if 0 <= item_index < len(self.loads):
            load_to_modify = self.loads[item_index]

            self.load_name_entry.delete(0, tk.END)
            self.load_name_entry.insert(0, load_to_modify["name"])

            self.power_entry.delete(0, tk.END)
            self.power_entry.insert(0, str(load_to_modify["power"]))

            self.pf_entry.delete(0, tk.END)
            self.pf_entry.insert(0, str(load_to_modify["pf"]))
            
            self.pf_type_var.set(load_to_modify["pf_type"])

            self.phase_a_var.set("A" in load_to_modify["phases"])
            self.phase_b_var.set("B" in load_to_modify["phases"])
            self.phase_c_var.set("C" in load_to_modify["phases"])
            self.neutral_var.set("N" in load_to_modify["phases"])

            del self.loads[item_index]
            self.update_loads_display()
            self.calculate_and_plot()

    def update_loads_display(self):
        for item in self.loads_tree.get_children():
            self.loads_tree.delete(item)
        for load in self.loads:
            phases_str = ', '.join(load['phases'])
            self.loads_tree.insert('', 'end', values=(load['name'], load['power'], load['pf'], load['pf_type'], phases_str, f'{load['current']:.2f}'))

    def calculate_and_plot(self):
        try:
            line_voltage = float(self.line_voltage_entry.get().strip())
            if line_voltage <= 0:
                return
        except ValueError:
            return
        
        voltage_phase = line_voltage / math.sqrt(3)

        total_ia = 0 + 0j
        total_ib = 0 + 0j
        total_ic = 0 + 0j
        total_in = 0 + 0j

        total_p = 0.0
        total_q = 0.0

        for load in self.loads:
            power = load['power']
            pf = load['pf']
            pf_type = load['pf_type']
            phases = load['phases']
            
            if pf == 0:
                apparent_power = 0.0
            else:
                apparent_power = power / pf
            
            current_mag = 0.0
            num_phases_selected = len([p for p in phases if p in ["A", "B", "C"]])

            if num_phases_selected == 1 and "N" in phases:
                current_mag = abs(apparent_power) / voltage_phase
            elif num_phases_selected == 2 and "N" not in phases:
                current_mag = abs(apparent_power) / line_voltage
            elif num_phases_selected == 3 and "N" not in phases:
                current_mag = abs(apparent_power) / (math.sqrt(3) * line_voltage)
            elif num_phases_selected == 1 and "N" not in phases:
                current_mag = abs(apparent_power) / voltage_phase
            
            load['current'] = current_mag if power >= 0 else -current_mag
            
            if pf != 1 and pf != 0:
                q_mag = power * math.tan(math.acos(pf))
                if power >= 0:
                    q_load = q_mag if pf_type == 'Indutivo' else -q_mag
                else:
                    q_load = -q_mag if pf_type == 'Indutivo' else q_mag
            else:
                q_load = 0.0

            total_p += power
            total_q += q_load

            angle_shift = math.degrees(math.acos(pf))
            
            if power >= 0:
                current_angle = -angle_shift if pf_type == 'Indutivo' else angle_shift
            else:
                current_angle = angle_shift if pf_type == 'Indutivo' else -angle_shift
                current_angle += 180

            if num_phases_selected == 1 and "N" in phases:
                if 'A' in phases:
                    total_ia += polar_to_complex(current_mag, 0 + current_angle)
                    total_in += polar_to_complex(current_mag, 180 + current_angle)
                elif 'B' in phases:
                    total_ib += polar_to_complex(current_mag, -120 + current_angle)
                    total_in += polar_to_complex(current_mag, -120 + 180 + current_angle)
                elif 'C' in phases:
                    total_ic += polar_to_complex(current_mag, 120 + current_angle)
                    total_in += polar_to_complex(current_mag, 120 + 180 + current_angle)
            elif num_phases_selected == 2 and "N" not in phases:
                if 'A' in phases and 'B' in phases:
                    total_ia += polar_to_complex(current_mag, 30 + current_angle)
                    total_ib += polar_to_complex(current_mag, 30 + 180 + current_angle)
                elif 'B' in phases and 'C' in phases:
                    total_ib += polar_to_complex(current_mag, -90 + current_angle)
                    total_ic += polar_to_complex(current_mag, -90 + 180 + current_angle)
                elif 'C' in phases and 'A' in phases:
                    total_ic += polar_to_complex(current_mag, 150 + current_angle)
                    total_ia += polar_to_complex(current_mag, 150 + 180 + current_angle)
            elif num_phases_selected == 3 and "N" not in phases:
                total_ia += polar_to_complex(current_mag, 0 + current_angle)
                total_ib += polar_to_complex(current_mag, -120 + current_angle)
                total_ic += polar_to_complex(current_mag, 120 + current_angle)
            elif num_phases_selected == 1 and "N" not in phases:
                if 'A' in phases:
                    total_ia += polar_to_complex(current_mag, 0 + current_angle)
                    total_in += polar_to_complex(current_mag, 180 + current_angle)
                elif 'B' in phases:
                    total_ib += polar_to_complex(current_mag, -120 + current_angle)
                    total_in += polar_to_complex(current_mag, -120 + 180 + current_angle)
                elif 'C' in phases:
                    total_ic += polar_to_complex(current_mag, 120 + current_angle)
                    total_in += polar_to_complex(current_mag, 120 + 180 + current_angle)

        self.update_loads_display()

        total_in_resultant = -(total_ia + total_ib + total_ic)

        total_s = math.sqrt(total_p**2 + total_q**2)
        total_pf = total_p / total_s if total_s != 0 else 0.0

        results = {
            'Ia': complex_to_polar(total_ia),
            'Ib': complex_to_polar(total_ib),
            'Ic': complex_to_polar(total_ic),
            'In': complex_to_polar(total_in_resultant),
            'P_total': total_p,
            'Q_total': total_q,
            'S_total': total_s,
            'PF_total': total_pf
        }

        self.display_results(results)
        self.plot_phasors(total_ia, total_ib, total_ic, total_in_resultant)

    def display_results(self, res):
        self.result_text.delete('1.0', tk.END)
        lines = []
        
        lines.append("--- Balanço Total de Potências ---")
        lines.append(f"Potência Ativa Total (P): {res['P_total']:.2f} W")
        lines.append(f"Potência Reativa Total (Q): {res['Q_total']:.2f} VAR")
        lines.append(f"Potência Aparente Total (S): {res['S_total']:.2f} VA")
        lines.append(f"Fator de Potência Total (FP): {res['PF_total'] if res['PF_total'] != -1 else 1:.3f}")
        lines.append("----------------------------------")
        lines.append("--- Correntes Fasoriais Totais ---")

        for k in ['Ia','Ib','Ic','In']:
            mag, ang = res[k]
            lines.append(f'{k}: {mag:.4f} A ∠ {ang:.2f}°')
        
        self.result_text.insert(tk.END, '\n'.join(lines))

    def plot_phasors(self, Ia, Ib, Ic, In):
        self.ax.clear()
        # Validação de valores não nulos
        # Caso um dos valores for nulo, ele será ignorado na plotagem dos fasores 
        phasors = []

        for k in [('IA', Ia), ('IB', Ib), ('IC', Ic), ('IN', In)]:
            mag, ang = complex_to_polar(k[1])

            if mag > 1e-4:
                phasors.append(k)
                # Lista de tuplas (label, valor complexo)

        max_mag = max(abs(z) for _,z in phasors) if phasors else 1.0
        lim = max(2e-3, max_mag*1.4)
        self.ax.set_xlim(-lim, lim)
        self.ax.set_ylim(-lim, lim)
        self.ax.axhline(0, linewidth=0.6)
        self.ax.axvline(0, linewidth=0.6)
        for label, z in phasors:
            self.ax.arrow(0, 0, z.real, z.imag, head_width=0.06*lim, head_length=0.08*lim, length_includes_head=True)
            mag, ang = complex_to_polar(z)
            self.ax.text(z.real*1.05, z.imag*1.05, f'{label}\n{mag:.2f}A\n{ang:.0f}°')

        self.ax.set_aspect('equal')
        self.ax.set_title('Diagrama Fasorial das Correntes Totais')
        self.ax.grid(True, linestyle='--', linewidth=0.5)
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = PhasorCalcApp(root)
    root.mainloop()