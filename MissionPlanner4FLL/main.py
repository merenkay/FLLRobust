import pygame
import sys
import tkinter as tk
from tkinter import filedialog
import json
import math

# Pygame başlatma
pygame.init()

# Sabitler
SCREEN_WIDTH, SCREEN_HEIGHT = 1300, 630
BACKGROUND_COLOR = (255, 255, 255)
POINT_RADIUS = 5

# Pencere ayarları
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FLL Harita İşaretleme")

# Harita resmi yükle ve boyutlandır
map_image = pygame.image.load("map.jpg")
map_image = pygame.transform.scale(map_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Noktalar, çizgiler ve çemberler listesi
points = []
line_color = (0, 0, 255)  # Başlangıç rengi mavi
circles = []  # Çemberler için liste

# Renk seçenekleri (1-9 tuşları için)
colors = {
    pygame.K_1: (0, 0, 0),       # Siyah
    pygame.K_2: (255, 0, 0),     # Kırmızı
    pygame.K_3: (0, 255, 0),     # Yeşil
    pygame.K_4: (0, 0, 255),     # Mavi
    pygame.K_5: (255, 255, 0),   # Sarı
    pygame.K_6: (0, 255, 255),   # Camgöbeği
    pygame.K_7: (255, 0, 255),   # Mor
    pygame.K_8: (255, 165, 0),   # Turuncu
    pygame.K_9: (128, 0, 128),   # Mor ton
}

# Yeni misyon kaydetme
def save_mission(mission_name):
    mission_data = {
        "points": points,
        "line_color": line_color,
        "circles": circles
    }
    with open(f"{mission_name}.json", "w") as file:
        json.dump(mission_data, file)

# Misyon yükleme
def load_mission(mission_name):
    global points, line_color, circles
    with open(f"{mission_name}.json", "r") as file:
        mission_data = json.load(file)
        points = mission_data["points"]
        line_color = tuple(mission_data["line_color"])
        circles = mission_data["circles"]

# Tkinter dosya kaydetme penceresi
def save_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    file_path = filedialog.asksaveasfilename(defaultextension=".json", title="Misyon Kaydet", filetypes=[("JSON Files", "*.json")])
    return file_path

# Tkinter dosya seçme penceresi
def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    file_path = filedialog.askopenfilename(title="Misyon Seç", filetypes=[("JSON Files", "*.json")])
    return file_path

def draw_points_and_lines():
    # Çizgi çizme
    for i in range(len(points) - 1):
        pygame.draw.line(screen, points[i][1], points[i][0], points[i + 1][0], 2)
    
    # Noktaları çizme
    for point, color in points:
        pygame.draw.circle(screen, color, point, POINT_RADIUS)

    # Çemberleri çizme
    for center, radius, color in circles:
        pygame.draw.circle(screen, color, center, radius, 2)

# Shift tuşu ile hizalama yapabilen fonksiyon
def snap_to_grid(mouse_pos, grid_size=15):
    x, y = mouse_pos
    # Dikey, yatay ve 45 derece doğrultusunda en yakın noktayı bul
    angles = [0, 90, 45, -45]  # Yatay, dikey ve 45 derece
    closest_snap = mouse_pos  # Başlangıçta mouse pozisyonu
    min_distance = float('inf')

    for angle in angles:
        if angle == 0:  # Yatay doğrultu
            snapped_pos = (round(x / grid_size) * grid_size, y)
        elif angle == 90:  # Dikey doğrultu
            snapped_pos = (x, round(y / grid_size) * grid_size)
        elif angle == 45:  # 45 derece doğrultu
            snapped_pos = (round(x / grid_size) * grid_size, round(y / grid_size) * grid_size)
        elif angle == -45:  # -45 derece doğrultu
            snapped_pos = (round(x / grid_size) * grid_size, round(y / grid_size) * grid_size)

        # En yakın noktayı bulma
        distance = math.dist(mouse_pos, snapped_pos)
        if distance < min_distance:
            min_distance = distance
            closest_snap = snapped_pos
    
    return closest_snap

def main():
    global line_color, circles
    drawing_circles = False  # Başlangıçta çember çizme kapalı
    circle_start_point = None  # Çemberin başlangıç noktası
    last_point = None  # Son nokta
    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        screen.blit(map_image, (0, 0))  # Haritayı (0,0) noktasına çiz
        
        # Olayları kontrol et
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tıklama ile nokta ekleme
                    if drawing_circles:
                        if circle_start_point is None:  # Çemberin başlangıcı
                            circle_start_point = event.pos
                        else:  # Çemberin bitişi
                            radius = int(math.dist(circle_start_point, event.pos))
                            circles.append((circle_start_point, radius, line_color))
                            drawing_circles = False  # Çember çizimi bitti
                            circle_start_point = None  # Başlangıç noktasını sıfırla
                    else:
                        points.append((event.pos, line_color))
                        last_point = event.pos  # Son noktayı güncelle

                elif event.button == 3:  # Sağ tıklama ile çizimi temizleme
                    points.clear()
                    circles.clear()

            elif event.type == pygame.KEYDOWN:
                # Renk değiştirme tuşları
                if event.key in colors:
                    line_color = colors[event.key]
                # Misyon yükle
                elif event.key == pygame.K_l:
                    file_path = open_file_dialog()  # Dosya seçme penceresini aç
                    if file_path:
                        load_mission(file_path.split("/")[-1].replace(".json", ""))  # Misyonu yükle

                # Misyon kaydetme
                elif event.key == pygame.K_s:
                    file_path = save_file_dialog()  # Dosya kaydetme penceresini aç
                    if file_path:
                        save_mission(file_path.split("/")[-1].replace(".json", ""))  # Misyonu kaydet

                # Çember çizme moduna geçiş
                elif event.key == pygame.K_c:
                    drawing_circles = True  # Çember çizme modunu aç

        # Eğer Shift tuşuna basılıysa hizalamayı yap
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            mouse_pos = pygame.mouse.get_pos()
            snapped_pos = snap_to_grid(mouse_pos)

            # Geçici çizgiyi çiz
            if last_point:
                pygame.draw.line(screen, line_color, last_point, snapped_pos, 2)

        # Çemberin geçici olarak çizilmesi
        if drawing_circles and circle_start_point:
            mouse_pos = pygame.mouse.get_pos()
            radius = int(math.dist(circle_start_point, mouse_pos))
            pygame.draw.circle(screen, line_color, circle_start_point, radius, 2)

        # Noktaları ve çizgileri çiz
        draw_points_and_lines()

        # Ekranı güncelle
        pygame.display.flip()

if __name__ == "__main__":
    main()
