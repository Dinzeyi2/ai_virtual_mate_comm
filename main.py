from main_sub import common_chat, run_ase_rp, run_ase_agent
from live2d import run_live2d
from mmd import run_mmd
from vrm import *


def refresh_preference():  # 刷新用户偏好
    while True:
        try:
            new_preference = {"语音识别模式": asr_menu.get(), "对话语言模型": llm_menu.get(),
                              "语音合成引擎": tts_menu.get(), "图像识别引擎": img_menu.get(),
                              "主动感知对话": ase_menu.get(), "运行模式切换": mode_menu.get()}
            with open('data/db/preference.json', 'w', encoding='utf-8') as f:
                json.dump(new_preference, f, ensure_ascii=False, indent=4)
            with open(f'data/db/history.db', 'w', encoding='utf-8') as f:
                f.write(output_box.get(1.0, "end").strip() + "\n")
        except:
            print("用户偏好保存错误")
        time.sleep(0.1)


def text_chat(event=None):  # 打字发送
    def text_chat_th():
        stop_tts()
        msg = input_box.get("1.0", "end").strip()
        if asr_menu.get() == "实时语音识别" and tts_menu.get() != "关闭语音合成":
            messagebox.showinfo("提示", "请关闭实时语音识别或关闭语音合成后\n再打字发送")
            return
        if msg == "":
            messagebox.showinfo("提示", "请输入内容后再发送")
            return
        input_box.delete("1.0", "end")
        common_chat(msg)

    Thread(target=text_chat_th).start()


def sense_voice_th():  # 语音识别(普通模式)
    from asr import recognize_audio, record_audio
    while True:
        try:
            if asr_menu.get() == "实时语音识别" or asr_menu.get() == "自定义唤醒词":
                pg.mixer.init()
                if pg.mixer.music.get_busy():
                    time.sleep(0.1)
                else:
                    say_text = recognize_audio(record_audio())
                    if len(say_text) > 1 and asr_menu.get() == "实时语音识别":
                        common_chat(say_text)
                    elif wake_word in say_text and asr_menu.get() == "自定义唤醒词":
                        if len(say_text) > 2:
                            say_text = say_text.replace(wake_word + "，", "").replace(wake_word, "")
                        common_chat(say_text)
            else:
                time.sleep(0.1)
        except:
            time.sleep(0.1)


def sense_voice_th_break():  # 语音识别(实时语音打断模式)
    from asr import recognize_audio, record_audio
    while True:
        try:
            if asr_menu.get() == "实时语音识别" or asr_menu.get() == "自定义唤醒词":
                say_text = recognize_audio(record_audio())
                if len(say_text) > 1 and asr_menu.get() == "实时语音识别":
                    stop_tts()
                    common_chat(say_text)
                elif wake_word in say_text and asr_menu.get() == "自定义唤醒词":
                    if len(say_text) > 2:
                        say_text = say_text.replace(wake_word + "，", "").replace(wake_word, "")
                    stop_tts()
                    common_chat(say_text)
            else:
                time.sleep(0.1)
        except:
            time.sleep(0.1)


# open_source_project_address:https://github.com/MewCo-AI/ai_virtual_mate_comm
def switch_voice(event=None):  # 切换语音模式
    if asr_menu.get() == "实时语音识别":
        voice_var.set("关闭语音识别")
    elif asr_menu.get() == "关闭语音识别":
        voice_var.set("实时语音识别")


if chat_web_switch == "开启":
    Thread(target=run_chatweb).start()
if voice_break == "开启":
    Thread(target=sense_voice_th_break).start()
else:
    Thread(target=sense_voice_th).start()
Thread(target=run_live2d).start()
Thread(target=run_mmd).start()
Thread(target=run_vrm).start()
Thread(target=refresh_preference).start()
Thread(target=run_ase_rp).start()
Thread(target=run_ase_agent).start()
input_box.bind('<Return>', text_chat)
kb.add_hotkey('alt+g', stop_tts)
try:
    kb.add_hotkey(f'alt+{voice_key}', switch_voice)
except:
    print("语音模式切换按键设置错误")
wydh_icon = Image.open("data/image/ui/wydh.png")
wydh_icon = wydh_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
wydh_icon = ImageTk.PhotoImage(wydh_icon)
Button(root, image=wydh_icon, command=open_chatweb, borderwidth=0, highlightthickness=0).place(relx=0.18, rely=0.02)
vrmjs_icon = Image.open("data/image/ui/vrmjs.png")
vrmjs_icon = vrmjs_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
vrmjs_icon = ImageTk.PhotoImage(vrmjs_icon)
Button(root, image=vrmjs_icon, command=lambda: wb.open(f"http://127.0.0.1:{vrm_port}"), borderwidth=0,
       highlightthickness=0).place(relx=0.27, rely=0.02)
