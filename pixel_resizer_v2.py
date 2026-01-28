import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
from rembg import remove

def toggle_custom_inputs(event=None):
    if size_combobox.get() == "Custom (직접 입력)":
        entry_width.config(state="normal")
        entry_height.config(state="normal")
    else:
        entry_width.config(state="disabled")
        entry_height.config(state="disabled")

def select_and_convert():
    # 1. 크기 값 가져오기
    try:
        selection = size_combobox.get()
        if selection == "Custom (직접 입력)":
            target_w = int(entry_width.get())
            target_h = int(entry_height.get())
        else:
            val = int(selection.split(' ')[0])
            target_w, target_h = val, val
            
        if target_w <= 0 or target_h <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("에러", "크기(X, Y)는 양의 정수만 입력 가능합니다.")
        return

    # 2. 파일 선택
    file_paths = filedialog.askopenfilenames(
        title=f"{target_w}x{target_h} 로 변환할 이미지 선택",
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
    do_remove_bg = remove_bg_var.get()

    # 3. 변환 루프
    for path in file_paths:
        try:
            folder, filename = os.path.split(path)
            print(f"처리 중: {filename}...") # 진행 상황 로그

            with Image.open(path) as img:
                # [순서 변경 핵심]
                # 1. 배경 제거를 가장 먼저 수행 (원본 해상도 이용)
                if do_remove_bg:
                    # AI가 원본 크기에서 사람/사물을 인식하므로 훨씬 정확함
                    img = remove(img)

                # 2. 투명도 처리를 위해 RGBA 변환
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 3. 리사이징 (Nearest Neighbor로 도트 느낌 살리기)
                # 배경이 제거된 깨끗한 이미지를 줄여야 경계선이 깔끔함
                resized_img = img.resize((target_w, target_h), Image.NEAREST)

                # 4. 저장
                name, ext = os.path.splitext(filename)
                
                # 배경을 지웠으면 무조건 png로 저장
                save_ext = ".png" if do_remove_bg else ext
                suffix = "_noBG" if do_remove_bg else ""
                
                new_filename = f"{name}{suffix}_{target_w}x{target_h}{save_ext}"
                save_path = os.path.join(folder, new_filename)

                resized_img.save(save_path)
                success_count += 1

        except Exception as e:
            print(f"Skipped {path}: {e}")

    messagebox.showinfo("완료", f"총 {success_count}개의 이미지를 변환했습니다.")

# --- GUI 설정 ---
root = tk.Tk()
root.title("Pixel Resizer")
root.geometry("350x280")
root.eval('tk::PlaceWindow . center')

# 상단 라벨
label_size = tk.Label(root, text="크기 프리셋:")
label_size.pack(pady=(15, 2))

# 드롭다운
size_options = ["128 x 128", "256 x 256", "512 x 512", "1024 x 1024", "2048 x 2048", "Custom (직접 입력)"]
size_combobox = ttk.Combobox(root, values=size_options, state="readonly")
size_combobox.current(0)
size_combobox.pack(pady=5)
size_combobox.bind("<<ComboboxSelected>>", toggle_custom_inputs)

# 직접 입력창
frame_custom = tk.Frame(root)
frame_custom.pack(pady=5)

tk.Label(frame_custom, text="X:").pack(side="left", padx=5)
entry_width = tk.Entry(frame_custom, width=6, state="disabled")
entry_width.pack(side="left")

tk.Label(frame_custom, text="Y:").pack(side="left", padx=5)
entry_height = tk.Entry(frame_custom, width=6, state="disabled")
entry_height.pack(side="left")

# 배경 제거 옵션
remove_bg_var = tk.BooleanVar()
chk = tk.Checkbutton(root, text="배경 자동 제거 (AI) - 원본 품질 유지", variable=remove_bg_var)
chk.pack(pady=10)

# 실행 버튼
btn = tk.Button(root, text="이미지 선택 및 변환", command=select_and_convert, height=2)
btn.pack(pady=10, fill='x', padx=20)

root.mainloop()