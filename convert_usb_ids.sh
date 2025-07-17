#!/bin/bash
# http://www.linux-usb.org/usb-ids.html

INPUT_FILE="usb.ids"
OUTPUT_FILE="src/usb_db.py"

if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Input file '$INPUT_FILE' not found."
    exit 1
fi

echo "usb_db = {" > "$OUTPUT_FILE"

current_vendor=""
inside_vendor=0

while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^# ]] && continue
    [[ -z "$line" ]] && continue

    if [[ "$line" =~ ^[0-9a-fA-F]{4} ]]; then
        # Close previous vendor if needed
        if [[ $inside_vendor -eq 1 ]]; then
            echo "        }," >> "$OUTPUT_FILE"
            echo "    }," >> "$OUTPUT_FILE"
        fi

        # Vendor line
        vid=$(echo "$line" | awk '{print tolower($1)}')
        vendor_name=$(echo "$line" | cut -d' ' -f2- | sed 's/"/\\"/g')
        echo "    \"$vid\": {" >> "$OUTPUT_FILE"
        echo "        \"name\": \"$vendor_name\"," >> "$OUTPUT_FILE"
        echo "        \"products\": {" >> "$OUTPUT_FILE"
        inside_vendor=1
        current_vendor="$vid"

    elif [[ "$line" =~ ^[[:space:]]+[0-9a-fA-F]{4} ]]; then
        # Product line (only if inside vendor block)
        if [[ $inside_vendor -eq 1 ]]; then
            pid=$(echo "$line" | awk '{print tolower($1)}')
            product_name=$(echo "$line" | cut -d' ' -f2- | sed 's/"/\\"/g')
            echo "            \"$pid\": \"$product_name\"," >> "$OUTPUT_FILE"
        fi
    fi
done < "$INPUT_FILE"

# Close final vendor block
if [[ $inside_vendor -eq 1 ]]; then
    echo "        }," >> "$OUTPUT_FILE"
    echo "    }," >> "$OUTPUT_FILE"
fi

echo "}" >> "$OUTPUT_FILE"

echo "✔ Converted '$INPUT_FILE' to '$OUTPUT_FILE'"

