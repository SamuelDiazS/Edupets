from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "static" / "images"


Color = tuple[int, int, int, int]


def canvas(width: int, height: int, color: Color = (0, 0, 0, 0)) -> bytearray:
    data = bytearray(width * height * 4)
    for y in range(height):
        for x in range(width):
            set_pixel(data, width, height, x, y, color)
    return data


def set_pixel(data: bytearray, width: int, height: int, x: int, y: int, color: Color) -> None:
    if x < 0 or y < 0 or x >= width or y >= height:
        return
    index = (y * width + x) * 4
    alpha = color[3] / 255
    inv = 1 - alpha
    current_alpha = data[index + 3] / 255
    out_alpha = alpha + current_alpha * inv
    if out_alpha == 0:
        data[index : index + 4] = bytes((0, 0, 0, 0))
        return
    for channel in range(3):
        data[index + channel] = int((color[channel] * alpha + data[index + channel] * current_alpha * inv) / out_alpha)
    data[index + 3] = int(out_alpha * 255)


def draw_circle(data: bytearray, width: int, height: int, cx: int, cy: int, radius: int, color: Color) -> None:
    r2 = radius * radius
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                set_pixel(data, width, height, x, y, color)


def draw_ellipse(data: bytearray, width: int, height: int, cx: int, cy: int, rx: int, ry: int, color: Color) -> None:
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) ** 2) / max(1, rx * rx) + ((y - cy) ** 2) / max(1, ry * ry) <= 1:
                set_pixel(data, width, height, x, y, color)


def draw_line(data: bytearray, width: int, height: int, x1: int, y1: int, x2: int, y2: int, thickness: int, color: Color) -> None:
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    for step in range(steps + 1):
        x = round(x1 + (x2 - x1) * step / steps)
        y = round(y1 + (y2 - y1) * step / steps)
        draw_circle(data, width, height, x, y, thickness, color)


def draw_triangle(data: bytearray, width: int, height: int, points: list[tuple[int, int]], color: Color) -> None:
    min_x = min(x for x, _ in points)
    max_x = max(x for x, _ in points)
    min_y = min(y for _, y in points)
    max_y = max(y for _, y in points)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            inside = False
            j = len(points) - 1
            for i in range(len(points)):
                xi, yi = points[i]
                xj, yj = points[j]
                if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 0.0001) + xi):
                    inside = not inside
                j = i
            if inside:
                set_pixel(data, width, height, x, y, color)


def draw_heart(data: bytearray, width: int, height: int, cx: int, cy: int, scale: float, color: Color) -> None:
    bound = int(scale * 1.5)
    for y in range(cy - bound, cy + bound + 1):
        for x in range(cx - bound, cx + bound + 1):
            nx = (x - cx) / scale
            ny = -(y - cy) / scale
            value = (nx * nx + ny * ny - 1) ** 3 - nx * nx * ny ** 3
            if value <= 0:
                set_pixel(data, width, height, x, y, color)