mmdjs_icon = Image.open("data/image/ui/mmdjs.png")
mmdjs_icon = mmdjs_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
mmdjs_icon = ImageTk.PhotoImage(mmdjs_icon)
Button(root, image=mmdjs_icon, command=lambda: wb.open(f"http://127.0.0.1:{mmd_port}"), borderwidth=0,
       highlightthickness=0).place(relx=0.36, rely=0.02)
mmddz_icon = Image.open("data/image/ui/mmddz.png")
mmddz_icon = mmddz_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
mmddz_icon = ImageTk.PhotoImage(mmddz_icon)
Button(root, image=mmddz_icon, command=open_vmd_music, borderwidth=0, highlightthickness=0).place(relx=0.45, rely=0.02)
live2djs_icon = Image.open("data/image/ui/live2djs.png")
live2djs_icon = live2djs_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
live2djs_icon = ImageTk.PhotoImage(live2djs_icon)
Button(root, image=live2djs_icon, command=lambda: wb.open(f"http://127.0.0.1:{live2d_port}"), borderwidth=0,
       highlightthickness=0).place(relx=0.54, rely=0.02)
l2dzc_icon = Image.open("data/image/ui/l2dzc.png")
l2dzc_icon = l2dzc_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
l2dzc_icon = ImageTk.PhotoImage(l2dzc_icon)
Button(root, image=l2dzc_icon, command=open_pet, borderwidth=0, highlightthickness=0).place(relx=0.63, rely=0.02)
zygl_icon = Image.open("data/image/ui/zygl.png")
zygl_icon = zygl_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
zygl_icon = ImageTk.PhotoImage(zygl_icon)
Button(root, image=zygl_icon, command=open_change_w, borderwidth=0, highlightthickness=0).place(relx=0.72, rely=0.02)
rjsz_icon = Image.open("data/image/ui/rjsz.png")
rjsz_icon = rjsz_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
rjsz_icon = ImageTk.PhotoImage(rjsz_icon)
Button(root, image=rjsz_icon, command=open_setting_w, borderwidth=0, highlightthickness=0).place(relx=0.81, rely=0.02)
tzbf_icon = Image.open("data/image/ui/tzbf.png")
tzbf_icon = tzbf_icon.resize((int(100 * scaling_factor), int(23 * scaling_factor)), Image.Resampling.LANCZOS)
tzbf_icon = ImageTk.PhotoImage(tzbf_icon)
Button(root, image=tzbf_icon, command=stop_tts, borderwidth=0, highlightthickness=0).place(relx=0.9, rely=0.02)
upphoto_icon = Image.open("data/image/ui/upphoto.png")
upphoto_icon = upphoto_icon.resize((int(25 * scaling_factor), int(25 * scaling_factor)), Image.Resampling.LANCZOS)
upphoto_icon = ImageTk.PhotoImage(upphoto_icon)
Button(root, image=upphoto_icon, command=up_photo, borderwidth=0, highlightthickness=0).place(relx=0.97, rely=0.825)
export_icon = Image.open("data/image/ui/export.png")
export_icon = export_icon.resize((int(25 * scaling_factor), int(25 * scaling_factor)), Image.Resampling.LANCZOS)
export_icon = ImageTk.PhotoImage(export_icon)
Button(root, image=export_icon, command=export_chat, borderwidth=0, highlightthickness=0).place(relx=0.97, rely=0.865)
add_icon = Image.open("data/image/ui/add.png")
add_icon = add_icon.resize((int(25 * scaling_factor), int(25 * scaling_factor)), Image.Resampling.LANCZOS)
add_icon = ImageTk.PhotoImage(add_icon)
Button(root, image=add_icon, command=clear_chat, borderwidth=0, highlightthickness=0).place(relx=0.97, rely=0.905)
send_icon = Image.open("data/image/ui/send.png")
send_icon = send_icon.resize((int(25 * scaling_factor), int(25 * scaling_factor)), Image.Resampling.LANCZOS)
send_icon = ImageTk.PhotoImage(send_icon)
Button(root, image=send_icon, command=text_chat, borderwidth=0, highlightthickness=0).place(relx=0.97, rely=0.945)
Button(root, text="📱手机网页访问", command=open_web_tips, borderwidth=0, highlightthickness=0).place(relx=0.02,
                                                                                                     rely=0.13)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
os.kill(os.getpid(), 15)
