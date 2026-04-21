import websocket
import json
import uuid
import requests


# ComfyUI 服务器地址常量
DEFAULT_SERVER_ADDRESS = "u826849-774757226f50.bjb1.seetacloud.com:8443"


class ComfyUIWebSocketClient:
    def __init__(self, server_address=None):
        self.server_address = server_address or DEFAULT_SERVER_ADDRESS
        self.client_id = str(uuid.uuid4())
        self.ws = None
        self.result = None
        # 在初始化时建立 WebSocket 连接（只用于监听）
        self._create_websocket_connection()

    def _create_websocket_connection(self):
        """创建 WebSocket 连接（用于监听进度）"""
        ws_url = f"wss://{self.server_address}/ws?clientId={self.client_id}"
        try:
            self.ws = websocket.create_connection(ws_url)
        except Exception as e:
            raise ConnectionError(f"与 ComfyUI 服务器建立 WebSocket 连接失败：{e}")

    def _is_websocket_available(self):
        """检查 WebSocket 连接是否可用"""
        if self.ws is None:
            return False
        try:
            self.ws.ping()
            return True
        except:
            return False

    def queue_prompt(self, workflow, prompt_id=None):
        """
        通过 HTTP POST 发送工作流到 ComfyUI（这是正确的方式！）
        ComfyUI 的 /prompt 端点接收任务
        """
        if prompt_id is None:
            prompt_id = str(uuid.uuid4())

        # 使用 HTTP POST 到 /prompt 端点
        prompt_data = {
            "prompt": workflow,
            "client_id": self.client_id,
            "prompt_id": prompt_id
        }
        url = f"https://{self.server_address}/prompt"
        response = requests.post(url, json=prompt_data)
        response.raise_for_status()
        return prompt_id

    def wait_for_completion(self, prompt_id):
        """
        通过 WebSocket 等待任务执行完成
        """
        while True:
            message = self.ws.recv()
            data = json.loads(message)

            # 只处理与当前 prompt_id 相关的消息
            msg_prompt_id = data.get("data", {}).get("prompt_id")
            if msg_prompt_id != prompt_id:
                continue

            msg_type = data.get("type")
            msg_data = data.get("data", {})

            if msg_type == "status":
                print(f"状态：{msg_data}")

            elif msg_type == "execution_start":
                print("开始执行")

            elif msg_type == "executing":
                node_id = msg_data.get("node")
                if node_id is None:
                    # node 为 None 表示整个队列执行完成
                    print("执行完成!")
                    break
                print(f"正在执行节点：{node_id}")

            elif msg_type == "progress":
                value = msg_data.get("value")
                max_value = msg_data.get("max")
                print(f"进度：{value}/{max_value}")

            elif msg_type == "executed":
                print(f"节点 {msg_data['node']} 执行完成")

            elif msg_type == "execution_success":
                print("执行成功!")
                break

            elif msg_type == "execution_error":
                raise RuntimeError(f"执行错误：{msg_data.get('exception_message', 'Unknown error')}")

            elif msg_type == "execution_cached":
                print("使用了缓存")

    def close(self):
        """关闭 WebSocket 连接"""
        if self.ws:
            self.ws.close()
            self.ws = None


def generate_image_with_websocket(prompt_text, save_path="comfyuiAPI/output"):
    """
    使用 WebSocket 方式生成图像
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
    print(f"使用随机种子：{random_seed}")

    # 发送工作流（使用 HTTP POST 到 /prompt 端点）
    prompt_id = client.queue_prompt(workflow)
    print(f"Prompt ID: {prompt_id}")

    # 等待执行完成
    client.wait_for_completion(prompt_id)
    print(f"执行完成!")

    # 关闭连接
    client.close()

    return prompt_id


def get_images_by_prompt_id(prompt_id, save_path="comfyuiAPI/output", server_address=None, node_id=None):
    """
    根据 prompt_id 获取生成的图片并保存到本地

    Args:
        prompt_id: ComfyUI 返回的任务 ID
        save_path: 图片保存目录
        server_address: ComfyUI 服务器地址（可选，默认使用常量）
        node_id: 指定节点 ID（可选，如 "8" 表示只获取节点 8 的图片，不指定则获取所有图片）

    Returns:
        保存的图片路径列表
    """
    import os

    os.makedirs(save_path, exist_ok=True)

    server_address = server_address or DEFAULT_SERVER_ADDRESS

    # 1. 通过 API 获取任务历史（包含输出文件名）
    history_url = f"https://{server_address}/api/history/{prompt_id}"
    response = requests.get(history_url)
    history = response.json()

    if prompt_id not in history:
        raise ValueError(f"未找到 prompt_id: {prompt_id}的历史记录")

    output_images = []
    outputs = history[prompt_id].get("outputs", {})

    # 2. 如果指定了 node_id，只获取该节点的图片
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
                    print(f"图片已保存：{local_filename}")
                else:
                    print(f"下载失败：{view_url} - 状态码：{img_response.status_code}")

    return output_images


# 使用示例
if __name__ == "__main__":
    prompt_id = generate_image_with_websocket(r"Ganyu (Genshin Impact), long blue-purple gradient hair, qilin horns, soft and reserved expression, faint blush, eyes slightly averted but secretly looking toward the viewer, gently holding her lover's sleeve (only the fabric edge / hand visible, no face shown), leaning in slightly as if relying on them, close-up half-body portrait, quiet snowy night, Liyue-style eaves and lanterns blurred in the background, thin mist, small snowflakes, calm breathing atmosphere, cinematic lighting, soft moonlight, shallow depth of field, bokeh, delicate hair highlights, smooth detailed skin, high-end anime illustration, ultra detailed, masterpiece, best quality, clean composition, wallpaper")
    print(f"生成完成，Prompt ID: {prompt_id}")

    client = ComfyUIWebSocketClient()
    server_address = client.server_address
    client.close()

    # 根据 prompt_id 获取图片（指定节点 8: SaveImage）
    images = get_images_by_prompt_id(prompt_id, server_address=server_address, node_id="8")
    print(f"获取到 {len(images)} 张图片：{images}")
