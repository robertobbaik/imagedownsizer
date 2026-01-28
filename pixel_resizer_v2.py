import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
from rembg import remove  # 핵심 라이브러리

def select_and_convert():
    try:
        selected_text = size_combobox.get()
        target_size = int(selected_text.split(' ')[0])
    except ValueError:
        messagebox.showerror("에러", "크기를 올바르게 선택해주세요.")
        return

    file_paths = filedialog.askopenfilenames(
        title=f"{target_size}px로 변환할 이미지 선택",
        filetypes=[
            ("All Images", "*.png *.jpg *.jpeg *.bmp"), 
            ("PNG Files", "*.png"),
            ("JPEG Files", "*.jpg *.jpeg"),
            ("All Files", "*.*")
        ]
    )

    if not file_paths:
        return

    success_count = 0
    
    # 체크박스 상태 확인 (1이면 켜짐)
    do_remove_bg = remove_bg_var.get()

    for path in file_paths:
        try:
            with Image.open(path) as img:
                # 1. 배경 제거 (체크되었을 경우)
                # 리사이징 전에 해야 원본 해상도 기반으로 정교하게 따짐
                if do_remove_bg:
                    img = remove(img)

                # 2. RGBA 모드 확인 (투명도 보존)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 3. Nearest Neighbor 리사이징
                resized_img = img.resize((target_size, target_size), Image.NEAREST)

                # 저장
                folder, filename = os.path.split(path)
                name, ext = os.path.splitext(filename)
                
                # 배경 지웠으면 무조건 png로 저장해야 투명도 유지됨
                save_ext = ".png" if do_remove_bg else ext
                suffix = "_noBG" if do_remove_bg else ""
                
                new_filename = f"{name}{suffix}_{target_size}{save_ext}"
                save_path = os.path.join(folder, new_filename)

                resized_img.save(save_path)
                success_count += 1
        except Exception as e:
            print(f"Skipped {path}: {e}")

    messagebox.showinfo("완료", f"총 {success_count}개의 이미지를 변환했습니다.")

# --- GUI 설정 ---
root = tk.Tk()
root.title("Pixel Resizer")
root.geometry("300x200") # 체크박스 때문에 세로 길이 조금 늘림
root.eval('tk::PlaceWindow . center')

label = tk.Label(root, text="변환할 크기 선택 (2의 보수):")
label.pack(pady=(15, 5))

size_options = ["128 x 128", "256 x 256", "512 x 512", "1024 x 1024", "2048 x 2048"]
size_combobox = ttk.Combobox(root, values=size_options, state="readonly")
size_combobox.current(0)
size_combobox.pack(pady=5)

# [추가됨] 배경 제거 체크박스
remove_bg_var = tk.BooleanVar()
chk = tk.Checkbutton(root, text="배경 자동 제거 (AI)", variable=remove_bg_var)
chk.pack(pady=5)

btn = tk.Button(root, text="이미지 선택 및 변환", command=select_and_convert, height=2)
btn.pack(pady=10, fill='x', padx=20)

root.mainloop()