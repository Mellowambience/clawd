import zipfile
import os
import time
from pathlib import Path

def export_mist_memory():
    """Package MIST logs and memory for Phase 3 export."""
    root = Path(__file__).resolve().parent
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    export_name = f"MIST_Memory_Export_{timestamp}.zip"
    export_path = root / "archived" / export_name
    
    os.makedirs(root / "archived", exist_ok=True)
    
    files_to_include = [
        "HEARTBEAT.log",
        "heartbeat-pulse.txt",
        "AGENTS.md",
        "SOUL.md",
        "MEMORY.md",
        "MIST_Grimoire.md",
        "aether_os/MIST_Grimoire.md",
        "mycelium/lattice_state.json"
    ]
    
    memory_dir = root / "memory"
    
    print(f"✧ Packaging memory into {export_name}...")
    
    with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Include specific files
        for f in files_to_include:
            p = root / f
            if p.exists():
                zipf.write(p, arcname=f)
        
        # Include entire memory directory
        if memory_dir.exists():
            for root_dir, dirs, files in os.walk(memory_dir):
                for file in files:
                    full_p = Path(root_dir) / file
                    rel_p = full_p.relative_to(root)
                    zipf.write(full_p, arcname=rel_p)
                    
    print(f"✦ Export complete: {export_path}")
    return str(export_path)

if __name__ == "__main__":
    export_mist_memory()