def save_png(path: Path, width: int, height: int, data: bytearray) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    rows = []
    row_length = width * 4
    for y in range(height):
        rows.append(b"\x00" + bytes(data[y * row_length : (y + 1) * row_length]))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk("IHDR".encode(), struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk("IDAT".encode(), zlib.compress(b"".join(rows), 9))
    png += chunk("IEND".encode(), b"")
    path.write_bytes(png)


def make_logo() -> None:
    w = h = 512
    img = canvas(w, h)
    draw_circle(img, w, h, 256, 256, 220, (46, 184, 240, 255))
    draw_circle(img, w, h, 256, 280, 144, (255, 255, 255, 255))
    draw_triangle(img, w, h, [(132, 150), (198, 68), (218, 202)], (88, 204, 2, 255))
    draw_triangle(img, w, h, [(380, 150), (314, 68), (294, 202)], (255, 200, 61, 255))
    draw_circle(img, w, h, 204, 238, 24, (24, 50, 71, 255))
    draw_circle(img, w, h, 308, 238, 24, (24, 50, 71, 255))
    draw_circle(img, w, h, 213, 229, 8, (255, 255, 255, 255))
    draw_circle(img, w, h, 317, 229, 8, (255, 255, 255, 255))
    draw_ellipse(img, w, h, 256, 294, 42, 30, (255, 123, 110, 255))
    draw_line(img, w, h, 228, 334, 284, 334, 8, (24, 50, 71, 255))
    save_png(OUT / "logo.png", w, h, img)


def make_pet() -> None:
    w = h = 512
    img = canvas(w, h)
    draw_ellipse(img, w, h, 256, 306, 136, 154, (46, 184, 240, 255))
    draw_ellipse(img, w, h, 256, 342, 86, 92, (231, 248, 255, 255))
    draw_triangle(img, w, h, [(134, 160), (202, 66), (222, 218)], (46, 184, 240, 255))
    draw_triangle(img, w, h, [(378, 160), (310, 66), (290, 218)], (46, 184, 240, 255))
    draw_triangle(img, w, h, [(156, 160), (198, 102), (208, 198)], (255, 200, 61, 255))
    draw_triangle(img, w, h, [(356, 160), (314, 102), (304, 198)], (255, 200, 61, 255))
    draw_circle(img, w, h, 204, 254, 28, (24, 50, 71, 255))
    draw_circle(img, w, h, 308, 254, 28, (24, 50, 71, 255))
    draw_circle(img, w, h, 214, 243, 9, (255, 255, 255, 255))
    draw_circle(img, w, h, 318, 243, 9, (255, 255, 255, 255))
    draw_ellipse(img, w, h, 256, 304, 44, 30, (255, 255, 255, 255))
    draw_circle(img, w, h, 256, 292, 12, (24, 50, 71, 255))
    draw_line(img, w, h, 236, 324, 276, 324, 6, (24, 50, 71, 255))
    draw_circle(img, w, h, 168, 315, 22, (255, 123, 110, 160))
    draw_circle(img, w, h, 344, 315, 22, (255, 123, 110, 160))
    draw_ellipse(img, w, h, 174, 448, 48, 22, (28, 138, 197, 255))
    draw_ellipse(img, w, h, 338, 448, 48, 22, (28, 138, 197, 255))
    save_png(OUT / "pet.png", w, h, img)


def make_food() -> None:
    w = h = 256
    img = canvas(w, h)
    draw_line(img, w, h, 92, 164, 176, 84, 18, (255, 237, 204, 255))
    draw_circle(img, w, h, 76, 178, 24, (255, 237, 204, 255))
    draw_circle(img, w, h, 98, 198, 22, (255, 237, 204, 255))
    draw_ellipse(img, w, h, 166, 86, 58, 48, (255, 123, 110, 255))
    draw_ellipse(img, w, h, 182, 82, 34, 26, (255, 169, 111, 255))
    save_png(OUT / "comida.png", w, h, img)


def make_happiness() -> None:
    w = h = 256
    img = canvas(w, h)
    draw_circle(img, w, h, 128, 128, 86, (255, 200, 61, 255))
    draw_circle(img, w, h, 96, 110, 12, (24, 50, 71, 255))
    draw_circle(img, w, h, 160, 110, 12, (24, 50, 71, 255))
    draw_line(img, w, h, 90, 156, 116, 176, 6, (24, 50, 71, 255))
    draw_line(img, w, h, 116, 176, 144, 176, 6, (24, 50, 71, 255))
    draw_line(img, w, h, 144, 176, 170, 156, 6, (24, 50, 71, 255))
    save_png(OUT / "felicidad.png", w, h, img)


def make_sleep() -> None:
    w = h = 256
    img = canvas(w, h)
    draw_circle(img, w, h, 126, 124, 78, (124, 108, 242, 255))
    draw_circle(img, w, h, 158, 104, 78, (246, 251, 255, 255))
    draw_circle(img, w, h, 78, 174, 24, (46, 184, 240, 255))
    draw_circle(img, w, h, 110, 164, 34, (46, 184, 240, 255))
    draw_circle(img, w, h, 146, 174, 24, (46, 184, 240, 255))
    draw_line(img, w, h, 58, 190, 166, 190, 14, (46, 184, 240, 255))
    save_png(OUT / "sueno.png", w, h, img)


def make_life(name: str, color: Color, slash: bool = False) -> None:
    w = h = 256
    img = canvas(w, h)
    draw_heart(img, w, h, 128, 132, 72, color)
    if slash:
        draw_line(img, w, h, 72, 196, 184, 60, 10, (255, 123, 110, 255))
    save_png(OUT / name, w, h, img)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_logo()
    make_pet()
    make_food()
    make_happiness()
    make_sleep()
    make_life("vida.png", (255, 88, 96, 255))
    make_life("vidamenos.png", (198, 209, 218, 255), slash=True)


if __name__ == "__main__":
    main()

def monedero() -> None:
    w = h = 256
    img = canvas(w, h)
    draw_circle(img, w, h, 128, 128, 100, (255, 200, 61, 255))
    draw_circle(img, w, h, 128, 128, 80, (255, 237, 204, 255))
    draw_line(img, w, h, 128 - 40, 128 - 40, 128 + 40, 128 + 40, 10, (24, 50, 71, 255))
    draw_line(img, w, h, 128 - 40, 128 + 40, 128 + 40, 128 - 40, 10, (24, 50, 71, 255))
    save_png(OUT / "monedero.png", w, h, img)

def canjear() -> None:
    w = h = 256
    img = canvas(w, h)
    draw_circle(img, w, h, 128, 128, 100, (46, 184, 240, 255))
    draw_circle(img, w, h, 128, 128, 80, (231, 248, 255, 255))
    draw_line(img, w, h, 128, 128 - 40, 128, 128 + 40, 10, (24, 50, 71, 255))
    save_png(OUT / "canjear.png", w, h, img)
