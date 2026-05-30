from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image
from core.cv_pipeline import process_tryon

app = FastAPI(title="AI Jewellery Try-On API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, you could restrict to your Vercel domain e.g. ["https://your-app.vercel.app"]
    allow_credentials=False, # Must be False if allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/try-on")
async def try_on_endpoint(
    image: UploadFile = File(...),
    earring_id: str = Form(...)
):
    try:
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # We process the image using cv_pipeline
        result = process_tryon(pil_image, earring_id)
        
        return {"success": True, "results": result["variations"], "face_shape": result["face_shape"]}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
