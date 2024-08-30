from PIL import Image, ImageDraw

def draw_pacman(filename, pacman_color, mouth_start, mouth_end):
    # Create a new image with transparent background
    img_size = (500, 500)
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Define the Pac-Man's parameters with a reduced radius
    pacman_center = (250, 250)  # Center of the image
    pacman_radius = 180  # Reduced radius to prevent touching edges

    # Draw the full circle (Pac-Man's body)
    draw.ellipse(
        [pacman_center[0] - pacman_radius, pacman_center[1] - pacman_radius,
         pacman_center[0] + pacman_radius, pacman_center[1] + pacman_radius],
        fill=pacman_color
    )
    
    # Draw the bite (pie slice) to make the Pac-Man's mouth
    draw.pieslice(
        [pacman_center[0] - pacman_radius, pacman_center[1] - pacman_radius,
         pacman_center[0] + pacman_radius, pacman_center[1] + pacman_radius],
        mouth_start, mouth_end, fill=(0, 0, 0, 0)  # Transparent slice
    )

    # Save the image
    img.save(filename)

def generate_pacman_images():
    # Generate images from 1.png to 9.png (golden Pac-Man)
    for i in range(1, 10):
        angle = (i - 1) * 5  # Adjust angle for each image
        # Calculate the mouth_start and mouth_end so that the mouth points to the right
        mouth_start = -angle
        mouth_end = angle
        filename = f"{i}.png"
        draw_pacman(filename, (255, 215, 0), mouth_start, mouth_end)

    # Generate images from A.png to I.png (red Pac-Man)
    for i in range(9):
        angle = i * 5  # Adjust angle for each image
        # Calculate the mouth_start and mouth_end so that the mouth points to the right
        mouth_start = -angle
        mouth_end = angle
        filename = f"{chr(65 + i)}.png"  # Convert 0-8 to A-I
        draw_pacman(filename, (255, 0, 0), mouth_start, mouth_end)

generate_pacman_images()
