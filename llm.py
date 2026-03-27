import io
from vlm import *

with open('data/db/memory.db', 'r', encoding='utf-8') as memory_file:
    try:
        openai_history = json.load(memory_file)
    except:
        openai_history = []


def chat_preprocess(msg):  # 聊天预处理
    try:
        if ("屏幕" in msg or "画面" in msg or "图像" in msg or "看到" in msg or "看看" in msg or "看见" in msg
              or "照片" in msg or "摄像头" in msg or "图片" in msg) and img_menu.get() != "关闭图像识别":
            if mode_menu.get() == "角色扮演聊天":
                msg = f"{prompt}。你需要根据其中内容和我聊天。我的问题是：{msg}"
            vlm_mapping = {
                "photo": {"GLM-4V-Flash": glm_4v_photo, "本地Ollama VLM": ollama_vlm_photo,
                          "本地LM Studio": lmstudio_vlm_photo, "本地QwenVL整合包": qwen_vlm_photo,
                          "本地Janus整合包": janus_photo, "自定义API-VLM": custom_vlm_photo},
                "screen": {"GLM-4V-Flash": glm_4v_screen, "本地Ollama VLM": ollama_vlm_screen,
                           "本地LM Studio": lmstudio_vlm_screen, "本地QwenVL整合包": qwen_vlm_screen,
                           "本地Janus整合包": janus_screen, "自定义API-VLM": custom_vlm_screen},
                "cam": {"GLM-4V-Flash": glm_4v_cam, "本地Ollama VLM": ollama_vlm_cam, "本地LM Studio": lmstudio_vlm_cam,
                        "本地QwenVL整合包": qwen_vlm_cam, "本地Janus整合包": janus_cam, "自定义API-VLM": custom_vlm_cam}}
            if "图片" in msg:
                if os.path.exists("data/cache/cache.png"):
                    selected_model = img_menu.get()
                    content = vlm_mapping["photo"][selected_model](msg)
                    notice(f"{mate_name}识别了上传的图片")
                    os.remove("data/cache/cache.png")
                else:
                    content = "请先点击右下方按钮上传图片"
                    notice("请先点击右下方按钮上传图片")
            elif any(keyword in msg for keyword in ["看到", "看见", "看看", "照片", "摄像头"]) and cam_permission == "开启":
                selected_model = img_menu.get()
                content = vlm_mapping["cam"][selected_model](msg)
                notice(f"{mate_name}拍了照片，调用[摄像头识别]")
            else:
                selected_model = img_menu.get()
                content = vlm_mapping["screen"][selected_model](msg)
                notice(f"{mate_name}捕获了屏幕，调用[电脑屏幕识别]")
        elif "画" in msg and prefer_draw != "关闭AI绘画":
            msg = re.sub(r"画|绘画", "", msg)
            content = "正在进行AI绘画"
            notice(f"{mate_name}正在进行AI绘画，请稍等...")
            if prefer_draw == "本地SD API":
                local_sd(msg)
            elif prefer_draw == "本地Janus整合包":
                local_janus(msg)
            elif prefer_draw == "云端CogView-3":
                cloud_cogview(msg)
            elif prefer_draw == "云端Kolors":
                cloud_kolors(msg)
            elif prefer_draw == "云端文心Web":
                content = "绘画完成"
                msg = re.sub(r"画|绘画", "", msg)
                wb.open(f'https://image.baidu.com/front/aigc?tn=aigc&word={msg}')
                notice(f"{mate_name}打开了浏览器，调用[云AI绘画]")
        else:
            if mode_menu.get() == "多智能体助手":
                content = function_llm(f"{prompt}。你是{mate_name}，是专属于我({username})的多智能体助手，支持调用多种智能体，拥有以下功能：{all_task}。", msg)
            elif mode_menu.get() == '伴侣模式':
                content =  chat_llm(msg)
            else:
                content = chat_llm(msg)
            notice(f"收到{mate_name}回复")
        with open('data/db/memory.db', 'w', encoding='utf-8') as f:
            json.dump(openai_history, f, ensure_ascii=False, indent=4)
        return content
    except Exception as e:
        notice(f"图像识别引擎配置错误，错误详情：{e}")
        return "图像识别引擎配置错误"


