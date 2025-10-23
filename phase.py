import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

class LoadCalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title('Calculadora de Cargas Elétricas')
        self.loads = [] # List to store load data
        self.create_ui()

    def create_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky='nsew')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Input Frame for new loads
        input_frame = ttk.Labelframe(main_frame, text='Adicionar Nova Carga')
        input_frame.grid(row=0, column=0, sticky='ew', pady=8, padx=5)

        ttk.Label(input_frame, text='Nome da Carga:').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.load_name_entry = ttk.Entry(input_frame, width=20)
        self.load_name_entry.grid(row=0, column=1, columnspan=4, sticky='ew', padx=5, pady=2)

        ttk.Label(input_frame, text='Potência (W):').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.power_entry = ttk.Entry(input_frame, width=10)
        self.power_entry.grid(row=1, column=1, columnspan=4, sticky='ew', padx=5, pady=2)

        ttk.Label(input_frame, text='Tensão de Linha (V):').grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.line_voltage_entry = ttk.Entry(input_frame, width=10)
        self.line_voltage_entry.grid(row=2, column=1, columnspan=4, sticky='ew', padx=5, pady=2)
        self.line_voltage_entry.insert(0, '380') # Default value

        ttk.Label(input_frame, text='Fase(s):').grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.phase_r_var = tk.BooleanVar()
        self.phase_s_var = tk.BooleanVar()
        self.phase_t_var = tk.BooleanVar()
        self.neutral_var = tk.BooleanVar()

        ttk.Checkbutton(input_frame, text='R', variable=self.phase_r_var).grid(row=3, column=1, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(input_frame, text='S', variable=self.phase_s_var).grid(row=3, column=2, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(input_frame, text='T', variable=self.phase_t_var).grid(row=3, column=3, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(input_frame, text='Neutro', variable=self.neutral_var).grid(row=3, column=4, sticky='w', padx=5, pady=2)

        add_load_btn = ttk.Button(input_frame, text='Adicionar Carga', command=self.add_load)
        add_load_btn.grid(row=4, column=0, columnspan=5, pady=10)

        # Loads List Frame
        loads_list_frame = ttk.Labelframe(main_frame, text='Cargas Adicionadas')
        loads_list_frame.grid(row=1, column=0, sticky='nsew', pady=8, padx=5)
        main_frame.rowconfigure(1, weight=1)

        self.loads_tree = ttk.Treeview(loads_list_frame, columns=('Nome', 'Potência', 'Fases', 'Corrente'), show='headings')
        self.loads_tree.heading('Nome', text='Nome')
        self.loads_tree.heading('Potência', text='Potência (W)')
        self.loads_tree.heading('Fases', text='Fases')
        self.loads_tree.heading('Corrente', text='Corrente (A)')
        self.loads_tree.column('Nome', width=100)
        self.loads_tree.column('Potência', width=80)
        self.loads_tree.column('Fases', width=80)
        self.loads_tree.column('Corrente', width=80)
        self.loads_tree.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Buttons for Modify and Delete
        btn_frame = ttk.Frame(loads_list_frame)
        btn_frame.grid(row=1, column=0, sticky='ew', pady=5)

        modify_load_btn = ttk.Button(btn_frame, text='Modificar Carga', command=self.modify_load)
        modify_load_btn.pack(side='left', padx=5)

        delete_load_btn = ttk.Button(btn_frame, text='Deletar Carga', command=self.delete_load)
        delete_load_btn.pack(side='left', padx=5)

        loads_list_frame.columnconfigure(0, weight=1)
        loads_list_frame.rowconfigure(0, weight=1)        # Results and Plot Frame
        results_plot_frame = ttk.Labelframe(main_frame, text='Resultados e Diagrama Fasorial')
        results_plot_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', pady=8, padx=5)
        main_frame.columnconfigure(1, weight=1)

        self.result_text = tk.Text(results_plot_frame, height=10, width=40)
        self.result_text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.fig = Figure(figsize=(5,4), tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=results_plot_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        results_plot_frame.columnconfigure(0, weight=1)
        results_plot_frame.rowconfigure(1, weight=1)

    def add_load(self):
        name = self.load_name_entry.get().strip()
        power_str = self.power_entry.get().strip()
        phases = []
        if self.phase_r_var.get():
            phases.append('R')
        if self.phase_s_var.get():
            phases.append('S')
        if self.phase_t_var.get():
            phases.append('T')
        if self.neutral_var.get():
            phases.append('N')

        if not name or not power_str or not phases:
            messagebox.showerror('Erro', 'Por favor, preencha todos os campos e selecione pelo menos uma fase.')
            return

        try:
            power = float(power_str)
            if power <= 0:
                messagebox.showerror("Erro", "A potência deve ser um valor positivo.")
                return
            line_voltage = float(self.line_voltage_entry.get().strip())
            if line_voltage <= 0:
                messagebox.showerror("Erro", "A tensão de linha deve ser um valor positivo.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Potência ou Tensão de Linha inválida. Por favor, insira um número.")
            return

        current = 0.0
        # Assuming a fixed phase voltage for single-phase loads (e.g., 220V for 380V line-to-line system)
        # This assumes a Y-connected system where V_phase = V_line / sqrt(3)
        voltage_phase = line_voltage / math.sqrt(3)

        num_phases_selected = len([p for p in phases if p in ["R", "S", "T"]])

        if num_phases_selected == 1 and "N" in phases:
            # Single-phase load (e.g., R-N)
            current = power / voltage_phase
        elif num_phases_selected == 2 and "N" not in phases:
            # Two-phase load (e.g., R-S for an inverter)
            # For a load connected between two phases, the voltage across it is the line-to-line voltage.
            # Assuming purely resistive load (PF=1) for simplicity: P = V_line * I_line
            current = power / line_voltage
        elif num_phases_selected == 3 and "N" not in phases:
            # Three-phase load (e.g., R-S-T)
            # P = sqrt(3) * V_line * I_line * PF. Assuming PF=1 for simplicity.
            current = power / (math.sqrt(3) * line_voltage)
        elif num_phases_selected == 1 and "N" not in phases:
            # If only one phase selected without Neutral, assume it's a single-phase load to Neutral
            messagebox.showwarning("Aviso", "Apenas uma fase selecionada sem Neutro. Assumindo conexão fase-neutro.")
            current = power / voltage_phase
        else:
            messagebox.showerror("Erro", "Combinação de fases não suportada para cálculo de corrente simplificado. Por favor, selecione uma fase e Neutro, duas fases (sem Neutro), ou R, S e T (sem Neutro) para trifásico.")
            return

        load_data = {"name": name, "power": power, "phases": phases, "current": current, "line_voltage": line_voltage}
        self.loads.append(load_data)
        self.update_loads_display()
        self.calculate_and_plot()

        # Clear input fields
        self.load_name_entry.delete(0, tk.END)
        self.power_entry.delete(0, tk.END)
        # Keep line_voltage_entry value
        self.phase_r_var.set(False)
        self.phase_s_var.set(False)
        self.phase_t_var.set(False)
        self.neutral_var.set(False)

    def delete_load(self):
        selected_item = self.loads_tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Por favor, selecione uma carga para deletar.")
            return

        # Get the index of the selected item in the loads_tree
        item_index = self.loads_tree.index(selected_item[0])

        # Remove the load from the list
        if 0 <= item_index < len(self.loads):
            del self.loads[item_index]
            self.update_loads_display()
            self.calculate_and_plot()

    def modify_load(self):
        selected_item = self.loads_tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Por favor, selecione uma carga para modificar.")
            return

        item_index = self.loads_tree.index(selected_item[0])
        if 0 <= item_index < len(self.loads):
            load_to_modify = self.loads[item_index]

            # Populate input fields with selected load data
            self.load_name_entry.delete(0, tk.END)
            self.load_name_entry.insert(0, load_to_modify["name"])

            self.power_entry.delete(0, tk.END)
            self.power_entry.insert(0, str(load_to_modify["power"]))

            # Set phase checkboxes
            self.phase_r_var.set("R" in load_to_modify["phases"])
            self.phase_s_var.set("S" in load_to_modify["phases"])
            self.phase_t_var.set("T" in load_to_modify["phases"])
            self.neutral_var.set("N" in load_to_modify["phases"])

            # Remove the load from the list, it will be re-added/modified by add_load
            del self.loads[item_index]
            self.update_loads_display()
            self.calculate_and_plot()

    def update_loads_display(self):
        for item in self.loads_tree.get_children():
            self.loads_tree.delete(item)
        for load in self.loads:
            phases_str = ', '.join(load['phases'])
            self.loads_tree.insert('', 'end', values=(load['name'], load['power'], phases_str, f"{load['current']:.2f}"))

    def calculate_and_plot(self):
        # Initialize total currents for each phase and neutral
        total_ia = 0 + 0j
        total_ib = 0 + 0j
        total_ic = 0 + 0j
        total_in = 0 + 0j

        # Assuming a reference voltage angle of 0 for phase R, -120 for S, +120 for T
        # And assuming purely resistive loads (current in phase with voltage)
        # This is a simplification. For inductive/capacitive loads, power factor would be needed.

        for load in self.loads:
            current_mag = load['current']
            phases = load['phases']

            # Distribute current based on connected phases
            # This is a highly simplified model. A real power system calculation is much more complex.
            # For single-phase loads (e.g., R-N), current flows in R and N.
            # For three-phase loads, current is distributed across R, S, T.

            if len(phases) == 2 and 'N' in phases:
                # Single-phase load. Current flows in the connected phase and neutral.
                if 'R' in phases:
                    total_ia += polar_to_complex(current_mag, 0) # Assuming R phase angle is 0
                    total_in += polar_to_complex(current_mag, 180) # Neutral current is 180 deg out of phase for single phase
                elif 'S' in phases:
                    total_ib += polar_to_complex(current_mag, -120) # Assuming S phase angle is -120
                    total_in += polar_to_complex(current_mag, -120 + 180) # Neutral current is 180 deg out of phase for single phase
                elif 'T' in phases:
                    total_ic += polar_to_complex(current_mag, 120) # Assuming T phase angle is 120
                    total_in += polar_to_complex(current_mag, 120 + 180) # Neutral current is 180 deg out of phase for single phase
            elif len(phases) == 2 and 'N' not in phases:
                # Two-phase load (e.g., R-S). Current flows between the two phases.
                # The current calculated is the line current. For simplicity, assuming current flows from one phase to another.
                # The angle of the current will be aligned with the voltage difference between the two phases.
                # V_RS = V_R - V_S. Angle of V_RS is 30 degrees (V_R at 0, V_S at -120, V_T at 120)
                # V_ST = V_S - V_T. Angle of V_ST is -90 degrees
                # V_TR = V_T - V_R. Angle of V_TR is 150 degrees
                # Assuming purely resistive load, current is in phase with voltage.
                if 'R' in phases and 'S' in phases:
                    total_ia += polar_to_complex(current_mag, 30) # Current in R
                    total_ib += polar_to_complex(current_mag, 30 + 180) # Current in S (180 out of phase with R)
                elif 'S' in phases and 'T' in phases:
                    total_ib += polar_to_complex(current_mag, -90) # Current in S
                    total_ic += polar_to_complex(current_mag, -90 + 180) # Current in T
                elif 'T' in phases and 'R' in phases:
                    total_ic += polar_to_complex(current_mag, 150) # Current in T
                    total_ia += polar_to_complex(current_mag, 150 + 180) # Current in R
            elif len(phases) == 3 and 'R' in phases and 'S' in phases and 'T' in phases:
                # Three-phase load. Current is distributed across phases.
                # Assuming balanced three-phase load, current in each phase is current_mag, with respective phase angles.
                total_ia += polar_to_complex(current_mag, 0)
                total_ib += polar_to_complex(current_mag, -120)
                total_ic += polar_to_complex(current_mag, 120)
            elif len(phases) == 1 and ('R' in phases or 'S' in phases or 'T' in phases):
                # Simplified: assume single phase to neutral if only one phase is selected without explicit neutral
                if 'R' in phases:
                    total_ia += polar_to_complex(current_mag, 0)
                    total_in += polar_to_complex(current_mag, 180)
                elif 'S' in phases:
                    total_ib += polar_to_complex(current_mag, -120)
                    total_in += polar_to_complex(current_mag, -120 + 180)
                elif 'T' in phases:
                    total_ic += polar_to_complex(current_mag, 120)
                    total_in += polar_to_complex(current_mag, 120 + 180)

        # Calculate total neutral current based on sum of phase currents (Kirchhoff's Current Law)
        # In = -(Ia + Ib + Ic) is for a 3-phase system where In is the resultant neutral current.
        # For single-phase loads, the neutral current from that load is already accounted for.
        # So, total_in should be the sum of all individual neutral currents from single-phase loads.
        # If we are calculating the *resultant* neutral current for the entire system, it's the sum of all phase currents.
        # Let's use the sum of phase currents for the overall neutral current for the phasor diagram.
        total_in_resultant = -(total_ia + total_ib + total_ic)

        results = {
            'Ia': complex_to_polar(total_ia),
            'Ib': complex_to_polar(total_ib),
            'Ic': complex_to_polar(total_ic),
            'In': complex_to_polar(total_in_resultant) # Use the resultant neutral current for display/plot
        }

        self.display_results(results)
        self.plot_phasors(total_ia, total_ib, total_ic, total_in_resultant)

    def display_results(self, res):
        self.result_text.delete('1.0', tk.END)
        lines = []
        for k in ['Ia','Ib','Ic','In']:
            mag, ang = res[k]
            lines.append(f'{k}: {mag:.4f} A ∠ {ang:.2f}°')
        self.result_text.insert(tk.END, '\n'.join(lines))

    def plot_phasors(self, Ia, Ib, Ic, In):
        self.ax.clear()
        phasors = [('IA', Ia), ('IB', Ib), ('IC', Ic), ('IN', In)]
        max_mag = max(abs(z) for _,z in phasors)
        lim = max(1.0, max_mag*1.4)
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
    app = LoadCalculatorApp(root)
    root.mainloop()
