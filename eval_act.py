"""Simple evaluation script for ACT policy on a real SO-101 robot."""

import time

import cv2
import torch

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig  # noqa: F401
from lerobot.configs.parser import wrap
from lerobot.policies.act.configuration_act import ACTConfig
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors
from lerobot.processor.factory import (
    make_default_robot_action_processor,
    make_default_robot_observation_processor,
)
from lerobot.robots.so_follower.config_so_follower import SO101FollowerConfig
from lerobot.robots.utils import make_robot_from_config
from lerobot.datasets.utils import build_dataset_frame, hw_to_dataset_features

from dataclasses import dataclass, field


@dataclass
class EvalConfig:
    policy: ACTConfig = field(default_factory=ACTConfig)
    robot: SO101FollowerConfig = field(default_factory=SO101FollowerConfig)
    fps: int = 30
    duration: int = 120
    device: str | None = None

    @classmethod
    def __get_path_fields__(cls) -> list[str]:
        return ["policy"]


@wrap()
def eval_act(cfg: EvalConfig):
    # Determine device
    if cfg.device:
        device = cfg.device
    elif torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    print(f"Using device: {device}")

    # Load policy
    pretrained_path = cfg.policy.pretrained_path
    print(f"Loading policy from {pretrained_path}...")
    policy = ACTPolicy.from_pretrained(pretrained_path)
    policy = policy.to(device)
    policy.eval()
    print("Policy loaded!")

    # Load preprocessor/postprocessor
    preprocessor, postprocessor = make_pre_post_processors(
        policy_cfg=cfg.policy,
        pretrained_path=pretrained_path,
        dataset_stats=None,
        preprocessor_overrides={"device_processor": {"device": device}},
    )

    # Create robot
    print(f"Connecting to robot on {cfg.robot.port}...")
    robot = make_robot_from_config(cfg.robot)
    robot.connect()
    print("Robot connected!")

    obs_processor = make_default_robot_observation_processor()
    action_processor = make_default_robot_action_processor()

    dataset_features = hw_to_dataset_features(robot.observation_features, "observation")

    action_interval = 1.0 / cfg.fps
    action_count = 0
    chunk_size = policy.config.chunk_size

    print(f"Running for {cfg.duration}s at {cfg.fps} FPS (chunk_size={chunk_size})")
    print("Press Ctrl+C to stop\n")

    start_time = time.time()
    try:
        while (time.time() - start_time) < cfg.duration:
            step_start = time.perf_counter()

            # Get observation
            obs = robot.get_observation()
            # Resize images to match model expectations (640x480) if needed
            for key in obs:
                if hasattr(obs[key], 'shape') and len(obs[key].shape) == 3 and 'image' in key:
                    h, w = obs[key].shape[:2]
                    if h != 480 or w != 640:
                        obs[key] = cv2.resize(obs[key], (640, 480))
            obs_processed = obs_processor(obs)

            obs_dict = build_dataset_frame(dataset_features, obs_processed, prefix="observation")

            for name in obs_dict:
                obs_dict[name] = torch.from_numpy(obs_dict[name])
                if "image" in name:
                    obs_dict[name] = obs_dict[name].float() / 255.0
                    obs_dict[name] = obs_dict[name].permute(2, 0, 1).contiguous()
                obs_dict[name] = obs_dict[name].unsqueeze(0).to(device)

            # select_action returns a single action (1, action_dim);
            # the policy internally manages its own action chunk buffer
            with torch.no_grad():
                preprocessed = preprocessor(obs_dict)
                action = policy.select_action(preprocessed)
                action = postprocessor(action)

            action = action.squeeze(0).cpu()
            action_dict = {key: action[i].item() for i, key in enumerate(robot.action_features)}
            action_out = action_processor((action_dict, None))
            robot.send_action(action_out)

            action_count += 1

            # Timing
            dt = time.perf_counter() - step_start
            sleep_time = max(0, action_interval - dt)
            time.sleep(sleep_time)

            if action_count % 30 == 0:
                elapsed = time.time() - start_time
                print(f"  [{elapsed:.0f}s] actions: {action_count}")

    except KeyboardInterrupt:
        print("\nStopped by user")

    robot.disconnect()
    elapsed = time.time() - start_time
    print(f"\nDone! Executed {action_count} actions in {elapsed:.1f}s ({action_count/elapsed:.1f} Hz)")


if __name__ == "__main__":
    eval_act()
