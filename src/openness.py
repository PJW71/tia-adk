
import sys
import os

# Standard path, can be improved with config
TIA_API_PATH = os.getenv("TIA_API_PATH", r"C:\Program Files\Siemens\Automation\Portal V17\PublicAPI\V17")

class TiaOpenness:
    def __init__(self, api_path=TIA_API_PATH):
        try:
            import clr
        except ImportError:
            raise ImportError("pythonnet is required for TIA Portal Openness. Please install it with 'pip install pythonnet'.")
        except RuntimeError as e:
             raise RuntimeError(f"Failed to initialize .NET runtime: {e}. Ensure you are on Windows or have Mono installed.")

        self.api_path = api_path
        self.tia_portal = None
        self.project = None
        self._load_assemblies()

    def _load_assemblies(self):
        """Load Siemens Engineering DLLs"""
        if not os.path.exists(self.api_path):
            raise FileNotFoundError(f"TIA Portal API not found at {self.api_path}")
        
        dll_path = os.path.join(self.api_path, "Siemens.Engineering.dll")
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"DLL not found: {dll_path}")

        try:
            import clr
            clr.AddReference(dll_path)
            import Siemens.Engineering
            print(f"Successfully loaded Siemens.Engineering from {dll_path}")
        except Exception as e:
            raise Exception(f"Failed to load Siemens.Engineering: {e}")

    def connect(self):
        """Connect to a running TIA Portal instance"""
        import Siemens.Engineering
        print("Searching for TIA Portal processes...")
        processes = Siemens.Engineering.TiaPortal.GetProcesses()
        print(f"Found {len(processes)} processes.")
        if len(processes) == 0:
            raise Exception("No running TIA Portal instance found.")
        
        # Connect to the first available process
        print(f"Attaching to process {processes[0].Id}...")
        self.tia_portal = processes[0].Attach()
        print(f"Connected to TIA Portal: {self.tia_portal.GetCurrentProcess().Id}")

    def load_project(self):
        """Load the active project"""
        if not self.tia_portal:
            raise Exception("Not connected to TIA Portal")
        
        print("Accessing Projects collection...")
        projects = self.tia_portal.Projects
        print(f"Found {projects.Count} open projects.")
        if projects.Count == 0:
            raise Exception("No open project found in TIA Portal")
        
        self.project = projects[0]
        print(f"Loaded Project: {self.project.Name}")

    def export_plc_blocks(self, export_dir):
        """Export all PLC blocks to XML"""
        if not self.project:
            self.load_project()
            
        import System.IO
        
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        # Iterate through devices (simplified, assumes one PLC or iterates all)
        for device in self.project.Devices:
            print(f"Scanning Device: {device.Name}")
            # This needs deep traversal to find PLC blocks, implementing a simple search for demonstration
            self._recursive_export(device, export_dir)

    def _recursive_export(self, item, export_dir):
        """Recursively find and export blocks"""
        import Siemens.Engineering
        
        # TIA Portal Hierarchy typically:
        # Project -> Devices -> DeviceItem -> ... -> PlcSoftware -> BlockGroup -> Blocks
        # We need to traverse down to find PlcSoftware.
        
        # Check if current item has 'DeviceItems' (e.g. valid device or folder)
        if hasattr(item, "DeviceItems"):
            for sub_item in item.DeviceItems:
                self._recursive_export(sub_item, export_dir)
                
        try:
             # Try to get PlcSoftware from DeviceItem
            import Siemens.Engineering.HW.Features
            software_container = item.GetService[Siemens.Engineering.HW.Features.SoftwareContainer]()
            if software_container:
                software = software_container.Software
                import Siemens.Engineering.SW
                if isinstance(software, Siemens.Engineering.SW.PlcSoftware):
                    self._export_blocks_from_software(software, export_dir)
        except:
             # If GetService fails or types don't match, just continue
             pass

    def _export_blocks_from_software(self, software, export_dir):
        """Export blocks from PlcSoftware"""
        print(f"Found PLC Software, exporting blocks...")
        # Recursively export from BlockGroups
        self._export_block_group(software.BlockGroup, export_dir)

    def _export_block_group(self, block_group, export_dir):
        # Export Blocks in this group
        for block in block_group.Blocks:
            self._export_block(block, export_dir)
            
        # Recurse into subgroups
        for group in block_group.Groups:
            self._export_block_group(group, export_dir)

    def _export_block(self, block, export_dir):
        """Export a single block"""
        import Siemens.Engineering
        try:
            # We filter for global DBs, OBs, FBs, FCs. 
            # Some blocks might not be exportable (e.g. know-how protected without password)
            import System.IO
            file_name = f"{block.Name}.xml"
            # Sanitize filename
            invalid_chars = System.IO.Path.GetInvalidFileNameChars()
            for char in invalid_chars:
                file_name = file_name.replace(char, '_')
                
            path = os.path.abspath(os.path.join(export_dir, file_name))
            if block.IsConsistent: 
                # generic export options
                 # Export(FileInfo path, ExportOptions options)
                export_options = getattr(Siemens.Engineering.ExportOptions, "None")
                block.Export(System.IO.FileInfo(path), export_options)
                print(f"Exported: {file_name}")
            else:
                print(f"Skipped {block.Name} (Inconsistent)")
        except Exception as e:
            print(f"Failed to export {block.Name}: {e}")

