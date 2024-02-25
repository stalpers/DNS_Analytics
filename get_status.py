import os

# Function to consolidate ranges
def consolidate_ranges(file_list):
    ranges = []
    for filename in file_list:
        # Get the number from the filename
        file_num = int(filename.split("_")[1].split(".")[0])

        if ranges and file_num == ranges[-1][-1] + 1:
            # If the current number is one more than the last number of the last range, extend the last range.
            ranges[-1][-1] = file_num
        else:
            # Otherwise, start a new range.
            ranges.append([file_num, file_num])
    return [f"./export/export_{start:010}.txt to ./export/export_{end:010}.txt" for start, end in ranges]

import click
@click.command()
@click.option('--export_dir', 'export_dir', required=True, type=str, help='directory where export files are stored')
@click.option('--expected_count', 'expected_count', required=True, type=int, default=0, help='The number of expected files')
def cli(export_dir, expected_count):

    total_records = expected_count
    missing_files, existing_files = [], []
    for i in range(total_records):
        filename = f"./export/export_{i:010}.txt"
        if os.path.exists(filename):
            existing_files.append(filename)
        else:
            missing_files.append(filename)

    # Consolidate ranges
    missing_files = consolidate_ranges(missing_files)
    existing_files = consolidate_ranges(existing_files)

    # Print a status summary
    print("Status Summary:")
    print("----------------")

    # Existing files
    print("\nExisting Files:")
    if existing_files:
        for file_range in existing_files:
            print(f"- {file_range}")
    else:
        print("No existing files found.")

    # Missing files
    print("\nMissing Files:")
    if missing_files:
        for file_range in missing_files:
            print(f"- {file_range}")
    else:
        print("No missing files.")


if __name__ == '__main__':
    cli()