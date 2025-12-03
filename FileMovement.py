#!/usr/bin/env python3
"""
File Organizer Script
Automatically sorts files into categorized folders based on file type.
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict


def get_all_files(directory):
    """
    Recursively scan directory and return all file paths.
    
    Args:
        directory: Path to the directory to scan
        
    Returns:
        List of Path objects for all files found
    """
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            files.append(Path(root) / filename)
    return files


def organize_files(source_directory, create_subfolders=True):
    """
    Organize files in the directory by moving them into folders based on extension.
    
    Args:
        source_directory: Path to the directory to organize
        create_subfolders: If True, create type folders in source directory
    """
    source_path = Path(source_directory).resolve()
    
    # Validate directory exists
    if not source_path.exists() or not source_path.is_dir():
        print(f"Error: '{source_directory}' is not a valid directory.")
        return
    
    print(f"Scanning directory: {source_path}")
    
    # Get all files recursively
    all_files = get_all_files(source_path)
    
    if not all_files:
        print("No files found to organize.")
        return
    
    # Group files by extension
    files_by_type = defaultdict(list)
    for file_path in all_files:
        # Get extension without the dot, convert to uppercase
        extension = file_path.suffix.lstrip('.').upper()
        
        # Skip files without extension
        if not extension:
            extension = "NO_EXTENSION"
        
        files_by_type[extension].append(file_path)
    
    # Statistics
    total_moved = 0
    total_errors = 0
    
    # Process each file type
    for file_type, files in files_by_type.items():
        # Create destination folder
        dest_folder = source_path / file_type
        
        try:
            dest_folder.mkdir(exist_ok=True)
            print(f"\n--- Processing {file_type} files ({len(files)} found) ---")
        except Exception as e:
            print(f"Error creating folder '{file_type}': {e}")
            total_errors += len(files)
            continue
        
        # Move files
        for file_path in files:
            # Skip if file is already in the correct folder
            if file_path.parent == dest_folder:
                print(f"  Skipping (already in place): {file_path.name}")
                continue
            
            # Handle filename conflicts
            dest_file = dest_folder / file_path.name
            counter = 1
            original_stem = dest_file.stem
            
            while dest_file.exists():
                dest_file = dest_folder / f"{original_stem}_{counter}{file_path.suffix}"
                counter += 1
            
            # Move the file
            try:
                shutil.move(str(file_path), str(dest_file))
                print(f"  Moved: {file_path.name} -> {file_type}/")
                total_moved += 1
            except Exception as e:
                print(f"  Error moving {file_path.name}: {e}")
                total_errors += 1
    
    # Clean up empty directories (except the organized folders)
    cleanup_empty_dirs(source_path, files_by_type.keys())
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Organization Complete!")
    print(f"Total files moved: {total_moved}")
    print(f"Errors encountered: {total_errors}")
    print(f"{'='*50}")


def cleanup_empty_dirs(directory, exclude_folders):
    """
    Remove empty directories, excluding the organized type folders.
    
    Args:
        directory: Root directory to clean
        exclude_folders: Set of folder names to exclude from deletion
    """
    removed_count = 0
    
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            
            # Skip the organized type folders
            if dir_name in exclude_folders:
                continue
            
            # Check if directory is empty
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    print(f"  Removed empty directory: {dir_path.relative_to(directory)}")
                    removed_count += 1
            except Exception as e:
                # Directory not empty or error occurred
                pass
    
    if removed_count > 0:
        print(f"\nRemoved {removed_count} empty director{'y' if removed_count == 1 else 'ies'}")


def main():
    """Main function to run the file organizer."""
    print("=" * 50)
    print("File Organizer - Sort files by type")
    print("=" * 50)
    
    # Get directory from user
    directory = input("\nEnter the directory path to organize (or press Enter for current directory): ").strip()
    
    # Use current directory if none specified
    if not directory:
        directory = os.getcwd()
    
    # Confirm action
    print(f"\nThis will organize all files in: {directory}")
    print("Files will be moved into folders based on their extension.")
    confirm = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        organize_files(directory)
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    main()
