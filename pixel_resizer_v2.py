import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
from rembg import remove

# --- 로직 부분 (이전과 동일) ---
def toggle_custom_inputs(event=None):
    if size_combobox.get() == "Custom (직접 입력)":
        entry_width.config(state="normal")
        entry_height.config(state="normal")
    else:
        entry_width.config(state="disabled")
        entry_height.config(state="disabled")

def select_and_convert():
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

    for path in file_paths:
        try:
            folder, filename = os.path.split(path)
            print(f"처리 중: {filename}...")

            with Image.open(path) as img:
                # 1. 배경 제거 (원본 크기에서 수행)
                if do_remove_bg:
                    img = remove(img)

                # 2. RGBA 변환
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 3. 리사이징 (Nearest Neighbor)
                resized_img = img.resize((target_w, target_h), Image.NEAREST)

                # 4. 저장
                name, ext = os.path.splitext(filename)
                save_ext = ".png" if do_remove_bg else ext
                suffix = "_noBG" if do_remove_bg else ""
                new_filename = f"{name}{suffix}_{target_w}x{target_h}{save_ext}"
                save_path = os.path.join(folder, new_filename)

                resized_img.save(save_path)
                success_count += 1

        except Exception as e:
            print(f"Skipped {path}: {e}")

    messagebox.showinfo("완료", f"총 {success_count}개의 이미지를 변환했습니다.")

# --- GUI 설정 (여기가 핵심 수정됨) ---
root = tk.Tk()
root.title("Pixel Resizer")
# 창 크기를 조금 더 키워서 여유를 줌
root.geometry("380x350") 
root.eval('tk::PlaceWindow . center')

# [스타일 설정] 드롭다운 폰트를 키워서 클릭 영역 확보
style = ttk.Style()
style.theme_use('clam') # 좀 더 깔끔한 테마
style.configure("TCombobox", padding=5, font=("Helvetica", 11)) 

# 상단 라벨
label_size = tk.Label(root, text="크기 프리셋:", font=("Helvetica", 12, "bold"))
label_size.pack(pady=(20, 5))

# 드롭다운 (Combobox) - 위아래 간격(pady)을 넓힘
size_options = ["128 x 128", "256 x 256", "512 x 512", "1024 x 1024", "2048 x 2048", "Custom (직접 입력)"]
size_combobox = ttk.Combobox(root, values=size_options, state="readonly", font=("Helvetica", 11), width=25)
size_combobox.current(0)
# pady=(위, 아래) 간격을 줘서 시원하게 배치
size_combobox.pack(pady=(0, 15)) 
size_combobox.bind("<<ComboboxSelected>>", toggle_custom_inputs)

# 직접 입력창 프레임
frame_custom = tk.Frame(root)
frame_custom.pack(pady=5)

tk.Label(frame_custom, text="X:", font=("Helvetica", 10)).pack(side="left", padx=5)
entry_width = tk.Entry(frame_custom, width=8, state="disabled", font=("Helvetica", 10))
entry_width.pack(side="left")

tk.Label(frame_custom, text="Y:", font=("Helvetica", 10)).pack(side="left", padx=5)
entry_height = tk.Entry(frame_custom, width=8, state="disabled", font=("Helvetica", 10))
entry_height.pack(side="left")

# 배경 제거 옵션 체크박스 - 간격 넓힘
remove_bg_var = tk.BooleanVar()
chk = tk.Checkbutton(root, text="배경 자동 제거 (AI)", variable=remove_bg_var, font=("Helvetica", 10))
chk.pack(pady=15)

# [핵심] 실행 버튼 크기 키우기
# height=2 는 글자 줄 수이고, ipady=8 은 내부 여백(padding)을 강제로 늘림
# 이렇게 해야 버튼 자체가 뚱뚱해져서 클릭이 잘 됨
btn = tk.Button(root, text="이미지 선택 및 변환", command=select_and_convert, 
                height=2, font=("Helvetica", 13, "bold"), bg="#e1e1e1")
# ipady=8 추가, pady 간격 넓힘
btn.pack(pady=(5, 25), fill='x', padx=30, ipady=8)

root.mainloop()