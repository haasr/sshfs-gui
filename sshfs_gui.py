"""
SSHFS GUI - A complete graphical interface for SSHFS with public key authentication support
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import json
import threading
from pathlib import Path

class SSHFSGui:
    def __init__(self, root):
        self.root = root
        self.root.title("SSHFS GUI - Advanced")
        self.root.geometry("600x850")
        
        # Configuration file for saving recent servers
        self.config_file = Path.home() / ".sshfs_gui_config.json"
        self.recent_servers = self.load_recent_servers()
        
        # Variables
        self.auth_method = tk.StringVar(value="password")
        self.connection_mode = tk.StringVar(value="passive")
        self.show_password = tk.BooleanVar()
        self.mount_on_startup = tk.BooleanVar()
        self.auto_reconnect = tk.BooleanVar()
        self.allow_other = tk.BooleanVar()
        
        self.setup_gui()
        
    def setup_gui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        current_row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="SSHFS GUI", font=("Arial", 16, "bold"))
        title_label.grid(row=current_row, column=0, columnspan=3, pady=(0, 20))
        current_row += 1
        
        # Server Connection Frame
        conn_frame = ttk.LabelFrame(main_frame, text="Server Connection", padding="10")
        conn_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        current_row += 1
        
        # Server
        ttk.Label(conn_frame, text="Server:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.server_entry = ttk.Entry(conn_frame, width=40)
        self.server_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Port
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.port_entry = ttk.Entry(conn_frame, width=8)
        self.port_entry.grid(row=0, column=3, sticky=tk.W)
        self.port_entry.insert(0, "22")
        
        # Username
        ttk.Label(conn_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.username_entry = ttk.Entry(conn_frame, width=40)
        self.username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        # Authentication Method Frame
        auth_frame = ttk.LabelFrame(main_frame, text="Authentication", padding="10")
        auth_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        auth_frame.columnconfigure(1, weight=1)
        current_row += 1
        
        # Authentication method radio buttons
        ttk.Radiobutton(auth_frame, text="Password", variable=self.auth_method, 
                       value="password", command=self.on_auth_method_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(auth_frame, text="Public Key", variable=self.auth_method, 
                       value="key", command=self.on_auth_method_change).grid(row=0, column=1, sticky=tk.W)
        
        # Password frame
        self.password_frame = ttk.Frame(auth_frame)
        self.password_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.password_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.password_frame, text="Password:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.password_entry = ttk.Entry(self.password_frame, show="*", width=40)
        self.password_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Checkbutton(self.password_frame, text="Show", variable=self.show_password,
                       command=self.toggle_password_visibility).grid(row=0, column=2, sticky=tk.W)
        
        # Public key frame
        self.key_frame = ttk.Frame(auth_frame)
        self.key_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.key_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.key_frame, text="Private Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.key_entry = ttk.Entry(self.key_frame, width=40)
        self.key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(self.key_frame, text="Browse", command=self.browse_key_file).grid(row=0, column=2, sticky=tk.W)
        
        # Set default key path
        default_key = str(Path.home() / ".ssh" / "id_rsa")
        if os.path.exists(default_key):
            self.key_entry.insert(0, default_key)
        
        # Directory Mapping Frame
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Mapping", padding="10")
        dir_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        current_row += 1
        
        # Remote directory
        ttk.Label(dir_frame, text="Remote Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.remote_dir_entry = ttk.Entry(dir_frame, width=40)
        self.remote_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.remote_dir_entry.insert(0, "/")
        
        # Local directory
        ttk.Label(dir_frame, text="Local Directory:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.local_dir_entry = ttk.Entry(dir_frame, width=40)
        self.local_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_local_dir).grid(row=1, column=2, sticky=tk.W, pady=(10, 0))
        
        # Advanced Options Frame
        advanced_frame = ttk.LabelFrame(main_frame, text="Advanced Options", padding="10")
        advanced_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        advanced_frame.columnconfigure(1, weight=1)
        current_row += 1
        
        # Connection mode
        ttk.Label(advanced_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        mode_combo = ttk.Combobox(advanced_frame, textvariable=self.connection_mode, 
                                 values=["passive", "active"], state="readonly", width=15)
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        # Additional options
        ttk.Label(advanced_frame, text="Additional Options:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.options_entry = ttk.Entry(advanced_frame, width=40)
        self.options_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        # Checkboxes
        ttk.Checkbutton(advanced_frame, text="Auto-reconnect", variable=self.auto_reconnect).grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Checkbutton(advanced_frame, text="Mount on startup", variable=self.mount_on_startup).grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        ttk.Checkbutton(advanced_frame, text="Allow other users (might be necessary for some applications)", variable=self.allow_other).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        # Recent Servers Frame
        recent_frame = ttk.LabelFrame(main_frame, text="Recent Servers", padding="10")
        recent_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        recent_frame.columnconfigure(0, weight=1)
        current_row += 1
        
        # Recent servers listbox
        self.recent_listbox = tk.Listbox(recent_frame, height=3)
        self.recent_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.recent_listbox.bind('<Double-1>', self.load_recent_server)
        
        recent_scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.recent_listbox.yview)
        recent_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.recent_listbox.configure(yscrollcommand=recent_scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=0, columnspan=3, pady=(10, 0))
        current_row += 1
        
        ttk.Button(button_frame, text="Mount", command=self.mount_filesystem).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Unmount", command=self.unmount_filesystem).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Test Connection", command=self.test_connection).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="Save Config", command=self.save_current_config).grid(row=0, column=3, padx=(0, 5))
        
        # Status and Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Status & Log", padding="10")
        log_frame.grid(row=current_row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(current_row, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize GUI state
        self.on_auth_method_change()
        self.populate_recent_servers()
        self.log_message("SSHFS GUI initialized successfully")
        
    def on_auth_method_change(self):
        """Handle authentication method change"""
        if self.auth_method.get() == "password":
            # Show password frame, hide key frame
            for widget in self.password_frame.winfo_children():
                widget.configure(state="normal")
            for widget in self.key_frame.winfo_children():
                widget.configure(state="disabled")
        else:
            # Show key frame, hide password frame
            for widget in self.password_frame.winfo_children():
                widget.configure(state="disabled")
            for widget in self.key_frame.winfo_children():
                widget.configure(state="normal")
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
    
    def browse_key_file(self):
        """Browse for private key file"""
        filename = filedialog.askopenfilename(
            title="Select Private Key File",
            initialdir=str(Path.home() / ".ssh"),
            filetypes=[("All files", "*")]
        )
        if filename:
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, filename)
    
    def browse_local_dir(self):
        """Browse for local directory"""
        dirname = filedialog.askdirectory(title="Select Local Mount Directory")
        if dirname:
            self.local_dir_entry.delete(0, tk.END)
            self.local_dir_entry.insert(0, dirname)
    
    def log_message(self, message):
        """Add message to log"""
        print(message)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.server_entry.get().strip():
            messagebox.showerror("Error", "Server address is required")
            return False
        
        if not self.username_entry.get().strip():
            messagebox.showerror("Error", "Username is required")
            return False
        
        if not self.local_dir_entry.get().strip():
            messagebox.showerror("Error", "Local directory is required")
            return False
        
        if self.auth_method.get() == "password" and not self.password_entry.get():
            messagebox.showerror("Error", "Password is required for password authentication")
            return False
        
        if self.auth_method.get() == "key":
            key_file = self.key_entry.get().strip()
            if not key_file:
                messagebox.showerror("Error", "Private key file is required for key authentication")
                return False
            if not os.path.exists(key_file):
                messagebox.showerror("Error", f"Private key file does not exist: {key_file}")
                return False
        
        # Create local directory if it doesn't exist
        local_dir = self.local_dir_entry.get().strip()
        if not os.path.exists(local_dir):
            try:
                os.makedirs(local_dir)
                self.log_message(f"Created local directory: {local_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create local directory: {e}")
                return False
        
        return True
    
    def build_sshfs_command(self):
        """Build the SSHFS command"""
        server = self.server_entry.get().strip()
        port = self.port_entry.get().strip() or "22"
        username = self.username_entry.get().strip()
        remote_dir = self.remote_dir_entry.get().strip() or "/"
        local_dir = self.local_dir_entry.get().strip()
        
        # Base command
        remote_path = f"{username}@{server}:{remote_dir}"
        cmd = ["sshfs", remote_path, local_dir]
        
        # Add port
        cmd.extend(["-p", port])
        
        # Add authentication options
        if self.auth_method.get() == "key":
            key_file = self.key_entry.get().strip()
            cmd.extend(["-o", f"IdentityFile={key_file}"])
            cmd.extend(["-o", "PasswordAuthentication=no"])
        
        # Add common options
        cmd.extend(["-o", "reconnect"])
        cmd.extend(["-o", "ServerAliveInterval=15"])
        cmd.extend(["-o", "ServerAliveCountMax=3"])
        
        # Add allow_other option if selected
        if self.allow_other.get():
            cmd.extend(["-o", "allow_other"])
        
        # Add additional options
        additional_opts = self.options_entry.get().strip()
        if additional_opts:
            for opt in additional_opts.split():
                cmd.extend(["-o", opt])
        
        return cmd
    
    def mount_filesystem(self):
        """Mount the SSHFS filesystem"""
        if not self.validate_inputs():
            return
        
        try:
            cmd = self.build_sshfs_command()
            self.log_message(f"Executing: {' '.join(cmd)}")
            
            # For password authentication, we need to handle password input
            if self.auth_method.get() == "password":
                # Use expect or similar for password input in production
                # For now, we'll use a simple approach
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Send password if needed
                try:
                    stdout, stderr = process.communicate(
                        input=self.password_entry.get() + "\n", 
                        timeout=10
                    )
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.log_message("Mount operation timed out")
                    return
            else:
                # For key authentication
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                stdout, stderr = process.stdout, process.stderr
            
            if process.returncode == 0:
                self.log_message("Filesystem mounted successfully!")
                self.save_to_recent_servers()
                messagebox.showinfo("Success", "Filesystem mounted successfully!")
            else:
                error_msg = stderr or "Unknown error occurred"
                self.log_message(f"Mount failed: {error_msg}")
                messagebox.showerror("Mount Failed", f"Failed to mount filesystem:\n{error_msg}")
                
        except Exception as e:
            self.log_message(f"Error during mount: {str(e)}")
            messagebox.showerror("Error", f"Error during mount: {str(e)}")
    
    def unmount_filesystem(self):
        """Unmount the SSHFS filesystem"""
        local_dir = self.local_dir_entry.get().strip()
        if not local_dir:
            messagebox.showerror("Error", "Local directory is required for unmounting")
            return
        
        try:
            # Try fusermount first (Linux)
            cmd = ["umount", local_dir]
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                # Try umount (macOS/BSD)
                cmd = ["umount", local_dir]
                process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0:
                self.log_message("Filesystem unmounted successfully!")
                messagebox.showinfo("Success", "Filesystem unmounted successfully!")
            else:
                error_msg = process.stderr or "Unknown error occurred"
                self.log_message(f"Unmount failed: {error_msg}")
                messagebox.showerror("Unmount Failed", f"Failed to unmount filesystem:\n{error_msg}")
                
        except Exception as e:
            self.log_message(f"Error during unmount: {str(e)}")
            messagebox.showerror("Error", f"Error during unmount: {str(e)}")
    
    def test_connection(self):
        """Test SSH connection"""
        if not self.server_entry.get().strip() or not self.username_entry.get().strip():
            messagebox.showerror("Error", "Server and username are required for testing")
            return
        
        def test_in_thread():
            try:
                server = self.server_entry.get().strip()
                port = self.port_entry.get().strip() or "22"
                username = self.username_entry.get().strip()
                
                cmd = ["ssh", "-p", port, "-o", "ConnectTimeout=10", "-o", "BatchMode=yes"]
                
                if self.auth_method.get() == "key":
                    key_file = self.key_entry.get().strip()
                    if key_file and os.path.exists(key_file):
                        cmd.extend(["-i", key_file])
                
                cmd.extend([f"{username}@{server}", "echo 'Connection successful'"])
                
                self.log_message(f"Testing connection: {' '.join(cmd[:5])}...")
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                if process.returncode == 0:
                    self.log_message("Connection test successful!")
                    messagebox.showinfo("Success", "Connection test successful!")
                else:
                    error_msg = process.stderr or "Connection failed"
                    self.log_message(f"Connection test failed: {error_msg}")
                    messagebox.showerror("Connection Failed", f"Connection test failed:\n{error_msg}")
                    
            except Exception as e:
                self.log_message(f"Error during connection test: {str(e)}")
                messagebox.showerror("Error", f"Error during connection test: {str(e)}")
        
        # Run test in separate thread to avoid blocking GUI
        thread = threading.Thread(target=test_in_thread)
        thread.daemon = True
        thread.start()
    
    def save_current_config(self):
        """Save current configuration to recent servers"""
        self.save_to_recent_servers()
        messagebox.showinfo("Success", "Configuration saved to recent servers!")
    
    def save_to_recent_servers(self):
        """Save current configuration to recent servers"""
        config = {
            "name": f"{self.username_entry.get()}@{self.server_entry.get()}",
            "server": self.server_entry.get(),
            "port": self.port_entry.get(),
            "username": self.username_entry.get(),
            "auth_method": self.auth_method.get(),
            "key_file": self.key_entry.get(),
            "remote_dir": self.remote_dir_entry.get(),
            "local_dir": self.local_dir_entry.get(),
            "additional_options": self.options_entry.get(),
            "allow_other": self.allow_other.get()
        }
        
        # Remove existing entry with same name
        self.recent_servers = [s for s in self.recent_servers if s.get("name") != config["name"]]
        
        # Add to beginning of list
        self.recent_servers.insert(0, config)
        
        # Keep only last 10 entries
        self.recent_servers = self.recent_servers[:10]
        
        # Save to file
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.recent_servers, f, indent=2)
            self.populate_recent_servers()
        except Exception as e:
            self.log_message(f"Failed to save configuration: {e}")
    
    def load_recent_servers(self):
        """Load recent servers from configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load recent servers: {e}")
        return []
    
    def populate_recent_servers(self):
        """Populate recent servers listbox"""
        self.recent_listbox.delete(0, tk.END)
        for server in self.recent_servers:
            self.recent_listbox.insert(tk.END, server.get("name", "Unknown"))
    
    def load_recent_server(self, event):
        """Load selected recent server configuration"""
        selection = self.recent_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.recent_servers):
                config = self.recent_servers[index]
                
                # Load configuration
                self.server_entry.delete(0, tk.END)
                self.server_entry.insert(0, config.get("server", ""))
                
                self.port_entry.delete(0, tk.END)
                self.port_entry.insert(0, config.get("port", "22"))
                
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, config.get("username", ""))
                
                self.auth_method.set(config.get("auth_method", "password"))
                
                self.key_entry.delete(0, tk.END)
                self.key_entry.insert(0, config.get("key_file", ""))
                
                self.remote_dir_entry.delete(0, tk.END)
                self.remote_dir_entry.insert(0, config.get("remote_dir", "/"))
                
                self.local_dir_entry.delete(0, tk.END)
                self.local_dir_entry.insert(0, config.get("local_dir", ""))
                
                self.options_entry.delete(0, tk.END)
                self.options_entry.insert(0, config.get("additional_options", ""))
                
                self.allow_other.set(config.get("allow_other", False))
                
                self.on_auth_method_change()
                self.log_message(f"Loaded configuration: {config.get('name')}")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = SSHFSGui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