def chat_llm(msg):  # 大语言模型聊天
    prompt1 = prompt + "/no_think"
    if "几点" in msg or "多少点" in msg or "时间" in msg or "时候" in msg or "日期" in msg or "多少号" in msg or "几号" in msg:
        msg = f"[当前时间:{current_time()}]{msg}"
    try:
        if llm_menu.get() == "GLM-4-Flash":
            client = ZhipuAI(api_key=glm_key)
            openai_history.append({"role": "user", "content": msg})
            messages = [{"role": "system", "content": prompt1}]
            messages.extend(openai_history)
            completion = client.chat.completions.create(model=glm_llm_model, messages=messages)
            openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
            return completion.choices[0].message.content.strip()
        elif llm_menu.get() == "DeepSeek-R1-8B":
            client = OpenAI(base_url=sf_url, api_key=sf_key)
            openai_history.append({"role": "user", "content": msg})
            messages = [{"role": "system", "content": prompt1}]
            messages.extend(openai_history)
            completion = client.chat.completions.create(model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
                                                        messages=messages)
            openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
            res = completion.choices[0].message.content
            if think_filter_switch == "on":
                res = res.split("</think>")[-1].strip()
            return res
        elif llm_menu.get() == "通义千问3-8B":
            client = OpenAI(base_url=sf_url, api_key=sf_key)
            openai_history.append({"role": "user", "content": msg})
            messages = [{"role": "system", "content": prompt1}]
            messages.extend(openai_history)
            completion = client.chat.completions.create(model="Qwen/Qwen3-8B", messages=messages)
            openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
            return completion.choices[0].message.content.strip()
        elif llm_menu.get() == "文心一言Speed":
            client = OpenAI(base_url=bd_url, api_key=bd_key)
            openai_history.append({"role": "user", "content": msg})
            messages = [{"role": "system", "content": prompt1}]
            messages.extend(openai_history)
            completion = client.chat.completions.create(model=bd_model, messages=messages)
            openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
            return completion.choices[0].message.content
        elif llm_menu.get() == "腾讯混元Lite":
            client = OpenAI(base_url=hy_url, api_key=hy_key)
            openai_history.append({"role": "user", "content": msg})
            messages = [{"role": "system", "content": prompt1}]
            messages.extend(openai_history)
            completion = client.chat.completions.create(model=hy_model, messages=messages)
            openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
            return completion.choices[0].message.content
        elif llm_menu.get() == "讯飞星火Lite":
            client = OpenAI(base_url=xf_url, api_key=xf_key)
            openai_history.append({"role": "user", "content": msg})
            messages = [{"role": "system", "content": prompt1}]
            messages.extend(openai_history)
            completion = client.chat.completions.create(model=xf_model, messages=messages)
            openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
            return completion.choices[0].message.content
        elif llm_menu.get() == "本地Transformers":
            try:
                client = OpenAI(base_url=f"http://{local_llm_ip}:{tf_port}/v1", api_key="transformers")
                openai_history.append({"role": "user", "content": msg})
                messages = [{"role": "system", "content": prompt1}]
                messages.extend(openai_history)
                completion = client.chat.completions.create(model=tf_model, messages=messages, stream=False)
                chunks = re.findall(r'^data:\s*(.+)$', completion, flags=re.MULTILINE)
                result_content = []
                for chunk in chunks:
                    try:
                        data = json.loads(chunk)
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content")
                        if content is not None:
                            result_content.append(content)
                    except json.JSONDecodeError:
                        continue
                result_content = "".join(result_content).replace("\n", "")
                openai_history.append({"role": "assistant", "content": result_content})
                res = result_content
                if think_filter_switch == "on":
                    res = res.split("</think>")[-1].strip()
                return res
            except Exception as e:
                return f"本地Transformers服务未开启，错误详情：{e}"
        elif llm_menu.get() == "本地LM Studio":
            try:
                client = OpenAI(base_url=f"http://{local_llm_ip}:{lmstudio_port}/v1", api_key="lm-studio")
                openai_history.append({"role": "user", "content": msg})
                messages = [{"role": "system", "content": prompt1}]
                messages.extend(openai_history)
                completion = client.chat.completions.create(model="", messages=messages)
                openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
                res = completion.choices[0].message.content
                if think_filter_switch == "on":
                    res = res.split("</think>")[-1].strip()
                return res
            except Exception as e:
                return f"本地LM Studio软件API服务未开启，错误详情：{e}"
        elif llm_menu.get() == "本地Ollama LLM":
            try:
                try:
                    rq.get(f'http://{local_llm_ip}:{ollama_port}')
                except:
                    Popen(f"ollama pull {ollama_model_name}", shell=False)
                client = Client(host=f'http://{local_llm_ip}:{ollama_port}')
                openai_history.append({"role": "user", "content": msg})
                messages = [{"role": "system", "content": prompt1}]
                messages.extend(openai_history)
                response = client.chat(model=ollama_model_name, messages=messages)
                openai_history.append({"role": "assistant", "content": response['message']['content']})
                res = response['message']['content']
                if think_filter_switch == "on":
                    res = res.split("</think>")[-1].strip()
                return res
            except Exception as e:
                return f"本地Ollama LLM配置错误，错误详情：{e}"
        elif llm_menu.get() == "Dify聊天助手":
            try:
                res = chat_dify(msg)
                return res
            
            except Exception as e:
                return f"本地Dify聊天助手配置错误，错误详情：{e}"
        elif llm_menu.get() == "AnythingLLM":
            try:
                res = chat_anything_llm(msg)
                return res
            except Exception as e:
                return f"本地AnythingLLM知识库配置错误，错误详情：{e}"
        else:
            try:
                if mode_menu.get() == '伴侣模式':
                    # 配置定义openAi客户端
                    client = OpenAI(base_url=custom_url, api_key=custom_key)
                    # 将用户对话加入到历史记录种
                    openai_history.append({"role": "user", "content": msg})
                    #TODO: 应该要
                    prompt1 = prompt1 + f"""
                    请你记住你当前扮演角色的人物状态:
                    人物当前的位置:{partner_config.get_current_location()},
                    可供参考的人物位置:{partner_config.get_current_location_options}
                    当前对话的时间段:{partner_config.get_current_time_period()}
                    当前人物正在干什么:{partner_config.get_current_action()}
                    可供参考的人物行为:{partner_config.get_current_action_options}
                    当前与用户约定的事:{partner_config.get_agreed_events()[0] if partner_config.get_agreed_events() else "无"}
                    当前对话场景下用户是否在角色的身边:{partner_config.get_is_user_nearby()}
                    请你严格按照如下格式进行回答{partner_config.response_rule}
                    前后回答的逻辑应当连贯
                    回复中提到的所有事物（人、物品、环境细节）必须与当前状态匹配
                    不能突然提及另一个地点的东西，除非明确发生了场景转换
                    场景转换必须通过明确的过渡描述，不能跳跃
                    """
                    # 构造系统提示词
                    messages = [{"role": "system", "content": prompt1}]
                    # 加入历史对话
                    messages.extend(openai_history)
                    # 发送聊天请求
                    completion = client.chat.completions.create(model=custom_model, messages=messages)
                    # 获取llm模型返回消息
                    res_json = completion.choices[0].message.content
                    # 更新人物状态
                    try:
                        # 将模型回答解析为json对象
                        res = json.loads(res_json)
                        # 获取llm返回消息并添加至历史对话记录
                        openai_history.append({"role": "assistant", "content": res['message']})
                        partner_config.set_current_action(res['action'])
                        partner_config.set_current_location(res['location'])
                        partner_config.set_is_user_nearby(res['is_user_nearby'])
                        partner_config.set_current_time_period(res['time_period'])
                        res_message = res['message']
                        # 约定事件管理更新
                        if eval(res['is_completion']):
                            partner_config.take_agreed_event()
                        if eval(res['is_new_event']):
                            partner_config.put_agreed_event(res['new_event'])
                        if think_filter_switch == "on":
                            res_message = res['message'].split("</think>")[-1].strip()
                    #  返回模型回复的消息
                        return res_message
                    # 模型未按指定回复则不对模型回复进行json对象解析
                    except Exception as e:

                        notice('模型未按指定格式回复')
                        res = res_json
                        if think_filter_switch == "on":
                            res = res.split("</think>")[-1].strip()
                        #  返回模型回复的消息
                        return res
                else:
                    client = OpenAI(base_url=custom_url, api_key=custom_key)
                    openai_history.append({"role": "user", "content": msg})
                    messages = [{"role": "system", "content": prompt1}]
                    messages.extend(openai_history)
                    completion = client.chat.completions.create(model=custom_model, messages=messages)
                    openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
                    res = completion.choices[0].message.content
                    if think_filter_switch == "on":
                        res = res.split("</think>")[-1].strip()
                return res.strip()
            except Exception as e:
                return f"自定义API配置错误，错误详情：{e}"
    except:
        return f"{llm_menu.get()}服务未正确设置，请前往软件设置→云端AI Key设置"


