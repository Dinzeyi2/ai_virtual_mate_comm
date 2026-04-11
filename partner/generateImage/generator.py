"""
伴侣模式文生图生成器
职责：调用 ComfyUI API 生成图像，返回图片路径
"""

import sys
import os

# 添加项目根目录到路径，以便导入 comfyuiAPI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from comfyuiAPI.api import generate_image_with_websocket, get_images_by_prompt_id


def build_image_prompt(prompt_dict):
    """
    将 LLM 返回的 prompt 字典组合成完整的文生图提示词

    Args:
        prompt_dict: 包含 scene, emotion, action, focus, lighting, camera 字段的字典

    Returns:
        组合后的英文提示词字符串
    """
    if not prompt_dict:
        return None

    # 按顺序组合各个字段
    parts = []

    # scene - 场景描述
    if prompt_dict.get('scene'):
        parts.append(prompt_dict['scene'])

    # emotion - 情绪表情
    if prompt_dict.get('emotion'):
        parts.append(prompt_dict['emotion'])
        
    # focus - 核心焦点
    if prompt_dict.get('focus'):
        parts.append(prompt_dict['focus'])

    # lighting - 光线
    if prompt_dict.get('lighting'):
        parts.append(prompt_dict['lighting'])

    # camera - 镜头构图
    if prompt_dict.get('camera'):
        parts.append(prompt_dict['camera'])

    # 用逗号连接所有部分
    return ", ".join(parts)


def generate_companion_image(prompt_dict, save_path=None):
    """
    伴侣模式专用文生图接口

    Args:
        prompt_dict: LLM 返回的 prompt 字段（字典格式），包含：
            - scene: 场景描述
            - emotion: 情绪表情
            - action: 动作行为
            - focus: 核心焦点
            - lighting: 光线描述
            - camera: 镜头构图
        save_path: 图片保存路径（可选，默认为模块 output 目录）

    Returns:
        生成的图片本地路径 (str)，生成失败返回 None
    """
    if save_path is None:
        save_path = os.path.join(os.path.dirname(__file__), "output")

    # 确保保存目录存在
    os.makedirs(save_path, exist_ok=True)

    try:
        # 组合提示词
        full_prompt = build_image_prompt(prompt_dict)
        if not full_prompt:
            print("[generateImage] 提示词为空，跳过生成")
            return None

        print(f"[generateImage] 开始生成图像，提示词：{full_prompt}")

        # 调用 ComfyUI API 生成图像
        prompt_id = generate_image_with_websocket(full_prompt, save_path)
        print(f"[generateImage] Prompt ID: {prompt_id}")

        # 根据 prompt_id 获取生成的图片
        images = get_images_by_prompt_id(prompt_id, save_path)

        if images and len(images) > 0:
            print(f"[generateImage] 图像生成成功：{images[0]}")
            return images[0]
        else:
            print("[generateImage] 未获取到生成的图像")
            return None

    except Exception as e:
        print(f"[generateImage] 图像生成失败：{e}")
        return None
