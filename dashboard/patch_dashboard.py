import os

def patch_dashboard():
    dashboard_path = 'c:\\Users\\USER\\Documents\\Maquina de produccion masiva\\ExtraerDatosGoogleAnalitics\\dashboard\\app_woo_v2.py'
    new_content_path = 'c:\\Users\\USER\\Documents\\Maquina de produccion masiva\\ExtraerDatosGoogleAnalitics\\dashboard\\new_main_content.py'
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
        
    with open(new_content_path, 'r', encoding='utf-8') as f:
        new_lines = f.readlines()
        
    # Find start of main function in original file
    # We look for "def main():"
    start_idx = -1
    for i, line in enumerate(original_lines):
        if line.strip().startswith('def main():'):
            start_idx = i
            break
            
    if start_idx == -1:
        print("Error: Could not find 'def main():' in app_woo_v2.py")
        return

    # Keep everything before main
    final_lines = original_lines[:start_idx]
    
    # Append new content
    final_lines.extend(new_lines)
    
    # Write back
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
        
    print("Successfully patched app_woo_v2.py")

if __name__ == "__main__":
    patch_dashboard()