# open_source_project_address:https://github.com/MewCo-AI/ai_virtual_mate_comm
def chat_dify(msg):  # Dify聊天助手
    headers = {"Authorization": f"Bearer {dify_key}", "Content-Type": "application/json"}
    data = {"query": msg, "inputs": {}, "response_mode": "blocking", "user": username, "conversation_id": None}
    res = rq.post(f"http://{dify_ip}/v1/chat-messages", headers=headers, data=json.dumps(data))
    res = res.json()['answer'].strip()
    if think_filter_switch == "on":
        res = res.split("</think>")[-1].strip()
    return res


def chat_anything_llm(msg):  # AnythingLLM知识库
    url = f"http://{local_llm_ip}:3001/api/v1/workspace/{anything_llm_ws}/chat"
    headers = {"Authorization": f"Bearer {anything_llm_key}", "Content-Type": "application/json"}
    data = {"message": msg}
    res = rq.post(url, json=data, headers=headers)
    res = res.json().get("textResponse")
    if think_filter_switch == "on":
        res = res.split("</think>")[-1].strip()
    return res


def clear_chat():  # 删除聊天记录
    global openai_history
    if messagebox.askokcancel(f"清除{mate_name}的聊天记录",
                              f"您确定要清除{mate_name}的聊天记录吗？\n如有需要可先点击🔼导出记录再开启新对话\n(该操作不影响伙伴记忆，\n如果想删除记忆可右键聊天框)"):
        output_box.delete("1.0", "end")
        notice("聊天记录已清空")


