# SO101 Local Guide (Leader + Follower)

This guide stitches together the key SO101 steps and commands in one place for
local use. It is derived from the docs in `docs/source/` and the SO101 code in
`src/lerobot/`. For full detail (videos, full assembly steps), use the linked
sources below.

Primary sources:
- `docs/source/so101.mdx`
- `docs/source/installation.mdx`
- `docs/source/il_robots.mdx`
- `docs/source/phone_teleop.mdx`
- `docs/source/hilserl.mdx`

## 1) Parts and assembly overview

- Parts list + 3D prints: https://github.com/TheRobotStudio/SO-ARM100
- Follower: 6x STS3215 motors at 1/345 gearing.
- Leader: mixed gearing to be lighter to move by hand.

Leader motor gear ratios:

| Joint (Leader)          | Motor | Gear Ratio |
| ----------------------- | :---: | :--------: |
| Base / Shoulder Pan     |   1   |  1 / 191   |
| Shoulder Lift           |   2   |  1 / 345   |
| Elbow Flex              |   3   |  1 / 191   |
| Wrist Flex              |   4   |  1 / 147   |
| Wrist Roll              |   5   |  1 / 147   |
| Gripper                 |   6   |  1 / 147   |

Full assembly steps and videos are in `docs/source/so101.mdx`.

## 2) Install LeRobot + Feetech SDK

From the repo root:

```bash
pip install -e ".[feetech]"
```

This installs LeRobot and the Feetech SDK required by SO100/SO101.

## 3) Find the USB ports for each arm

Connect a controller board (MotorBus) and run:

```bash
lerobot-find-port
```

On Linux, you may need:

```bash
sudo chmod 666 /dev/ttyACM0
sudo chmod 666 /dev/ttyACM1
```

Repeat for both leader and follower so you know each port.

## 4) Set motor IDs and baudrates

You must set IDs once per motor (EEPROM). Follow the on-screen prompts; connect
only one motor at a time to the controller board.

Follower:

```bash
lerobot-setup-motors \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodemXXXX
```

Leader:

```bash
lerobot-setup-motors \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodemYYYY
```

## 5) Calibrate leader and follower

Calibration sets the joint middle positions and range. Use consistent `id`
values across teleop/record/eval so the same calibration file is reused.

Follower:

```bash
lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodemXXXX \
  --robot.id=my_awesome_follower_arm
```

Leader:

```bash
lerobot-calibrate \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodemYYYY \
  --teleop.id=my_awesome_leader_arm
```

## 6) Teleoperate (leader -> follower)

Command:

```bash
lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodemXXXX \
  --robot.id=my_awesome_follower_arm \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodemYYYY \
  --teleop.id=my_awesome_leader_arm
```

The teleoperate command will prompt for calibration if needed.

## 7) Record a dataset

Login to the Hugging Face Hub:

```bash
huggingface-cli login --token ${HUGGINGFACE_TOKEN} --add-to-git-credential
HF_USER=$(hf auth whoami | head -n 1)
```

Record example (adapt ports, IDs, cameras, and task text):

```bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodemXXXX \
  --robot.id=my_awesome_follower_arm \
  --robot.cameras="{ front: {type: opencv, index_or_path: 0, width: 1920, height: 1080, fps: 30}}" \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodemYYYY \
  --teleop.id=my_awesome_leader_arm \
  --display_data=true \
  --dataset.repo_id=${HF_USER}/so101_recording \
  --dataset.num_episodes=5 \
  --dataset.single_task="Grab the black cube"
```

Notes:
- If you do not have cameras, remove `--robot.cameras` and set `--display_data=false`.
- Datasets are stored in `~/.cache/huggingface/lerobot/{repo-id}` and can be
  pushed to the Hub automatically.

## 8) Train a policy (example)

```bash
lerobot-train \
  --dataset.repo_id=${HF_USER}/so101_test \
  --policy.type=act \
  --output_dir=outputs/train/act_so101_test \
  --job_name=act_so101_test \
  --policy.device=cuda \
  --wandb.enable=true \
  --policy.repo_id=${HF_USER}/my_policy
```

See `docs/source/il_robots.mdx` for more training and resume details.

## 9) Run inference / evaluation (example)

Use `lerobot-record` with a policy path; adapt from the `il_robots` example:

```bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodemXXXX \
  --robot.id=my_awesome_follower_arm \
  --display_data=false \
  --dataset.repo_id=${HF_USER}/eval_so101 \
  --dataset.single_task="Put the cube into the box" \
  --policy.path=${HF_USER}/my_policy
```

If you want to teleoperate between episodes, add the leader config flags.

## 10) Phone teleop + URDF note

If you use the phone-teleop examples, copy the SO101 URDF from the SO-ARM100
repo. The docs recommend:
https://github.com/TheRobotStudio/SO-ARM100/blob/main/Simulation/SO101/so101_new_calib.urdf

See `docs/source/phone_teleop.mdx` for the exact tutorial and file placement.

## 11) Useful code locations

- Follower robot implementation: `src/lerobot/robots/so_follower/so_follower.py`
- Follower config: `src/lerobot/robots/so_follower/config_so_follower.py`
- Leader teleop implementation: `src/lerobot/teleoperators/so_leader/so_leader.py`
- Leader config: `src/lerobot/teleoperators/so_leader/config_so_leader.py`
- CLI entrypoints: `src/lerobot/scripts/`
