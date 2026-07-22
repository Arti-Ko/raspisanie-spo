from PIL import Image, ImageDraw

ACCENT = (68, 114, 196, 255)
ACCENT_DARK = (31, 56, 100, 255)
WHITE = (255, 255, 255, 255)
SIZE = 1024


def build_icon() -> Image.Image:
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    margin = 48
    radius = 190
    draw.rounded_rectangle(
        [margin, margin, SIZE - margin, SIZE - margin], radius=radius, fill=ACCENT
    )

    header_bottom = 330
    draw.rounded_rectangle(
        [margin, margin, SIZE - margin, header_bottom + radius],
        radius=radius,
        fill=ACCENT_DARK,
    )
    draw.rectangle([margin, header_bottom - radius, SIZE - margin, header_bottom], fill=ACCENT_DARK)
    draw.rectangle([margin, header_bottom, SIZE - margin, header_bottom + 6], fill=ACCENT)

    ring_width = 34
    ring_top = margin - 40
    ring_height = 170
    for cx in (SIZE * 0.32, SIZE * 0.68):
        draw.rounded_rectangle(
            [cx - ring_width / 2, ring_top, cx + ring_width / 2, ring_top + ring_height],
            radius=ring_width / 2,
            fill=ACCENT_DARK,
        )

    grid_top = header_bottom + 70
    grid_bottom = SIZE - margin - 70
    grid_left = margin + 90
    grid_right = SIZE - margin - 90
    cols = 3
    rows = 3
    cell_w = (grid_right - grid_left) / cols
    cell_h = (grid_bottom - grid_top) / rows
    pad = 16
    for row in range(rows):
        for col in range(cols):
            x0 = grid_left + col * cell_w + pad
            y0 = grid_top + row * cell_h + pad
            x1 = grid_left + (col + 1) * cell_w - pad
            y1 = grid_top + (row + 1) * cell_h - pad
            fill = WHITE if (row + col) % 2 == 0 else (255, 255, 255, 130)
            draw.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=fill)

    return image


if __name__ == "__main__":
    icon = build_icon()
    icon.save("assets/icon.png")
    print("saved assets/icon.png", icon.size)
