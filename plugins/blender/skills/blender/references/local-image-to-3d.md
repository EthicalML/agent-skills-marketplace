# Local image-to-3D on Apple Silicon

1. Use this route when local generation fits the machine and task. The tested runtime is [mlx-spatial](https://github.com/appautomaton/mlx-spatial), revision `d2cc98ef7fb2166dc7e3b826b487e80f6f5027dc`, with [TRELLIS.2 MLX 8-bit weights](https://huggingface.co/appautomaton/trellis2-mlx-8bit). It produced real shape meshes on an M1 Max with 32 GB memory. This is an experimental reconstruction backend, not a guarantee of likeness or production topology. Recheck upstream requirements when changing revisions.

2. Clone the runtime outside the skill directory, check out the tested revision, and run `uv sync` there. Reserve roughly 11 GB for the selected checkpoint files plus room for the environment, intermediate meshes, and Blender copies. Read the model card and each component's license; a repository license does not cover every bundled checkpoint. Download weights into the runtime's `weights/trellis2-mlx-8bit` directory using its environment:

```python
from huggingface_hub import snapshot_download
snapshot_download(
    "appautomaton/trellis2-mlx-8bit",
    revision="a1cc385eb197f9536615ec3aa6bc8f137cecb365",
    local_dir="weights/trellis2-mlx-8bit",
    ignore_patterns=["rmbg/*", "ckpts/tex_enc*"],
    max_workers=4,
)
```

Set `HF_HUB_DISABLE_XET=1` before starting the process if the default transfer stalls. The exclusions assume preprocessed RGBA input and shape-only generation. Keep license files. The runtime's readiness manifest also expects some checkpoints unused by shape generation; do not delete arbitrary files to trim the download. Run `uv run mlx-spatial-trellis2 --root weights/trellis2-mlx-8bit validate` and require `ready=True`.

3. Supply an inspected RGBA foreground image; this bypasses the bundled RMBG model. `rembg` with its `u2net` session is one tested preprocessing option; install it in a suitable separate environment if needed and inspect the saved alpha. Run from the runtime directory, replacing the input and output paths:

```sh
uv run python scripts/trellis2/generate_shape.py /absolute/reference-rgba.png --root weights/trellis2-mlx-8bit --dino-root weights/trellis2-mlx-8bit/dinov3 --output-dir /absolute/project/candidates/first --pipeline-type 512 --seed 42
```

Keep the model-config sampler defaults; a one-step smoke test is not a quality run. Save stdout/stderr and `trace.json`. Require an actual `model.obj`, successful exit, no trace blocker, and completed mesh export. The original script prints little during inference. On the tested machine one 512 run took about four minutes; time varies with the image and hardware. Run GPU-heavy generation and Blender renders sequentially.

4. Follow the neutral multi-angle review and mesh checks in [reconstruction.md](reconstruction.md). In the tested runtime, exported meshes had extensive inconsistent face winding; recalculating normals on a copy removed most striped shading but left genuine topology defects. Do not mistake that repair for retopology or a recovered hidden surface. If the candidate is promising, test `--pipeline-type 1024_cascade` as a separate candidate and compare before selecting it. If a token or memory guard blocks the run, record the exact stage and inspect memory requirements before increasing limits; do not retry indefinitely.
