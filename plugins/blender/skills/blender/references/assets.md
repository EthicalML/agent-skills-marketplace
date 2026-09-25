# External assets and generation

1. Choose a source based on the brief: Poly Haven for HDRIs/materials and scanned props, Sketchfab for specific models, Poly Pizza for low-poly assets, or procedural construction for precise/custom geometry. Read the relevant command entry from commands.json rather than guessing parameters. `B.call` returns raw add-on results; MCP-side formatting and image decoding are not included.

2. Check `B.call('get_polyhaven_status')`, `get_sketchfab_status`, `get_polypizza_status`, `get_hyper3d_status`, or `get_hunyuan3d_status` for the chosen source. Integrations are enabled per scene. For a requested free Poly Haven workflow, enable `bpy.context.scene.blendermcp_use_polyhaven = True` through execute if necessary. For other services, use the add-on preferences and configured credentials; never print keys or put them in build scripts. Paid generation needs authorization for that service/use.

3. Search before downloading. Example:

```python
assets = B.call("search_polyhaven_assets", asset_type="hdris", query="studio", limit=5)
# Inspect the returned candidates and choose an actual returned ID.
preview = B.call("get_polyhaven_asset_preview", asset_id=chosen_id)
# Read the response fields; decode returned base64 image data to project/tmp and open it.
asset = B.call(
    "download_polyhaven_asset",
    asset_id=chosen_id,
    asset_type="hdris",
    resolution="1k",
    timeout=180,
)
```

4. For Sketchfab use search_sketchfab_models, get_sketchfab_model_preview, download_sketchfab_model. For Poly Pizza use search_polypizza_models and download_polypizza_model; preserve CC-BY attribution returned by the service and saved on imported objects. Normalize scale from measured bounds and the requested real-world dimensions; don't assume downloaded models use matching units. Check orientation, origin, texture paths, and collection membership. Service handlers may block the live GUI during downloads; keep candidates/resolutions small while iterating and do not submit overlapping mutations.

5. Hyper3D's MCP generation tools map to the add-on command create_rodin_job, followed by poll_rodin_job_status and import_generated_asset. Hunyuan uses create_hunyuan_job, poll_hunyuan_job_status, import_generated_asset_hunyuan. Their accepted parameters depend on the configured service mode; consult the mode variants in commands.json. Preserve job IDs, poll until terminal, and import only successful results. A connection timeout does not mean generation failed; recover by job ID rather than paying for a duplicate request. These external APIs need separate live verification with the user's credentials before claiming support was tested.

6. Record asset source, identifier, license, and any attribution beside the deliverable. After importing, inspect object/material data and a rendered preview. Pack downloaded textures where appropriate and validate the saved deliverable. Missing credentials or a failed service is a reason to use another suitable source or procedural construction, not to invent a successful download.
