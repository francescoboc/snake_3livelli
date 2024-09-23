#!/bin/bash

# Base image
base_image="img/arrow.png"

# Check if the base image exists
if [ ! -f "$base_image" ]; then
    echo "Base image '$base_image' not found!"
    exit 1
fi

# Get original dimensions
original_dimensions=$(gm identify -format "%wx%h" "$base_image")
original_width=$(echo $original_dimensions | cut -dx -f1)
original_height=$(echo $original_dimensions | cut -dx -f2)

# Compass angles and corresponding output filenames
declare -A compass_angles=(
    ["north"]=0
    ["north_east"]=45
    ["east"]=90
    ["south_east"]=135
    ["south"]=180
    ["south_west"]=225
    ["west"]=270
    ["north_west"]=315
)

# Iterate over the compass angles and create rotated images
for direction in "${!compass_angles[@]}"; do
    angle=${compass_angles[$direction]}
    output_image="img/${direction}.png"
    
    # # Rotate the image using ImageMagick's convert command
    # gm convert "$base_image" -rotate "$angle" "$output_image"

    # Rotate the image using GraphicsMagick
    gm convert "$base_image" -background none -rotate "$angle" \
        -gravity Center -crop "${original_width}x${original_height}+0+0" "$output_image"
    
    # Check if the command was successful
    if [ $? -eq 0 ]; then
        echo "Image rotated to '$output_image' at angle $angle degrees."
    else
        echo "Failed to rotate the image for direction '$direction'."
    fi
done