def local_sd(msg):  # 本地Stable Diffusion
    def local_sd_th():
        try:
            sd_prompt = function_llm("你是一个专业且高水平的Stable Diffusion AI绘画提示词生成器，擅长把我的自然语言转换成Stable Diffusion AI绘画英文提示词。回答只需输出AI绘画英文提示词，提示词由英文单词组成，用英文逗号隔开，不要输出其他内容。",
                                     f"请你根据我的下述需求生成AI绘画提示词，提示词由英文单词组成，用英文逗号隔开，不要输出其他内容：{msg}")
            payload = {"prompt": sd_prompt, "steps": 20}
            res = rq.post(f"http://{local_draw_ip}:{sd_port}/sdapi/v1/txt2img", json=payload)
            data = res.json()
            sd_draw_path = "data/cache/draw/sd_aigc.png"
            with open(sd_draw_path, 'wb') as f:
                f.write(b64decode(data['images'][0]))
            notice("绘画完成")
            draw_box("Stable Diffusion", "sd_aigc")
        except Exception as e:
            notice(f"本地SD AI绘画出错，错误详情：{e}")

    Thread(target=local_sd_th).start()


def local_janus(msg):  # 本地Janus
    def local_janus_th():
        try:
            janus_prompt = function_llm("你是一个专业且高水平的翻译官，擅长把我的语言翻译成英文。回答只需输出翻译成英文的结果，不要输出其他内容。",
                                        f"把下列内容翻译成英文，回答只需输出翻译成英文的结果：{msg}")
            data = {'prompt': janus_prompt, 'seed': None, 'guidance': 5}
            response = rq.post(f"http://{local_draw_ip}:8082/generate_images/", data=data, stream=True)
            buffer = io.BytesIO()
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    buffer.write(chunk)
            buffer.seek(0)
            image = Image.open(buffer)
            janus_draw_path = "data/cache/draw/janus_aigc.png"
            image.save(janus_draw_path)
            notice("绘画完成")
            draw_box("Janus", "janus_aigc")
        except Exception as e:
            notice(f"本地Janus AI绘画出错，错误详情：{e}")

    Thread(target=local_janus_th).start()


def cloud_cogview(msg):  # 云端CogView
    def cloud_cogview_th():
        try:
            client = ZhipuAI(api_key=glm_key)
            res = client.images.generations(model="cogview-3-flash", prompt=msg)
            image_response = rq.get(res.data[0].url)
            cogview_draw_path = "data/cache/draw/cogview_aigc.png"
            with open(cogview_draw_path, "wb") as f:
                f.write(image_response.content)
            notice("绘画完成")
            draw_box("CogView", "cogview_aigc")
        except:
            notice("云端Cogview绘画未正确配置，请前往软件设置→云端AI Key设置GLM智谱BigModel开放平台key")

    Thread(target=cloud_cogview_th).start()


def cloud_kolors(msg):  # 云端Kolors
    def cloud_kolors_th():
        try:
            url = f"{sf_url}/images/generations"
            payload = {"model": "Kwai-Kolors/Kolors", "prompt": msg}
            headers = {"Authorization": f"Bearer {sf_key}", "Content-Type": "application/json"}
            res = rq.request("POST", url, json=payload, headers=headers)
            image_response = rq.get(res.json()["images"][0]["url"])
            kolors_draw_path = "data/cache/draw/kolors_aigc.png"
            with open(kolors_draw_path, "wb") as f:
                f.write(image_response.content)
            notice("绘画完成")
            draw_box("Kolors", "kolors_aigc")
        except:
            notice("云端Kolors绘画未正确配置，请前往软件设置→云端AI Key设置SiliconCloud硅基流动平台key")

    Thread(target=cloud_kolors_th).start()
