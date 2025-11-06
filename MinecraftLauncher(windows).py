import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import zipfile
import urllib.request
import urllib.parse
import platform
import threading
import hashlib
import re
import shutil
from pathlib import Path
from datetime import datetime

class JavaManager:
    """Manages Java installations"""
    def __init__(self):
        self.java_installations = []
        self.detect_java()
    
    def detect_java(self):
        """Detect Java installations on the system"""
        self.java_installations = []
        
        # Check system PATH
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = self.parse_java_version(result.stderr)
                self.java_installations.append({
                    'path': 'java',
                    'version': version,
                    'name': f'System Java {version}'
                })
        except:
            pass
        
        # Common Java installation locations
        if platform.system() == 'Windows':
            self.scan_windows_java()
        elif platform.system() == 'Darwin':
            self.scan_mac_java()
        else:
            self.scan_linux_java()
        
        return self.java_installations
    
    def scan_windows_java(self):
        """Scan for Java on Windows"""
        locations = [
            r'C:\Program Files\Java',
            r'C:\Program Files (x86)\Java',
            r'C:\Program Files\Eclipse Adoptium',
            r'C:\Program Files\AdoptOpenJDK',
            r'C:\Program Files\Temurin',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
        ]
        
        for location in locations:
            if os.path.exists(location):
                for item in os.listdir(location):
                    java_exe = os.path.join(location, item, 'bin', 'java.exe')
                    if os.path.exists(java_exe):
                        version = self.get_java_version(java_exe)
                        if version:
                            self.java_installations.append({
                                'path': java_exe,
                                'version': version,
                                'name': f'{item} ({version})'
                            })
    
    def scan_mac_java(self):
        """Scan for Java on macOS"""
        locations = [
            '/Library/Java/JavaVirtualMachines',
            os.path.expanduser('~/Library/Java/JavaVirtualMachines'),
        ]
        
        for location in locations:
            if os.path.exists(location):
                for item in os.listdir(location):
                    java_exe = os.path.join(location, item, 'Contents', 'Home', 'bin', 'java')
                    if os.path.exists(java_exe):
                        version = self.get_java_version(java_exe)
                        if version:
                            self.java_installations.append({
                                'path': java_exe,
                                'version': version,
                                'name': f'{item} ({version})'
                            })
    
    def scan_linux_java(self):
        """Scan for Java on Linux"""
        locations = [
            '/usr/lib/jvm',
            '/usr/java',
            os.path.expanduser('~/.jdks'),
        ]
        
        for location in locations:
            if os.path.exists(location):
                for item in os.listdir(location):
                    java_exe = os.path.join(location, item, 'bin', 'java')
                    if os.path.exists(java_exe):
                        version = self.get_java_version(java_exe)
                        if version:
                            self.java_installations.append({
                                'path': java_exe,
                                'version': version,
                                'name': f'{item} ({version})'
                            })
    
    def get_java_version(self, java_path):
        """Get Java version from executable"""
        try:
            result = subprocess.run([java_path, '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return self.parse_java_version(result.stderr)
        except:
            pass
        return None
    
    def parse_java_version(self, version_string):
        """Parse Java version from output"""
        match = re.search(r'version "([^"]+)"', version_string)
        if match:
            version = match.group(1)
            # Extract major version
            if version.startswith('1.'):
                major = version.split('.')[1]
            else:
                major = version.split('.')[0]
            return f"Java {major}"
        return "Unknown"


class LegacyMinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Launcher - PrismLauncher Style")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Launcher directories
        self.launcher_dir = os.path.join(os.path.expanduser("~"), ".minecraft_legacy")
        self.instances_dir = os.path.join(self.launcher_dir, "instances")
        self.versions_dir = os.path.join(self.launcher_dir, "versions")
        self.libraries_dir = os.path.join(self.launcher_dir, "libraries")
        self.assets_dir = os.path.join(self.launcher_dir, "assets")
        self.profiles_file = os.path.join(self.launcher_dir, "profiles.json")
        self.instances_file = os.path.join(self.launcher_dir, "instances.json")
        
        # Create directories
        os.makedirs(self.instances_dir, exist_ok=True)
        os.makedirs(self.versions_dir, exist_ok=True)
        os.makedirs(self.libraries_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Load profiles and instances
        self.profiles = self.load_profiles()
        self.instances = self.load_instances()
        self.current_instance = None
        
        # Minecraft API URLs
        self.version_manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
        self.version_list = []
        self.version_data = {}
        
        # Java manager
        self.java_manager = JavaManager()
        
        # Game process
        self.game_process = None
        
        self.setup_ui()
        self.load_versions()
        
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel - Instance list
        left_panel = tk.Frame(main_container, width=300)
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Right panel - Tabs for console and settings
        right_panel = tk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Setup left panel
        self.setup_instances_panel(left_panel)
        
        # Setup right panel with tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill="both", expand=True)
        
        # Console tab
        console_frame = ttk.Frame(self.notebook)
        self.notebook.add(console_frame, text="Console")
        self.setup_console_tab(console_frame)
        
        # Settings tab
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        self.setup_settings_tab(settings_frame)
    
    def setup_instances_panel(self, parent):
        # Title
        title_label = tk.Label(parent, text="Instances", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Instance list frame
        list_frame = tk.Frame(parent)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox for instances
        self.instance_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                           font=("Arial", 10))
        self.instance_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.instance_listbox.yview)
        
        self.instance_listbox.bind('<Double-Button-1>', lambda e: self.launch_instance())
        
        # Buttons frame
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Button(btn_frame, text="Launch", command=self.launch_instance,
                 font=("Arial", 11, "bold"), bg="#4CAF50", fg="white",
                 height=2).pack(fill="x", pady=2)
        
        tk.Button(btn_frame, text="New Instance", command=self.new_instance,
                 font=("Arial", 10), bg="#2196F3", fg="white").pack(fill="x", pady=2)
        
        tk.Button(btn_frame, text="Edit", command=self.edit_instance,
                 font=("Arial", 10)).pack(fill="x", pady=2)
        
        tk.Button(btn_frame, text="Open Folder", command=self.open_instance_folder,
                 font=("Arial", 10)).pack(fill="x", pady=2)
        
        tk.Button(btn_frame, text="Delete", command=self.delete_instance,
                 font=("Arial", 10), bg="#f44336", fg="white").pack(fill="x", pady=2)
        
        # Status at bottom
        self.status_label = tk.Label(parent, text="Ready", 
                                     font=("Arial", 8), fg="gray")
        self.status_label.pack(pady=5)
        
        self.progress = ttk.Progressbar(parent, length=280, mode='determinate')
        self.progress.pack(pady=5, padx=10)
        self.progress['value'] = 0
        
        # Refresh instance list
        self.refresh_instance_list()
    
    def setup_console_tab(self, parent):
        # Console output
        console_label = tk.Label(parent, text="Game Console Output", 
                                font=("Arial", 12, "bold"))
        console_label.pack(pady=10)
        
        # Console text area
        console_frame = tk.Frame(parent)
        console_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.console_text = scrolledtext.ScrolledText(console_frame, 
                                                      wrap=tk.WORD,
                                                      font=("Consolas", 9),
                                                      bg="black", fg="white")
        self.console_text.pack(fill="both", expand=True)
        
        # Console buttons
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=10)
        
        clear_btn = tk.Button(button_frame, text="Clear Console", 
                             command=self.clear_console)
        clear_btn.pack(side="left", padx=5)
        
        copy_btn = tk.Button(button_frame, text="Copy to Clipboard", 
                            command=self.copy_console)
        copy_btn.pack(side="left", padx=5)
        
        self.log_to_console("Launcher started")
        self.log_to_console(f"Launcher directory: {self.launcher_dir}")
    
    def setup_settings_tab(self, parent):
        settings_label = tk.Label(parent, text="Launcher Settings", 
                                 font=("Arial", 14, "bold"))
        settings_label.pack(pady=15)
        
        # Java installations
        java_frame = tk.LabelFrame(parent, text="Java Installations", 
                                  font=("Arial", 10, "bold"), padx=15, pady=10)
        java_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Java listbox
        java_list_frame = tk.Frame(java_frame)
        java_list_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(java_list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.java_listbox = tk.Listbox(java_list_frame, yscrollcommand=scrollbar.set,
                                       font=("Consolas", 9))
        self.java_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.java_listbox.yview)
        
        self.refresh_java_list()
        
        # Java buttons
        java_btn_frame = tk.Frame(java_frame)
        java_btn_frame.pack(pady=10)
        
        detect_btn = tk.Button(java_btn_frame, text="Auto-Detect Java", 
                              command=self.detect_java)
        detect_btn.pack(side="left", padx=5)
        
        add_btn = tk.Button(java_btn_frame, text="Add Java Manually", 
                           command=self.add_java_manually)
        add_btn.pack(side="left", padx=5)
        
        # Launcher info
        info_frame = tk.LabelFrame(parent, text="Launcher Information", 
                                  font=("Arial", 10, "bold"), padx=15, pady=10)
        info_frame.pack(padx=20, pady=10, fill="x")
        
        info_text = f"""Launcher Directory: {self.launcher_dir}
Versions: {self.versions_dir}
Libraries: {self.libraries_dir}
Assets: {self.assets_dir}

Java Installations Found: {len(self.java_manager.java_installations)}"""
        
        tk.Label(info_frame, text=info_text, justify="left", font=("Consolas", 9)).pack()
    
    def load_profiles(self):
        """Load profiles from JSON file"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        # Default profile
        return {
            "Player": {
                "username": "Player",
                "last_version": None,
                "memory": "2048",
                "min_memory": "512"
            }
        }
    
    def save_profiles(self):
        """Save profiles to JSON file"""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            self.log_to_console(f"Failed to save profiles: {e}")
    
    def update_profile_list(self):
        """Update the profile combobox"""
        profile_names = list(self.profiles.keys())
        self.profile_combo['values'] = profile_names
        if profile_names:
            if self.profile_var.get() not in profile_names:
                self.profile_combo.current(0)
                self.on_profile_selected(None)
        else:
            self.profile_var.set("")
    
    def on_profile_selected(self, event):
        """Handle profile selection"""
        profile_name = self.profile_var.get()
        if profile_name and profile_name in self.profiles:
            profile = self.profiles[profile_name]
            self.username_var.set(profile.get('username', profile_name))
            self.memory_var.set(profile.get('memory', '2048'))
            self.min_memory_var.set(profile.get('min_memory', '512'))
            if profile.get('last_version') and profile['last_version'] in self.version_list:
                self.version_var.set(profile['last_version'])
            self.log_to_console(f"Loaded profile: {profile_name}")
    
    def new_profile(self):
        """Create a new profile"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Profile")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Profile Name:", font=("Arial", 10)).pack(pady=10)
        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        tk.Label(dialog, text="Username:", font=("Arial", 10)).pack(pady=10)
        username_var = tk.StringVar(value="Player")
        username_entry = tk.Entry(dialog, textvariable=username_var, width=30)
        username_entry.pack(pady=5)
        
        def save():
            profile_name = name_var.get().strip()
            username = username_var.get().strip()
            
            if not profile_name:
                messagebox.showerror("Error", "Profile name cannot be empty")
                return
            
            if profile_name in self.profiles:
                messagebox.showerror("Error", "Profile already exists")
                return
            
            if not username:
                username = profile_name
            
            self.profiles[profile_name] = {
                "username": username,
                "last_version": None,
                "memory": "2048",
                "min_memory": "512"
            }
            self.save_profiles()
            self.update_profile_list()
            self.profile_var.set(profile_name)
            self.on_profile_selected(None)
            self.log_to_console(f"Created profile: {profile_name}")
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Create", command=save, width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10).pack(side="left", padx=5)
        
        dialog.bind('<Return>', lambda e: save())
    
    def edit_profile(self):
        """Edit the selected profile"""
        profile_name = self.profile_var.get()
        if not profile_name or profile_name not in self.profiles:
            messagebox.showerror("Error", "Please select a profile to edit")
            return
        
        profile = self.profiles[profile_name]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Profile: {profile_name}")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Username:", font=("Arial", 10)).pack(pady=10)
        username_var = tk.StringVar(value=profile.get('username', profile_name))
        username_entry = tk.Entry(dialog, textvariable=username_var, width=30)
        username_entry.pack(pady=5)
        username_entry.focus()
        
        def save():
            username = username_var.get().strip()
            
            if not username:
                messagebox.showerror("Error", "Username cannot be empty")
                return
            
            self.profiles[profile_name]['username'] = username
            self.save_profiles()
            self.username_var.set(username)
            self.log_to_console(f"Updated profile: {profile_name}")
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save", command=save, width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10).pack(side="left", padx=5)
        
        dialog.bind('<Return>', lambda e: save())
    
    def delete_profile(self):
        """Delete the selected profile"""
        profile_name = self.profile_var.get()
        if not profile_name or profile_name not in self.profiles:
            messagebox.showerror("Error", "Please select a profile to delete")
            return
        
        if len(self.profiles) == 1:
            messagebox.showerror("Error", "Cannot delete the last profile")
            return
        
        result = messagebox.askyesno("Confirm Delete", 
            f"Are you sure you want to delete profile '{profile_name}'?")
        
        if result:
            del self.profiles[profile_name]
            self.save_profiles()
            self.update_profile_list()
            self.log_to_console(f"Deleted profile: {profile_name}")
    
    def load_instances(self):
        """Load instances from JSON file"""
        if os.path.exists(self.instances_file):
            try:
                with open(self.instances_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_instances(self):
        """Save instances to JSON file"""
        try:
            with open(self.instances_file, 'w') as f:
                json.dump(self.instances, f, indent=2)
        except Exception as e:
            self.log_to_console(f"Failed to save instances: {e}")
    
    def refresh_instance_list(self):
        """Refresh the instance listbox"""
        self.instance_listbox.delete(0, tk.END)
        for name, instance in self.instances.items():
            version = instance.get('version', 'Unknown')
            self.instance_listbox.insert(tk.END, f"{name} ({version})")
    
    def new_instance(self):
        """Create a new instance"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Instance")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Instance Name:", font=("Arial", 10, "bold")).pack(pady=10)
        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        tk.Label(dialog, text="Minecraft Version:", font=("Arial", 10, "bold")).pack(pady=10)
        version_var = tk.StringVar()
        version_combo = ttk.Combobox(dialog, textvariable=version_var,
                                     state="readonly", width=37)
        version_combo['values'] = self.version_list if self.version_list else ["Loading..."]
        if self.version_list:
            version_combo.current(0)
        version_combo.pack(pady=5)
        
        tk.Label(dialog, text="Username:", font=("Arial", 10, "bold")).pack(pady=10)
        username_var = tk.StringVar(value="Player")
        username_entry = tk.Entry(dialog, textvariable=username_var, width=40)
        username_entry.pack(pady=5)
        
        tk.Label(dialog, text="Java Version:", font=("Arial", 10, "bold")).pack(pady=10)
        java_var = tk.StringVar()
        java_combo = ttk.Combobox(dialog, textvariable=java_var,
                                  state="readonly", width=37)
        java_list = [j['name'] for j in self.java_manager.java_installations]
        java_combo['values'] = java_list if java_list else ["No Java found"]
        if java_list:
            java_combo.current(0)
        java_combo.pack(pady=5)
        
        tk.Label(dialog, text="Memory (MB) - Max:", font=("Arial", 10, "bold")).pack(pady=5)
        memory_var = tk.StringVar(value="2048")
        memory_entry = tk.Entry(dialog, textvariable=memory_var, width=40)
        memory_entry.pack(pady=5)
        
        def create():
            instance_name = name_var.get().strip()
            version = version_var.get()
            username = username_var.get().strip()
            java_selection = java_var.get()
            memory = memory_var.get()
            
            if not instance_name:
                messagebox.showerror("Error", "Instance name cannot be empty")
                return
            
            if instance_name in self.instances:
                messagebox.showerror("Error", "Instance already exists")
                return
            
            if not version:
                messagebox.showerror("Error", "Please select a version")
                return
            
            if not username:
                username = "Player"
            
            # Create instance directory
            instance_dir = os.path.join(self.instances_dir, instance_name)
            os.makedirs(instance_dir, exist_ok=True)
            os.makedirs(os.path.join(instance_dir, "natives"), exist_ok=True)
            
            self.instances[instance_name] = {
                "version": version,
                "username": username,
                "java": java_selection,
                "path": instance_dir,
                "memory": memory,
                "min_memory": "512"
            }
            
            self.save_instances()
            self.refresh_instance_list()
            self.log_to_console(f"Created instance: {instance_name} (v{version})")
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Create", command=create, 
                 font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, 
                 font=("Arial", 10), width=12).pack(side="left", padx=5)
    
    def edit_instance(self):
        """Edit selected instance"""
        selection = self.instance_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an instance to edit")
            return
        
        instance_name = list(self.instances.keys())[selection[0]]
        instance = self.instances[instance_name]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Instance: {instance_name}")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Minecraft Version:", font=("Arial", 10, "bold")).pack(pady=10)
        version_var = tk.StringVar(value=instance.get('version', ''))
        version_combo = ttk.Combobox(dialog, textvariable=version_var,
                                     state="readonly", width=37)
        version_combo['values'] = self.version_list
        version_combo.pack(pady=5)
        
        tk.Label(dialog, text="Username:", font=("Arial", 10, "bold")).pack(pady=10)
        username_var = tk.StringVar(value=instance.get('username', 'Player'))
        username_entry = tk.Entry(dialog, textvariable=username_var, width=40)
        username_entry.pack(pady=5)
        
        tk.Label(dialog, text="Java Version:", font=("Arial", 10, "bold")).pack(pady=10)
        java_var = tk.StringVar(value=instance.get('java', ''))
        java_combo = ttk.Combobox(dialog, textvariable=java_var,
                                  state="readonly", width=37)
        java_list = [j['name'] for j in self.java_manager.java_installations]
        java_combo['values'] = java_list if java_list else ["No Java found"]
        java_combo.pack(pady=5)
        
        tk.Label(dialog, text="Max Memory (MB):", font=("Arial", 10, "bold")).pack(pady=10)
        memory_var = tk.StringVar(value=instance.get('memory', '2048'))
        memory_entry = tk.Entry(dialog, textvariable=memory_var, width=40)
        memory_entry.pack(pady=5)
        
        tk.Label(dialog, text="Min Memory (MB):", font=("Arial", 10, "bold")).pack(pady=10)
        min_memory_var = tk.StringVar(value=instance.get('min_memory', '512'))
        min_memory_entry = tk.Entry(dialog, textvariable=min_memory_var, width=40)
        min_memory_entry.pack(pady=5)
        
        # Instance folder button
        tk.Button(dialog, text="Open Instance Folder", 
                 command=lambda: self.open_folder_path(instance['path']),
                 font=("Arial", 9)).pack(pady=10)
        
        def save():
            self.instances[instance_name]['version'] = version_var.get()
            self.instances[instance_name]['username'] = username_var.get()
            self.instances[instance_name]['java'] = java_var.get()
            self.instances[instance_name]['memory'] = memory_var.get()
            self.instances[instance_name]['min_memory'] = min_memory_var.get()
            self.save_instances()
            self.refresh_instance_list()
            self.log_to_console(f"Updated instance: {instance_name}")
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save", command=save, 
                 font=("Arial", 10, "bold"), width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, 
                 font=("Arial", 10), width=12).pack(side="left", padx=5)
    
    def delete_instance(self):
        """Delete selected instance"""
        selection = self.instance_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an instance to delete")
            return
        
        instance_name = list(self.instances.keys())[selection[0]]
        
        result = messagebox.askyesno("Confirm Delete", 
            f"Are you sure you want to delete instance '{instance_name}'?\n\nThis will delete all game files!")
        
        if result:
            instance = self.instances[instance_name]
            # Delete instance directory
            if os.path.exists(instance['path']):
                try:
                    shutil.rmtree(instance['path'])
                except Exception as e:
                    self.log_to_console(f"Error deleting instance folder: {e}")
            
            del self.instances[instance_name]
            self.save_instances()
            self.refresh_instance_list()
            self.log_to_console(f"Deleted instance: {instance_name}")
    
    def open_instance_folder(self):
        """Open instance folder in file explorer"""
        selection = self.instance_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an instance")
            return
        
        instance_name = list(self.instances.keys())[selection[0]]
        instance = self.instances[instance_name]
        self.open_folder_path(instance['path'])
    
    def open_folder_path(self, path):
        """Open a folder path in file explorer"""
        if os.path.exists(path):
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', path])
            else:
                subprocess.run(['xdg-open', path])
        else:
            messagebox.showerror("Error", "Folder not found")
    
    def launch_instance(self):
        """Launch selected instance"""
        selection = self.instance_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an instance to launch")
            return
        
        instance_name = list(self.instances.keys())[selection[0]]
        instance = self.instances[instance_name]
        
        # Set current instance
        self.current_instance = instance
        
        # Switch to launch tab and trigger launch
        self.notebook.select(1)  # Launch tab
        
        # Set version
        version = instance.get('version')
        if version in self.version_list:
            self.version_var.set(version)
        
        # Set profile
        profile = instance.get('profile')
        if profile and profile in self.profiles:
            self.profile_var.set(profile)
            self.on_profile_selected(None)
        
        # Set memory
        self.memory_var.set(instance.get('memory', '2048'))
        self.min_memory_var.set(instance.get('min_memory', '512'))
        
        # Launch
        self.launch_game_for_instance(instance_name, instance)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.gamedir_var.get())
        if directory:
            self.gamedir_var.set(directory)
    
    def browse_java(self):
        """Browse for Java executable"""
        if platform.system() == 'Windows':
            filetypes = [("Java Executable", "java.exe"), ("All Files", "*.*")]
        else:
            filetypes = [("Java Executable", "java"), ("All Files", "*.*")]
        
        java_path = filedialog.askopenfilename(title="Select Java Executable",
                                               filetypes=filetypes)
        if java_path:
            version = self.java_manager.get_java_version(java_path)
            if version:
                name = f"Custom - {os.path.basename(os.path.dirname(os.path.dirname(java_path)))} ({version})"
                self.java_manager.java_installations.append({
                    'path': java_path,
                    'version': version,
                    'name': name
                })
                # Update combo
                java_list = [j['name'] for j in self.java_manager.java_installations]
                self.java_combo['values'] = java_list
                self.java_combo.set(name)
                self.refresh_java_list()
                self.log_to_console(f"Added Java: {name} at {java_path}")
            else:
                messagebox.showerror("Error", "Could not determine Java version")
    
    def detect_java(self):
        """Re-detect Java installations"""
        self.log_to_console("Detecting Java installations...")
        self.java_manager.detect_java()
        java_list = [j['name'] for j in self.java_manager.java_installations]
        self.java_combo['values'] = java_list if java_list else ["No Java found"]
        if java_list:
            self.java_combo.current(0)
        self.refresh_java_list()
        self.log_to_console(f"Found {len(java_list)} Java installations")
    
    def add_java_manually(self):
        """Add Java installation manually"""
        self.browse_java()
    
    def refresh_java_list(self):
        """Refresh Java listbox in settings"""
        self.java_listbox.delete(0, tk.END)
        for java in self.java_manager.java_installations:
            self.java_listbox.insert(tk.END, f"{java['name']}: {java['path']}")
    
    def log_to_console(self, message):
        """Log message to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Only log if console exists
        if hasattr(self, 'console_text'):
            self.console_text.insert(tk.END, formatted_message)
            self.console_text.see(tk.END)
            self.console_text.update()
    
    def clear_console(self):
        """Clear console output"""
        self.console_text.delete(1.0, tk.END)
    
    def copy_console(self):
        """Copy console to clipboard"""
        console_content = self.console_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(console_content)
        messagebox.showinfo("Copied", "Console output copied to clipboard")
    
    def filter_versions(self):
        """Filter versions based on checkboxes"""
        if not hasattr(self, 'all_versions'):
            return
        
        filtered = []
        for vid in self.all_versions:
            version_info = self.version_data.get(vid)
            if not version_info:
                continue
            
            vtype = version_info.get('type', '')
            if vtype == 'release' and self.show_release.get():
                filtered.append(vid)
            elif vtype == 'old_beta' and self.show_beta.get():
                filtered.append(vid)
            elif vtype == 'old_alpha' and self.show_alpha.get():
                filtered.append(vid)
        
        self.version_list = filtered
        self.version_combo['values'] = self.version_list
        if self.version_list:
            self.version_combo.current(0)
    
    def kill_game(self):
        """Kill the running game process"""
        if self.game_process and self.game_process.poll() is None:
            self.log_to_console("Killing game process...")
            self.game_process.terminate()
            try:
                self.game_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.game_process.kill()
            self.log_to_console("Game process killed")
            self.kill_btn.config(state="disabled")
            self.launch_btn.config(state="normal")
    
    def load_versions(self):
        """Load available versions from Mojang API"""
        def fetch():
            try:
                self.status_label.config(text="Loading versions from Mojang...", fg="blue")
                self.log_to_console("Fetching version manifest from Mojang...")
                self.root.update()
                
                with urllib.request.urlopen(self.version_manifest_url) as response:
                    manifest = json.loads(response.read().decode())
                
                # Filter versions from 1.9 down to alpha
                self.version_list = []
                self.version_data = {}
                
                for version in manifest['versions']:
                    vid = version['id']
                    vtype = version['type']
                    
                    # Include releases, old_beta, and old_alpha
                    if vtype in ['release', 'old_beta', 'old_alpha']:
                        # Filter to only include versions 1.9 and earlier
                        if self.should_include_version(vid):
                            self.version_list.append(vid)
                            self.version_data[vid] = version
                
                # Store all versions for filtering
                self.all_versions = self.version_list.copy()
                
                # Update combobox
                self.version_combo['values'] = self.version_list
                if self.version_list:
                    self.version_combo.current(0)
                
                self.status_label.config(text=f"Loaded {len(self.version_list)} versions", fg="green")
                self.log_to_console(f"Loaded {len(self.version_list)} versions successfully")
                
            except Exception as e:
                error_msg = f"Failed to load versions: {str(e)}"
                self.status_label.config(text=error_msg, fg="red")
                self.log_to_console(f"ERROR: {error_msg}")
                messagebox.showerror("Error", f"Could not fetch version list:\n{str(e)}")
        
        # Run in thread to avoid blocking UI
        threading.Thread(target=fetch, daemon=True).start()
    
    def should_include_version(self, version_id):
        """Check if version should be included (1.9 and earlier)"""
        # Alpha versions
        if version_id.startswith('a'):
            return True
        # Beta versions
        if version_id.startswith('b'):
            return True
        # Release versions - check if 1.9 or earlier
        if version_id.startswith('1.'):
            try:
                # Parse version number
                parts = version_id.split('.')
                major = int(parts[0])
                minor = int(parts[1].split('-')[0]) if len(parts) > 1 else 0
                
                # Include if version is 1.0-1.9
                if major == 1 and minor <= 9:
                    return True
            except:
                pass
        
        return False
    
    def download_file(self, url, dest_path, description="file"):
        """Download a file with progress tracking"""
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        try:
            self.log_to_console(f"Downloading {description}...")
            with urllib.request.urlopen(url) as response:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                downloaded = 0
                
                with open(dest_path, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        
                        downloaded += len(buffer)
                        f.write(buffer)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.progress['value'] = percent
                            self.root.update_idletasks()
            
            self.log_to_console(f"✓ Downloaded {description}")
            return True
        except Exception as e:
            self.log_to_console(f"✗ Error downloading {description}: {e}")
            return False
    
    def download_version(self, version_id):
        """Download version JSON and JAR"""
        try:
            version_info = self.version_data[version_id]
            version_url = version_info['url']
            
            # Download version JSON
            self.status_label.config(text=f"Downloading {version_id} metadata...", fg="blue")
            self.log_to_console(f"Fetching version metadata for {version_id}...")
            
            with urllib.request.urlopen(version_url) as response:
                version_json = json.loads(response.read().decode())
            
            # Save version JSON
            version_dir = os.path.join(self.versions_dir, version_id)
            os.makedirs(version_dir, exist_ok=True)
            
            json_path = os.path.join(version_dir, f"{version_id}.json")
            with open(json_path, 'w') as f:
                json.dump(version_json, f, indent=2)
            
            self.log_to_console(f"✓ Saved version metadata")
            
            # Download client JAR
            if 'downloads' in version_json and 'client' in version_json['downloads']:
                client_info = version_json['downloads']['client']
                jar_url = client_info['url']
                jar_path = os.path.join(version_dir, f"{version_id}.jar")
                
                if not os.path.exists(jar_path):
                    self.status_label.config(text=f"Downloading {version_id} client...", fg="blue")
                    self.download_file(jar_url, jar_path, f"{version_id} client JAR")
                else:
                    self.log_to_console(f"Client JAR already exists")
            else:
                # Very old versions might not have downloads section
                self.log_to_console(f"Warning: No download info for client JAR")
            
            # Download libraries and natives
            if 'libraries' in version_json:
                self.download_libraries_and_natives(version_json)
            
            self.progress['value'] = 100
            self.log_to_console(f"✓ Version {version_id} ready to launch")
            return True
            
        except Exception as e:
            error_msg = f"Failed to download {version_id}: {str(e)}"
            self.status_label.config(text=error_msg, fg="red")
            self.log_to_console(f"✗ ERROR: {error_msg}")
            messagebox.showerror("Download Error", error_msg)
            return False
    
    def download_libraries_and_natives(self, version_json):
        """Download all libraries and natives for a version"""
        total_libs = len(version_json['libraries'])
        self.status_label.config(text=f"Downloading libraries...", fg="blue")
        self.log_to_console(f"Processing {total_libs} libraries...")
        
        downloaded = 0
        skipped = 0
        
        for i, lib in enumerate(version_json['libraries']):
            # Check rules
            if 'rules' in lib:
                allowed = self.check_rules(lib['rules'])
                if not allowed:
                    skipped += 1
                    continue
            
            # Download main artifact
            if 'downloads' in lib and 'artifact' in lib['downloads']:
                artifact = lib['downloads']['artifact']
                lib_path = os.path.join(self.libraries_dir, artifact['path'])
                
                if not os.path.exists(lib_path):
                    lib_name = os.path.basename(artifact['path'])
                    if self.download_file(artifact['url'], lib_path, f"library {lib_name}"):
                        downloaded += 1
            elif 'name' in lib:
                # Try to construct path for very old libraries without downloads section
                lib_name = lib['name']
                lib_path = self.construct_library_path(lib_name)
                if lib_path and 'url' in lib:
                    base_url = lib['url']
                    lib_url = base_url + lib_path.replace('\\', '/')
                    full_lib_path = os.path.join(self.libraries_dir, lib_path)
                    if not os.path.exists(full_lib_path):
                        if self.download_file(lib_url, full_lib_path, f"library {os.path.basename(lib_path)}"):
                            downloaded += 1
            
            # Download natives for this library
            if 'natives' in lib:
                self.download_native_library(lib, downloaded)
            
            # Update progress
            progress = ((i + 1) / total_libs) * 100
            self.progress['value'] = progress
            self.root.update_idletasks()
        
        self.log_to_console(f"✓ Downloaded {downloaded} new libraries, skipped {skipped} incompatible")
    
    def download_native_library(self, lib, downloaded_count):
        """Download native library for current OS"""
        os_name = self.get_os_name()
        if os_name in lib['natives']:
            classifier = lib['natives'][os_name]
            # Replace variables in classifier
            arch = platform.architecture()[0][:2]  # "64" or "32"
            classifier = classifier.replace('${arch}', arch)
            
            if 'downloads' in lib and 'classifiers' in lib['downloads']:
                if classifier in lib['downloads']['classifiers']:
                    native_info = lib['downloads']['classifiers'][classifier]
                    native_path = os.path.join(self.libraries_dir, native_info['path'])
                    
                    if not os.path.exists(native_path):
                        native_name = os.path.basename(native_info['path'])
                        self.download_file(native_info['url'], native_path, f"native {native_name}")
                        return True
        return False
    
    def construct_library_path(self, lib_name):
        """Construct library path from Maven coordinates (for old versions)"""
        try:
            # Format: group:artifact:version
            parts = lib_name.split(':')
            if len(parts) >= 3:
                group = parts[0].replace('.', '/')
                artifact = parts[1]
                version = parts[2]
                filename = f"{artifact}-{version}.jar"
                return f"{group}/{artifact}/{version}/{filename}"
        except:
            pass
        return None
    
    def extract_natives(self, version_json):
        """Extract native libraries"""
        try:
            self.log_to_console("Extracting native libraries...")
            extracted_count = 0
            
            # Clear natives directory first
            if os.path.exists(self.natives_dir):
                for file in os.listdir(self.natives_dir):
                    file_path = os.path.join(self.natives_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        self.log_to_console(f"Warning: Could not delete {file}: {e}")
            
            os.makedirs(self.natives_dir, exist_ok=True)
            
            for lib in version_json.get('libraries', []):
                # Check rules for this library
                if 'rules' in lib:
                    allowed = self.check_rules(lib['rules'])
                    if not allowed:
                        continue
                
                if 'natives' in lib:
                    os_name = self.get_os_name()
                    if os_name in lib['natives']:
                        classifier = lib['natives'][os_name]
                        # Replace variables in classifier
                        arch = platform.architecture()[0][:2]  # "64" or "32"
                        classifier = classifier.replace('${arch}', arch)
                        
                        native_path = None
                        
                        # Try modern format first
                        if 'downloads' in lib and 'classifiers' in lib['downloads']:
                            if classifier in lib['downloads']['classifiers']:
                                native_info = lib['downloads']['classifiers'][classifier]
                                native_path = os.path.join(self.libraries_dir, native_info['path'])
                        
                        # Try legacy format if not found
                        if not native_path and 'name' in lib:
                            lib_path = self.construct_library_path(lib['name'])
                            if lib_path:
                                # Add classifier to filename
                                lib_path = lib_path.replace('.jar', f'-{classifier}.jar')
                                native_path = os.path.join(self.libraries_dir, lib_path)
                        
                        # Extract if exists
                        if native_path and os.path.exists(native_path):
                            try:
                                with zipfile.ZipFile(native_path, 'r') as zip_ref:
                                    # Get exclude patterns
                                    excludes = []
                                    if 'extract' in lib and 'exclude' in lib['extract']:
                                        excludes = lib['extract']['exclude']
                                    
                                    for member in zip_ref.namelist():
                                        # Check if should be excluded
                                        should_extract = True
                                        for exclude in excludes:
                                            if member.startswith(exclude):
                                                should_extract = False
                                                break
                                        
                                        if should_extract and not member.endswith('/'):
                                            # Extract file
                                            zip_ref.extract(member, self.natives_dir)
                                            extracted_count += 1
                                
                                self.log_to_console(f"  ✓ Extracted {os.path.basename(native_path)}")
                            except Exception as e:
                                self.log_to_console(f"  ✗ Failed to extract {os.path.basename(native_path)}: {e}")
                        elif native_path:
                            self.log_to_console(f"  ✗ Native not found: {os.path.basename(native_path)}")
            
            if extracted_count > 0:
                self.log_to_console(f"✓ Extracted {extracted_count} native files")
            else:
                self.log_to_console(f"Warning: No native files extracted")
                
        except Exception as e:
            self.log_to_console(f"✗ Error extracting natives: {e}")
            
    def launch_game(self):
        version = self.version_var.get()
        username = self.username_var.get()
        memory = self.memory_var.get()
        min_memory = self.min_memory_var.get()
        game_dir = self.gamedir_var.get()
        profile_name = self.profile_var.get()
        
        if not version or version == "Loading versions...":
            messagebox.showerror("Error", "Please select a version")
            return
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        # Save profile settings
        if profile_name and profile_name in self.profiles:
            self.profiles[profile_name]['last_version'] = version
            self.profiles[profile_name]['memory'] = memory
            self.profiles[profile_name]['min_memory'] = min_memory
            self.save_profiles()
        
        # Get selected Java
        java_selection = self.java_var.get()
        if not java_selection or java_selection == "No Java found":
            messagebox.showerror("Error", "No Java installation selected.\nPlease install Java or add it manually in Settings.")
            return
        
        # Find Java path
        java_path = None
        for java in self.java_manager.java_installations:
            if java['name'] == java_selection:
                java_path = java['path']
                break
        
        if not java_path:
            messagebox.showerror("Error", "Could not find selected Java installation")
            return
        
        try:
            memory_int = int(memory)
            min_memory_int = int(min_memory)
            if memory_int < 64 or min_memory_int < 64:
                messagebox.showerror("Error", "Memory must be at least 64 MB")
                return
            if min_memory_int > memory_int:
                messagebox.showerror("Error", "Minimum memory cannot be greater than maximum memory")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid memory value")
            return
        
        self.launch_btn.config(state="disabled")
        self.kill_btn.config(state="disabled")
        self.progress['value'] = 0
        
        # Switch to console tab
        self.notebook.select(1)
        
        def launch_thread():
            try:
                self.log_to_console("=" * 60)
                self.log_to_console(f"Launching Minecraft {version}")
                self.log_to_console(f"Username: {username}")
                self.log_to_console(f"Java: {java_path}")
                self.log_to_console(f"Memory: {min_memory}MB - {memory}MB")
                self.log_to_console("=" * 60)
                
                # Check if version is downloaded
                version_dir = os.path.join(self.versions_dir, version)
                json_path = os.path.join(version_dir, f"{version}.json")
                jar_path = os.path.join(version_dir, f"{version}.jar")
                
                if not os.path.exists(json_path) or not os.path.exists(jar_path):
                    self.status_label.config(text=f"Downloading {version}...", fg="blue")
                    self.log_to_console(f"Version {version} not found locally, downloading...")
                    if not self.download_version(version):
                        self.launch_btn.config(state="normal")
                        return
                else:
                    self.log_to_console(f"✓ Version {version} found locally")
                
                # Load version JSON
                with open(json_path, 'r') as f:
                    version_json = json.load(f)
                
                # Always extract natives to ensure they're up to date
                self.log_to_console("Extracting native libraries...")
                self.extract_natives(version_json)
                
                # Build classpath
                self.status_label.config(text="Building classpath...", fg="blue")
                self.log_to_console("Building classpath...")
                classpath = []
                
                # Add libraries
                if 'libraries' in version_json:
                    for lib in version_json['libraries']:
                        # Check rules
                        if 'rules' in lib:
                            allowed = self.check_rules(lib['rules'])
                            if not allowed:
                                continue
                        
                        # Skip natives from classpath
                        if 'natives' in lib:
                            continue
                        
                        lib_path = None
                        
                        # Try modern format
                        if 'downloads' in lib and 'artifact' in lib['downloads']:
                            artifact = lib['downloads']['artifact']
                            lib_path = os.path.join(self.libraries_dir, artifact['path'])
                        # Try legacy format
                        elif 'name' in lib:
                            constructed_path = self.construct_library_path(lib['name'])
                            if constructed_path:
                                lib_path = os.path.join(self.libraries_dir, constructed_path)
                        
                        if lib_path and os.path.exists(lib_path):
                            classpath.append(lib_path)
                        elif lib_path:
                            self.log_to_console(f"  Warning: Missing library {os.path.basename(lib_path)}")
                
                # Add client JAR
                classpath.append(jar_path)
                
                self.log_to_console(f"✓ Classpath built with {len(classpath)} entries")
                
                # Build classpath string
                cp_separator = ';' if platform.system() == 'Windows' else ':'
                classpath_str = cp_separator.join(classpath)
                
                # Get main class
                main_class = version_json.get('mainClass', 'net.minecraft.client.Minecraft')
                self.log_to_console(f"Main class: {main_class}")
                
                # Create game directory structure
                saves_dir = os.path.join(game_dir, "saves")
                resources_dir = os.path.join(game_dir, "resources")
                os.makedirs(saves_dir, exist_ok=True)
                os.makedirs(resources_dir, exist_ok=True)
                
                # Generate UUID for offline account
                import uuid
                player_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))
                
                # Build launch command
                launch_args = [
                    java_path,
                    f"-Xmx{memory}M",
                    f"-Xms{min_memory}M",
                    f"-Djava.library.path={self.natives_dir}",
                    "-cp", classpath_str,
                    main_class
                ]
                
                # Add game arguments
                if 'minecraftArguments' in version_json:
                    # Old format (pre-1.13)
                    game_args = version_json['minecraftArguments']
                    game_args = game_args.replace('${auth_player_name}', username)
                    game_args = game_args.replace('${version_name}', version)
                    game_args = game_args.replace('${game_directory}', game_dir)
                    game_args = game_args.replace('${assets_root}', self.assets_dir)
                    game_args = game_args.replace('${assets_index_name}', version_json.get('assets', 'legacy'))
                    game_args = game_args.replace('${auth_uuid}', player_uuid)
                    game_args = game_args.replace('${auth_access_token}', '0')
                    game_args = game_args.replace('${user_type}', 'legacy')
                    game_args = game_args.replace('${version_type}', version_json.get('type', 'release'))
                    game_args = game_args.replace('${user_properties}', '{}')
                    
                    launch_args.extend(game_args.split())
                elif 'arguments' in version_json and 'game' in version_json['arguments']:
                    # New format (1.13+)
                    for arg in version_json['arguments']['game']:
                        if isinstance(arg, str):
                            arg = arg.replace('${auth_player_name}', username)
                            arg = arg.replace('${version_name}', version)
                            arg = arg.replace('${game_directory}', game_dir)
                            arg = arg.replace('${assets_root}', self.assets_dir)
                            arg = arg.replace('${assets_index_name}', version_json.get('assets', 'legacy'))
                            arg = arg.replace('${auth_uuid}', player_uuid)
                            arg = arg.replace('${auth_access_token}', '0')
                            arg = arg.replace('${user_type}', 'legacy')
                            arg = arg.replace('${version_type}', version_json.get('type', 'release'))
                            launch_args.append(arg)
                else:
                    # Very old versions - just add username
                    launch_args.append(username)
                
                self.log_to_console("Launch command prepared")
                self.status_label.config(text=f"Starting {version}...", fg="green")
                self.progress['value'] = 100
                
                # Launch the game
                self.log_to_console("Starting game process...")
                self.log_to_console("-" * 60)
                
                if platform.system() == 'Windows':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    self.game_process = subprocess.Popen(launch_args, cwd=game_dir,
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.STDOUT,
                                              startupinfo=startupinfo,
                                              universal_newlines=True,
                                              bufsize=1)
                else:
                    self.game_process = subprocess.Popen(launch_args, cwd=game_dir,
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.STDOUT,
                                              universal_newlines=True,
                                              bufsize=1)
                
                # Enable kill button
                self.kill_btn.config(state="normal")
                
                # Read output in real-time
                for line in self.game_process.stdout:
                    self.log_to_console(line.rstrip())
                
                # Wait for process to complete
                return_code = self.game_process.wait()
                
                self.log_to_console("-" * 60)
                if return_code == 0:
                    self.log_to_console(f"✓ Game exited normally (code {return_code})")
                    self.status_label.config(text="Game closed normally", fg="green")
                else:
                    self.log_to_console(f"✗ Game exited with code {return_code}")
                    self.status_label.config(text=f"Game exited with error (code {return_code})", fg="red")
                
                self.launch_btn.config(state="normal")
                self.kill_btn.config(state="disabled")
                
            except Exception as e:
                error_msg = f"Failed to launch game: {str(e)}"
                self.log_to_console(f"✗ ERROR: {error_msg}")
                messagebox.showerror("Launch Error", error_msg)
                self.status_label.config(text="Launch failed", fg="red")
                self.launch_btn.config(state="normal")
                self.kill_btn.config(state="disabled")
        
        threading.Thread(target=launch_thread, daemon=True).start()
    
    def launch_game_for_instance(self, instance_name, instance):
        """Launch game for a specific instance"""
        version = instance.get('version')
        profile_name = instance.get('profile')
        memory = instance.get('memory', '2048')
        min_memory = instance.get('min_memory', '512')
        instance_dir = instance['path']
        natives_dir = os.path.join(instance_dir, "natives")
        
        # Create natives directory
        os.makedirs(natives_dir, exist_ok=True)
        
        # Get username from profile
        username = "Player"
        if profile_name and profile_name in self.profiles:
            username = self.profiles[profile_name].get('username', profile_name)
        
        # Get selected Java
        java_selection = self.java_var.get()
        if not java_selection or java_selection == "No Java found":
            messagebox.showerror("Error", "No Java installation selected")
            return
        
        java_path = None
        for java in self.java_manager.java_installations:
            if java['name'] == java_selection:
                java_path = java['path']
                break
        
        if not java_path:
            messagebox.showerror("Error", "Could not find selected Java installation")
            return
        
        self.launch_btn.config(state="disabled")
        self.kill_btn.config(state="disabled")
        self.progress['value'] = 0
        
        # Switch to console tab
        self.notebook.select(2)
        
        def launch_thread():
            try:
                self.log_to_console("=" * 60)
                self.log_to_console(f"Launching Instance: {instance_name}")
                self.log_to_console(f"Minecraft {version}")
                self.log_to_console(f"Username: {username}")
                self.log_to_console(f"Java: {java_path}")
                self.log_to_console(f"Memory: {min_memory}MB - {memory}MB")
                self.log_to_console("=" * 60)
                
                # Check if version is downloaded
                version_dir = os.path.join(self.versions_dir, version)
                json_path = os.path.join(version_dir, f"{version}.json")
                jar_path = os.path.join(version_dir, f"{version}.jar")
                
                if not os.path.exists(json_path) or not os.path.exists(jar_path):
                    self.status_label.config(text=f"Downloading {version}...", fg="blue")
                    self.log_to_console(f"Version {version} not found locally, downloading...")
                    if not self.download_version(version):
                        self.launch_btn.config(state="normal")
                        return
                else:
                    self.log_to_console(f"✓ Version {version} found locally")
                
                # Load version JSON
                with open(json_path, 'r') as f:
                    version_json = json.load(f)
                
                # Extract natives to instance directory
                self.log_to_console(f"Extracting natives to instance...")
                self.extract_natives_to_dir(version_json, natives_dir)
                
                # Build classpath
                self.status_label.config(text="Building classpath...", fg="blue")
                self.log_to_console("Building classpath...")
                classpath = []
                
                # Add libraries with proper LWJGL version selection
                if 'libraries' in version_json:
                    for lib in version_json['libraries']:
                        # Check rules
                        if 'rules' in lib:
                            allowed = self.check_rules(lib['rules'])
                            if not allowed:
                                continue
                        
                        # Skip natives from classpath
                        if 'natives' in lib:
                            continue
                        
                        lib_path = None
                        
                        # Try modern format
                        if 'downloads' in lib and 'artifact' in lib['downloads']:
                            artifact = lib['downloads']['artifact']
                            lib_path = os.path.join(self.libraries_dir, artifact['path'])
                        # Try legacy format
                        elif 'name' in lib:
                            constructed_path = self.construct_library_path(lib['name'])
                            if constructed_path:
                                lib_path = os.path.join(self.libraries_dir, constructed_path)
                        
                        if lib_path and os.path.exists(lib_path):
                            classpath.append(lib_path)
                        elif lib_path:
                            self.log_to_console(f"  Warning: Missing library {os.path.basename(lib_path)}")
                
                # Add client JAR
                classpath.append(jar_path)
                
                self.log_to_console(f"✓ Classpath built with {len(classpath)} entries")
                
                # Build classpath string
                cp_separator = ';' if platform.system() == 'Windows' else ':'
                classpath_str = cp_separator.join(classpath)
                
                # Get main class
                main_class = version_json.get('mainClass', 'net.minecraft.client.Minecraft')
                self.log_to_console(f"Main class: {main_class}")
                
                # Create instance directory structure
                saves_dir = os.path.join(instance_dir, "saves")
                resources_dir = os.path.join(instance_dir, "resources")
                os.makedirs(saves_dir, exist_ok=True)
                os.makedirs(resources_dir, exist_ok=True)
                
                # Generate UUID for offline account
                import uuid
                player_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))
                
                # Build launch command
                launch_args = [
                    java_path,
                    f"-Xmx{memory}M",
                    f"-Xms{min_memory}M",
                    f"-Djava.library.path={natives_dir}",
                    "-cp", classpath_str,
                    main_class
                ]
                
                # Add game arguments
                if 'minecraftArguments' in version_json:
                    # Old format (pre-1.13)
                    game_args = version_json['minecraftArguments']
                    game_args = game_args.replace('${auth_player_name}', username)
                    game_args = game_args.replace('${version_name}', version)
                    game_args = game_args.replace('${game_directory}', instance_dir)
                    game_args = game_args.replace('${assets_root}', self.assets_dir)
                    game_args = game_args.replace('${assets_index_name}', version_json.get('assets', 'legacy'))
                    game_args = game_args.replace('${auth_uuid}', player_uuid)
                    game_args = game_args.replace('${auth_access_token}', '0')
                    game_args = game_args.replace('${user_type}', 'legacy')
                    game_args = game_args.replace('${version_type}', version_json.get('type', 'release'))
                    game_args = game_args.replace('${user_properties}', '{}')
                    
                    launch_args.extend(game_args.split())
                elif 'arguments' in version_json and 'game' in version_json['arguments']:
                    # New format (1.13+)
                    for arg in version_json['arguments']['game']:
                        if isinstance(arg, str):
                            arg = arg.replace('${auth_player_name}', username)
                            arg = arg.replace('${version_name}', version)
                            arg = arg.replace('${game_directory}', instance_dir)
                            arg = arg.replace('${assets_root}', self.assets_dir)
                            arg = arg.replace('${assets_index_name}', version_json.get('assets', 'legacy'))
                            arg = arg.replace('${auth_uuid}', player_uuid)
                            arg = arg.replace('${auth_access_token}', '0')
                            arg = arg.replace('${user_type}', 'legacy')
                            arg = arg.replace('${version_type}', version_json.get('type', 'release'))
                            launch_args.append(arg)
                else:
                    # Very old versions - just add username
                    launch_args.append(username)
                
                self.log_to_console("Launch command prepared")
                self.status_label.config(text=f"Starting {version}...", fg="green")
                self.progress['value'] = 100
                
                # Launch the game
                self.log_to_console("Starting game process...")
                self.log_to_console("-" * 60)
                
                if platform.system() == 'Windows':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    self.game_process = subprocess.Popen(launch_args, cwd=instance_dir,
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.STDOUT,
                                              startupinfo=startupinfo,
                                              universal_newlines=True,
                                              bufsize=1)
                else:
                    self.game_process = subprocess.Popen(launch_args, cwd=instance_dir,
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.STDOUT,
                                              universal_newlines=True,
                                              bufsize=1)
                
                # Enable kill button
                self.kill_btn.config(state="normal")
                
                # Read output in real-time
                for line in self.game_process.stdout:
                    self.log_to_console(line.rstrip())
                
                # Wait for process to complete
                return_code = self.game_process.wait()
                
                self.log_to_console("-" * 60)
                if return_code == 0:
                    self.log_to_console(f"✓ Game exited normally (code {return_code})")
                    self.status_label.config(text="Game closed normally", fg="green")
                else:
                    self.log_to_console(f"✗ Game exited with code {return_code}")
                    self.status_label.config(text=f"Game exited with error (code {return_code})", fg="red")
                
                self.launch_btn.config(state="normal")
                self.kill_btn.config(state="disabled")
                
            except Exception as e:
                error_msg = f"Failed to launch game: {str(e)}"
                self.log_to_console(f"✗ ERROR: {error_msg}")
                messagebox.showerror("Launch Error", error_msg)
                self.status_label.config(text="Launch failed", fg="red")
                self.launch_btn.config(state="normal")
                self.kill_btn.config(state="disabled")
        
        threading.Thread(target=launch_thread, daemon=True).start()
    
    def extract_natives_to_dir(self, version_json, target_dir):
        """Extract native libraries to a specific directory"""
        try:
            self.log_to_console(f"Extracting natives to: {target_dir}")
            extracted_count = 0
            
            # Clear directory first
            if os.path.exists(target_dir):
                for file in os.listdir(target_dir):
                    file_path = os.path.join(target_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        pass
            
            os.makedirs(target_dir, exist_ok=True)
            
            for lib in version_json.get('libraries', []):
                # Check rules
                if 'rules' in lib:
                    allowed = self.check_rules(lib['rules'])
                    if not allowed:
                        continue
                
                if 'natives' in lib:
                    os_name = self.get_os_name()
                    if os_name in lib['natives']:
                        classifier = lib['natives'][os_name]
                        arch = platform.architecture()[0][:2]
                        classifier = classifier.replace('${arch}', arch)
                        
                        native_path = None
                        
                        # Try modern format
                        if 'downloads' in lib and 'classifiers' in lib['downloads']:
                            if classifier in lib['downloads']['classifiers']:
                                native_info = lib['downloads']['classifiers'][classifier]
                                native_path = os.path.join(self.libraries_dir, native_info['path'])
                        
                        # Extract if exists
                        if native_path and os.path.exists(native_path):
                            try:
                                with zipfile.ZipFile(native_path, 'r') as zip_ref:
                                    excludes = []
                                    if 'extract' in lib and 'exclude' in lib['extract']:
                                        excludes = lib['extract']['exclude']
                                    
                                    for member in zip_ref.namelist():
                                        should_extract = True
                                        for exclude in excludes:
                                            if member.startswith(exclude):
                                                should_extract = False
                                                break
                                        
                                        if should_extract and not member.endswith('/'):
                                            zip_ref.extract(member, target_dir)
                                            extracted_count += 1
                                
                                self.log_to_console(f"  ✓ Extracted {os.path.basename(native_path)}")
                            except Exception as e:
                                self.log_to_console(f"  ✗ Failed to extract {os.path.basename(native_path)}: {e}")
            
            if extracted_count > 0:
                self.log_to_console(f"✓ Extracted {extracted_count} native files")
            else:
                self.log_to_console(f"Warning: No native files extracted")
                
        except Exception as e:
            self.log_to_console(f"✗ Error extracting natives: {e}")
    
    def check_rules(self, rules):
        """Check if library rules allow this platform"""
        action = True
        for rule in rules:
            if rule['action'] == 'allow':
                if 'os' in rule:
                    os_name = rule['os'].get('name', '')
                    current_os = self.get_os_name()
                    action = (os_name == current_os)
                else:
                    action = True
            elif rule['action'] == 'disallow':
                if 'os' in rule:
                    os_name = rule['os'].get('name', '')
                    current_os = self.get_os_name()
                    if os_name == current_os:
                        action = False
        return action
    
    def get_os_name(self):
        """Get OS name for Minecraft format"""
        system = platform.system()
        if system == 'Windows':
            return 'windows'
        elif system == 'Darwin':
            return 'osx'
        elif system == 'Linux':
            return 'linux'
        return 'unknown'


def main():
    root = tk.Tk()
    app = LegacyMinecraftLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
