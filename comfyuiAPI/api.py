import websocket
import json
import uuid
import requests
import time

# ComfyUI服务器地址常量
DEFAULT_SERVER_ADDRESS = "u826849-774757226f50.bjb1.seetacloud.com:8443"


class ComfyUIWebSocketClient:
    def __init__(self, server_address=None):
        self.server_address = server_address or DEFAULT_SERVER_ADDRESS
        self.client_id = str(uuid.uuid4())
        self.ws = None
        self.result = None

    def send_prompt(self, workflow):
        """
        通过WebSocket发送工作流
        """
        # 连接WebSocket
        ws_url = f"wss://{self.server_address}/ws?clientId={self.client_id}"
        self.ws = websocket.create_connection(ws_url)

        # 发送POST请求
        prompt_endpoint = f"https://{self.server_address}/api/prompt"
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }

        response = requests.post(
            prompt_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        return response.json()

    def listen_progress(self, prompt_id):
        """
        监听生成进度
        """
        try:
            while True:
                message = self.ws.recv()
                data = json.loads(message)

                # 处理不同类型的消息
                if data["type"] == "status":
                    print(f"状态更新: {data['data']}")

                elif data["type"] == "executing":
                    node_id = data["data"].get("node")
                    print(f"正在执行节点: {node_id}")

                elif data["type"] == "progress":
                    value = data["data"]["value"]
                    max_value = data["data"]["max"]
                    print(f"进度: {value}/{max_value}")

                elif data["type"] == "execution_start":
                    print("开始执行")

                elif data["type"] == "execution_success":
                    print("执行成功!")
                    self.result = data
                    break

                elif data["type"] == "execution_cached":
                    print("使用了缓存")

        except KeyboardInterrupt:
            print("监听中断")
        finally:
            self.ws.close()

def generate_image_with_websocket(prompt_text, save_path="comfyuiAPI/output"):
    """
    使用WebSocket方式生成图像
    """
    import os
    import random
    os.makedirs(save_path, exist_ok=True)

    client = ComfyUIWebSocketClient()

    # 加载并修改工作流
    with open("comfyuiAPI/wrokflows/Test.json", "r", encoding="utf-8") as f:
        workflow = json.load(f)
    # 正向提示词
    workflow["9"]["inputs"]["text"] = prompt_text  # 修改提示词
    # 生成随机种子
    random_seed = random.randint(0, 18446744073709551615)
    workflow["6"]["inputs"]["noise_seed"] = random_seed
    workflow["7"]["inputs"]["seed"] = random_seed
    print(f"使用随机种子: {random_seed}")

    # 发送工作流
    result = client.send_prompt(workflow)
    print(f"API返回结果: {result}")

    if "prompt_id" not in result:
        raise ValueError(f"API返回错误: {result}")

    prompt_id = result["prompt_id"]
    print(f"Prompt ID: {prompt_id}")

    # 监听进度
    client.listen_progress(prompt_id)

    return prompt_id


def get_images_by_prompt_id(prompt_id, save_path="comfyuiAPI/output", server_address=None, node_id=None):
    """
    根据prompt_id获取生成的图片并保存到本地

    Args:
        prompt_id: ComfyUI返回的任务ID
        save_path: 图片保存目录
        server_address: ComfyUI服务器地址（可选，默认使用常量）
        node_id: 指定节点ID（可选，如 "8" 表示只获取节点8的图片，不指定则获取所有图片）

    Returns:
        保存的图片路径列表
    """
    import os

    os.makedirs(save_path, exist_ok=True)

    server_address = server_address or DEFAULT_SERVER_ADDRESS

    # 1. 通过API获取任务历史（包含输出文件名）
    history_url = f"https://{server_address}/api/history/{prompt_id}"
    response = requests.get(history_url)
    history = response.json()

    if prompt_id not in history:
        raise ValueError(f"未找到prompt_id: {prompt_id}的历史记录")

    output_images = []
    outputs = history[prompt_id].get("outputs", {})

    # 2. 如果指定了node_id，只获取该节点的图片
    if node_id is not None:
        if node_id in outputs and "images" in outputs[node_id]:
            node_data = outputs[node_id]
        else:
            print(f"节点 {node_id} 没有图片输出")
            return []
        node_iter = [(node_id, node_data)]
    else:
        # 获取所有节点的图片
        node_iter = outputs.items()

    # 3. 遍历找到的图片并下载
    for nid, node_data in node_iter:
        if "images" in node_data:
            for img_info in node_data["images"]:
                filename = img_info["filename"]
                subfolder = img_info.get("subfolder", "")
                img_type = img_info.get("type", "output")

                # 4. 下载图片
                view_url = f"https://{server_address}/view"
                params = {"filename": filename, "subfolder": subfolder, "type": img_type}

                img_response = requests.get(view_url, params=params)

                if img_response.status_code == 200:
                    # 保存图片
                    local_filename = f"{save_path}/{filename}"
                    with open(local_filename, "wb") as f:
                        f.write(img_response.content)
                    output_images.append(os.path.abspath(local_filename))
                    print(f"图片已保存: {local_filename}")
                else:
                    print(f"下载失败: {view_url} - 状态码: {img_response.status_code}")

    return output_images


# 使用示例
if __name__ == "__main__":
    client = ComfyUIWebSocketClient()
    server_address = client.server_address

    prompt_id = generate_image_with_websocket(r"Ganyu (Genshin Impact), long blue-purple gradient hair, qilin horns, soft and reserved expression, faint blush, eyes slightly averted but secretly looking toward the viewer, gently holding her lover’s sleeve (only the fabric edge / hand visible, no face shown), leaning in slightly as if relying on them, close-up half-body portrait, quiet snowy night, Liyue-style eaves and lanterns blurred in the background, thin mist, small snowflakes, calm breathing atmosphere, cinematic lighting, soft moonlight, shallow depth of field, bokeh, delicate hair highlights, smooth detailed skin, high-end anime illustration, ultra detailed, masterpiece, best quality, clean composition, wallpaper")
    print(f"生成完成, Prompt ID: {prompt_id}")

    # 根据prompt_id获取图片（指定节点8: SaveImage）
    images = get_images_by_prompt_id(prompt_id, server_address=server_address, node_id="8")
    print(f"获取到 {len(images)} 张图片: {images}")
