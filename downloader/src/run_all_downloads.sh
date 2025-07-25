#!/bin/bash

# Set the output directory
OUTPUT_DIR="/Users/wjackson/Developer/AI-Building-Blocks/general_files"

# Array of URL list files
URL_LISTS=(
    "url_lists/main_verified_urls.txt"
    "url_lists/verified_essential_docs.txt"
    "url_lists/verified_programming.txt"
    "url_lists/config_build_files_urls.txt"
    "url_lists/data_formats_urls.txt"
    "url_lists/essential_documents_urls.txt"
    "url_lists/programming_languages_urls.txt"
    "url_lists/specialized_formats_urls.txt"
    "url_lists/web_markup_urls.txt"
    "url_lists/xml_download_urls.txt"
)

# Function to process a URL list
process_url_list() {
    local url_list=$1
    echo "Processing URL list: $url_list"
    echo "----------------------------------------"
    python file_downloader.py --urls-file "$url_list" --output-dir "$OUTPUT_DIR"
    echo "----------------------------------------"
    echo "Completed processing: $url_list"
    echo
}

# Main execution
echo "Starting download process..."
echo "Output directory: $OUTPUT_DIR"
echo

# Process each URL list
for url_list in "${URL_LISTS[@]}"; do
    if [ -f "$url_list" ]; then
        process_url_list "$url_list"
    else
        echo "Warning: URL list file not found: $url_list"
    fi
done

echo "All downloads completed!" 